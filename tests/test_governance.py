from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from scripts._common import (
    ConsistencyError,
    OutputError,
    SchemaError,
    atomic_write_many,
    canonical_json_bytes,
    load_and_validate,
    load_project,
    validate_consistency,
)
from scripts.research_checklist import sync_checklist
from scripts.research_checklist import main as checklist_main
from scripts.research_export import main as export_main
from scripts.research_export import render_export
from scripts.research_resolve import apply_decisions


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "synthetic-study"
SCHEMAS = ROOT / "shared" / "schemas"


class GovernanceTests(unittest.TestCase):
    def load_documents(self):
        return load_project(FIXTURE, SCHEMAS)

    def test_valid_synthetic_project(self) -> None:
        documents = self.load_documents()
        self.assertEqual("SRC-SYN-001", documents["source_catalog"]["sources"][0]["source_id"])

    def test_formal_source_free_claim_is_rejected(self) -> None:
        documents = self.load_documents()
        documents["research_evidence"]["evidence"][0]["source_refs"] = []
        errors = validate_consistency(documents)
        self.assertTrue(any("source-free evidence" in error for error in errors))

    def test_duplicate_stable_id_is_rejected(self) -> None:
        documents = self.load_documents()
        duplicate = deepcopy(documents["source_catalog"]["sources"][0])
        documents["source_catalog"]["sources"].append(duplicate)
        self.assertTrue(any("duplicate source ID" in error for error in validate_consistency(documents)))

    def test_conflicting_source_versions_are_preserved(self) -> None:
        documents = self.load_documents()
        second = deepcopy(documents["source_catalog"]["sources"][0])
        second["source_id"] = "SRC-SYN-002"
        second["version"] = "v2-conflict"
        second["sha256"] = "c" * 64
        second["conflict_group"] = "CG-SYN-001"
        documents["source_catalog"]["sources"][0]["conflict_group"] = "CG-SYN-001"
        documents["source_catalog"]["sources"].append(second)
        self.assertEqual([], validate_consistency(documents))
        self.assertEqual(2, len(documents["source_catalog"]["sources"]))

    def test_schema_failure_is_distinct_from_consistency_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            invalid = Path(temp) / "source-catalog.json"
            invalid.write_text('{"schema_version":"1.0.0","sources":[{}]}\n', encoding="utf-8")
            with self.assertRaises(SchemaError):
                load_and_validate(invalid, SCHEMAS / "source-catalog.schema.json")

    def test_finding_sync_is_idempotent_and_does_not_mutate_core(self) -> None:
        documents = self.load_documents()
        source_before = deepcopy(documents["source_catalog"])
        evidence_before = deepcopy(documents["research_evidence"])
        first = sync_checklist(documents["findings"], documents["source_catalog"])
        second = sync_checklist(documents["findings"], documents["source_catalog"], first)
        self.assertEqual(first, second)
        self.assertEqual(source_before, documents["source_catalog"])
        self.assertEqual(evidence_before, documents["research_evidence"])

    def test_source_hash_change_reopens_closed_item_and_preserves_history(self) -> None:
        documents = self.load_documents()
        existing = deepcopy(documents["checklist"])
        existing["items"][0]["status"] = "closed"
        existing["items"][0]["history"].append(
            {"at": "2026-08-03", "event": "close", "reason": "reviewed"}
        )
        original_fingerprint = existing["items"][0]["fingerprint"]
        catalog = deepcopy(documents["source_catalog"])
        catalog["sources"][0]["sha256"] = "c" * 64
        updated = sync_checklist(documents["findings"], catalog, existing)
        item = updated["items"][0]
        self.assertEqual(original_fingerprint, item["fingerprint"])
        self.assertEqual("open", item["status"])
        self.assertEqual("reopened", item["history"][-1]["event"])

    def test_decision_updates_only_explicit_fingerprint(self) -> None:
        documents = self.load_documents()
        pending = {
            "schema_version": "1.0.0",
            "decisions": [
                {
                    "decision_id": "D-SYN-001",
                    "fingerprint": documents["checklist"]["items"][0]["fingerprint"],
                    "action": "close",
                    "reviewer": "Synthetic Reviewer",
                    "reviewed_at": "2026-08-03",
                    "reason": "The bounded wording was confirmed."
                }
            ],
        }
        checklist, decision_log = apply_decisions(documents["checklist"], pending, documents["decision_log"])
        self.assertEqual("closed", checklist["items"][0]["status"])
        self.assertEqual(["D-SYN-001"], [item["decision_id"] for item in decision_log["decisions"]])

    def test_incomplete_waiver_is_rejected(self) -> None:
        documents = self.load_documents()
        pending = {
            "schema_version": "1.0.0",
            "decisions": [
                {
                    "decision_id": "D-SYN-002",
                    "fingerprint": documents["checklist"]["items"][0]["fingerprint"],
                    "action": "waive",
                    "reviewer": "Synthetic Reviewer",
                    "reviewed_at": "2026-08-03",
                    "reason": "Synthetic waiver without approval."
                }
            ],
        }
        with self.assertRaisesRegex(ConsistencyError, "approver"):
            apply_decisions(documents["checklist"], pending, documents["decision_log"])

    def test_atomic_multi_file_failure_rolls_back(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.json"
            second = Path(temp) / "second.json"
            first.write_bytes(b"first-old")
            second.write_bytes(b"second-old")
            calls = 0

            def fail_second(source: str, target: str) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("synthetic replacement failure")
                os.replace(source, target)

            with self.assertRaises(OutputError):
                atomic_write_many({first: b"first-new", second: b"second-new"}, replace_func=fail_second)
            self.assertEqual(b"first-old", first.read_bytes())
            self.assertEqual(b"second-old", second.read_bytes())

    def test_export_gate_and_force_warning(self) -> None:
        documents = self.load_documents()
        artifact, report, blocked = render_export(documents, FIXTURE, force=False)
        self.assertTrue(blocked)
        self.assertEqual(b"", artifact)
        forced_artifact, forced_report, forced_blocked = render_export(documents, FIXTURE, force=True)
        self.assertFalse(forced_blocked)
        self.assertIn("FORCED WARNING", forced_artifact.decode("utf-8"))
        self.assertEqual(["CL-SYN-001"], forced_report["included_claim_ids"])

    def test_force_does_not_include_ineligible_claims(self) -> None:
        documents = self.load_documents()
        documents["research_evidence"]["claims"].append(
            {
                "claim_id": "CL-SYN-DRAFT",
                "text": "A draft claim that must stay excluded.",
                "claim_type": "transfer",
                "evidence_ids": [],
                "scope": "Synthetic fixture only.",
                "limitations": "Not reviewed.",
                "status": "draft",
                "active": True,
                "researcher_decision": "pending",
            }
        )
        artifact, report, blocked = render_export(documents, FIXTURE, force=True)
        self.assertFalse(blocked)
        self.assertNotIn("CL-SYN-DRAFT", artifact.decode("utf-8"))
        self.assertIn("CL-SYN-DRAFT", report["excluded_claim_ids"])

    def test_dry_run_leaves_no_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            checklist_output = Path(temp) / "checklist.json"
            result = checklist_main(
                [
                    "--findings", str(FIXTURE / "findings.json"),
                    "--source-catalog", str(FIXTURE / "source-catalog.json"),
                    "--checklist", str(checklist_output),
                    "--schema-dir", str(SCHEMAS),
                    "--dry-run",
                ]
            )
            self.assertEqual(0, result)
            self.assertFalse(checklist_output.exists())

            export_output = Path(temp) / "claims.md"
            result = export_main(
                [
                    "--project-dir", str(FIXTURE),
                    "--output", str(export_output),
                    "--schema-dir", str(SCHEMAS),
                    "--dry-run",
                    "--force",
                ]
            )
            self.assertEqual(0, result)
            self.assertFalse(export_output.exists())
            self.assertFalse(Path(str(export_output) + ".report.json").exists())


if __name__ == "__main__":
    unittest.main()
