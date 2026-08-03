"""Export eligible claims with a deterministic audit sidecar."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

try:
    from ._common import (
        ExitCode,
        GovernanceError,
        PROJECT_FILES,
        atomic_write_many,
        canonical_json_bytes,
        load_project,
        print_error,
        refuse_overwrite,
        resolve_schema_dir,
        sha256_bytes,
        sha256_file,
    )
except ImportError:  # Direct script execution and packaged Skill layout.
    from _common import (
    ExitCode,
    GovernanceError,
    PROJECT_FILES,
    atomic_write_many,
    canonical_json_bytes,
    load_project,
    print_error,
    refuse_overwrite,
    resolve_schema_dir,
    sha256_bytes,
    sha256_file,
)


def render_export(documents: Mapping[str, Any], project_dir: Path, force: bool) -> Tuple[bytes, Dict[str, Any], bool]:
    evidence_doc = documents["research_evidence"]
    checklist = documents.get("checklist", {}).get("items", [])
    unresolved_high = [item["fingerprint"] for item in checklist if item.get("priority") == "high" and item.get("status") != "closed"]
    warnings: List[str] = []
    if unresolved_high:
        if not force:
            return b"", {"unresolved_high": unresolved_high}, True
        warnings.append("FORCED WARNING: unresolved high-priority review items remain; no ineligible claims were included.")

    included: List[Mapping[str, Any]] = []
    excluded: List[str] = []
    for claim in evidence_doc.get("claims", []):
        if claim.get("active") is True and claim.get("status") in {"reviewed", "confirmed"}:
            included.append(claim)
        else:
            excluded.append(claim["claim_id"])

    lines = ["# Governed Research Export", ""]
    if warnings:
        lines.extend([f"> {warning}" for warning in warnings] + [""])
    for claim in sorted(included, key=lambda item: item["claim_id"]):
        lines.extend(
            [
                f"## {claim['claim_id']}",
                "",
                claim["text"],
                "",
                f"- Type: `{claim['claim_type']}`",
                f"- Evidence: {', '.join(claim['evidence_ids'])}",
                f"- Scope: {claim['scope']}",
                f"- Limitations: {claim['limitations']}",
                "",
            ]
        )
    artifact = "\n".join(lines).encode("utf-8")
    input_hashes = {
        filename: sha256_file(project_dir / filename)
        for key, filename in sorted(PROJECT_FILES.items())
        if key in documents
    }
    report = {
        "schema_version": "1.0.0",
        "input_hashes": input_hashes,
        "included_claim_ids": [item["claim_id"] for item in sorted(included, key=lambda item: item["claim_id"])],
        "excluded_claim_ids": sorted(excluded),
        "warnings": warnings,
        "limitations": ["Local governed export; not peer review, ethics approval, public release, or proof of effectiveness."],
        "artifact_sha256": sha256_bytes(artifact),
    }
    return artifact, report, False


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Export reviewed source-grounded claims with an audit sidecar.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--schema-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Allow overwrite and emit a warning artifact when high review items remain.")
    args = parser.parse_args(argv)
    sidecar = args.output.with_name(args.output.name + ".report.json")
    try:
        schema_dir = resolve_schema_dir(Path(__file__), args.schema_dir)
        project_dir = args.project_dir.resolve()
        documents = load_project(
            project_dir,
            schema_dir,
            required=("source_catalog", "research_evidence", "findings", "checklist"),
        )
        artifact, report, blocked = render_export(documents, project_dir, args.force)
        if blocked:
            print("ERROR: unresolved high-priority checklist items block export", file=sys.stderr)
            return int(ExitCode.REVIEW_REQUIRED)
        if args.dry_run:
            print(f"Dry run: {len(report['included_claim_ids'])} claim(s) eligible; no files written.")
            return 0
        refuse_overwrite([args.output, sidecar], args.force)
        atomic_write_many({args.output: artifact, sidecar: canonical_json_bytes(report)})
    except GovernanceError as exc:
        return print_error(exc)
    print(f"Created {args.output}")
    print(f"Created {sidecar}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
