"""Apply explicit human decisions to checklist items and an append-only log."""

from __future__ import annotations

import argparse
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

try:
    from ._common import (
        ConsistencyError,
        GovernanceError,
        SCHEMA_FILES,
        atomic_write_many,
        canonical_json_bytes,
        load_and_validate,
        print_error,
        refuse_overwrite,
        resolve_schema_dir,
    )
except ImportError:  # Direct script execution and packaged Skill layout.
    from _common import (
    ConsistencyError,
    GovernanceError,
    SCHEMA_FILES,
    atomic_write_many,
    canonical_json_bytes,
    load_and_validate,
    print_error,
    refuse_overwrite,
    resolve_schema_dir,
)


def apply_decisions(
    checklist_doc: Mapping[str, Any],
    pending_doc: Mapping[str, Any],
    decision_log_doc: Optional[Mapping[str, Any]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    checklist = deepcopy(checklist_doc)
    decision_log = deepcopy(decision_log_doc or {"schema_version": "1.0.0", "decisions": []})
    items = {item["fingerprint"]: item for item in checklist.get("items", [])}
    known_decisions = {item["decision_id"] for item in decision_log.get("decisions", [])}
    pending = pending_doc.get("decisions", [])
    if not pending:
        raise ConsistencyError("decision input is empty")

    for decision in pending:
        decision_id = decision.get("decision_id")
        fingerprint = decision.get("fingerprint")
        action = decision.get("action")
        if decision_id in known_decisions:
            raise ConsistencyError(f"duplicate decision ID: {decision_id}")
        if fingerprint not in items:
            raise ConsistencyError(f"decision targets unknown fingerprint: {fingerprint}")
        for field in ("reviewer", "reviewed_at", "reason"):
            if not decision.get(field):
                raise ConsistencyError(f"decision {decision_id} lacks {field}")
        if action == "waive":
            for field in ("approver", "approved_at"):
                if not decision.get(field):
                    raise ConsistencyError(f"waiver {decision_id} lacks {field}")
        if action not in {"close", "reopen", "waive"}:
            raise ConsistencyError(f"unsupported decision action: {action}")

        item = items[fingerprint]
        item["status"] = "open" if action == "reopen" else "closed"
        item["resolution"] = {
            "decision_id": decision_id,
            "action": action,
            "reviewer": decision["reviewer"],
            "reviewed_at": decision["reviewed_at"],
        }
        item.setdefault("history", []).append(
            {"at": decision["reviewed_at"], "event": action, "reason": decision["reason"]}
        )
        decision_log.setdefault("decisions", []).append(deepcopy(decision))
        known_decisions.add(decision_id)

    decision_log["decisions"] = sorted(decision_log["decisions"], key=lambda item: item["decision_id"])
    checklist["items"] = sorted(items.values(), key=lambda item: item["fingerprint"])
    return checklist, decision_log


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Apply explicit human checklist decisions atomically.")
    parser.add_argument("--checklist", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--decision-log", type=Path, required=True)
    parser.add_argument("--schema-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Allow replacement of governed state files.")
    args = parser.parse_args(argv)
    try:
        schema_dir = resolve_schema_dir(Path(__file__), args.schema_dir)
        checklist = load_and_validate(args.checklist, schema_dir / SCHEMA_FILES["checklist"])
        pending = load_and_validate(args.decisions, schema_dir / SCHEMA_FILES["decision_log"])
        decision_log = None
        if args.decision_log.exists():
            decision_log = load_and_validate(args.decision_log, schema_dir / SCHEMA_FILES["decision_log"])
        updated_checklist, updated_log = apply_decisions(checklist, pending, decision_log)
        if args.dry_run:
            print(f"Dry run: {len(pending['decisions'])} decision(s); no files written.")
            return 0
        refuse_overwrite([args.checklist, args.decision_log], args.force)
        atomic_write_many(
            {
                args.checklist: canonical_json_bytes(updated_checklist),
                args.decision_log: canonical_json_bytes(updated_log),
            }
        )
    except GovernanceError as exc:
        return print_error(exc)
    print(f"Applied {len(pending['decisions'])} decision(s) atomically.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
