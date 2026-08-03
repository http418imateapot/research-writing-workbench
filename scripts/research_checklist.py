"""Synchronize review findings into an idempotent governed checklist."""

from __future__ import annotations

import argparse
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

try:
    from ._common import (
        GovernanceError,
        SCHEMA_FILES,
        atomic_write_many,
        canonical_json_bytes,
        load_and_validate,
        print_error,
        refuse_overwrite,
        resolve_schema_dir,
        stable_fingerprint,
    )
except ImportError:  # Direct script execution and packaged Skill layout.
    from _common import (
    GovernanceError,
    SCHEMA_FILES,
    atomic_write_many,
    canonical_json_bytes,
    load_and_validate,
    print_error,
    refuse_overwrite,
    resolve_schema_dir,
    stable_fingerprint,
)


def sync_checklist(
    findings_doc: Mapping[str, Any],
    source_catalog: Mapping[str, Any],
    existing: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    current = deepcopy(existing or {"schema_version": "1.0.0", "items": []})
    existing_by_fingerprint = {item["fingerprint"]: item for item in current.get("items", [])}
    source_hashes = {item["source_id"]: item["sha256"] for item in source_catalog.get("sources", [])}
    generated_at = findings_doc.get("generated_at", "[待研究者裁定]")

    for finding in findings_doc.get("findings", []):
        if finding.get("requires_review") is not True:
            continue
        fingerprint = stable_fingerprint(
            finding.get("finding_id"),
            finding.get("method", {}).get("id"),
            finding.get("method", {}).get("version"),
            sorted(finding.get("target_ids", [])),
        )
        hashes = {source_id: source_hashes[source_id] for source_id in sorted(finding.get("source_ids", [])) if source_id in source_hashes}
        item = existing_by_fingerprint.get(fingerprint)
        if item is None:
            item = {
                "fingerprint": fingerprint,
                "finding_id": finding["finding_id"],
                "priority": finding["severity"],
                "status": "open",
                "affected_ids": sorted(finding.get("target_ids", [])),
                "source_hashes": hashes,
                "history": [{"at": generated_at, "event": "opened", "reason": "review required"}],
            }
            existing_by_fingerprint[fingerprint] = item
        elif item.get("source_hashes") != hashes:
            previous_status = item.get("status")
            item["source_hashes"] = hashes
            if previous_status == "closed":
                item["status"] = "open"
                item.setdefault("history", []).append(
                    {"at": generated_at, "event": "reopened", "reason": "source hash changed"}
                )
    current["items"] = sorted(existing_by_fingerprint.values(), key=lambda item: item["fingerprint"])
    return current


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize governed findings into a stable checklist.")
    parser.add_argument("--findings", type=Path, required=True)
    parser.add_argument("--source-catalog", type=Path, required=True)
    parser.add_argument("--checklist", type=Path, required=True)
    parser.add_argument("--schema-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Allow replacement of an existing checklist.")
    args = parser.parse_args(argv)
    try:
        schema_dir = resolve_schema_dir(Path(__file__), args.schema_dir)
        findings = load_and_validate(args.findings, schema_dir / SCHEMA_FILES["findings"])
        catalog = load_and_validate(args.source_catalog, schema_dir / SCHEMA_FILES["source_catalog"])
        existing = None
        if args.checklist.exists():
            existing = load_and_validate(args.checklist, schema_dir / SCHEMA_FILES["checklist"])
        updated = sync_checklist(findings, catalog, existing)
        content = canonical_json_bytes(updated)
        if args.dry_run:
            print(f"Dry run: {len(updated['items'])} checklist item(s); no files written.")
            return 0
        refuse_overwrite([args.checklist], args.force)
        atomic_write_many({args.checklist: content})
    except GovernanceError as exc:
        return print_error(exc)
    print(f"Wrote {args.checklist} with {len(updated['items'])} item(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
