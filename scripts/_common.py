"""Shared deterministic governance helpers for public research CLIs."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple


class ExitCode(IntEnum):
    OK = 0
    USAGE = 2
    INPUT = 3
    SCHEMA = 4
    CONSISTENCY = 5
    OUTPUT = 6
    REVIEW_REQUIRED = 8


class GovernanceError(Exception):
    """Base exception carrying the required public CLI exit code."""

    def __init__(self, message: str, exit_code: ExitCode) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class InputFileError(GovernanceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.INPUT)


class SchemaError(GovernanceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.SCHEMA)


class ConsistencyError(GovernanceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.CONSISTENCY)


class OutputError(GovernanceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.OUTPUT)


SCHEMA_FILES: Mapping[str, str] = {
    "source_catalog": "source-catalog.schema.json",
    "research_evidence": "research-evidence.schema.json",
    "corpus_snapshot": "corpus-snapshot.schema.json",
    "findings": "findings.schema.json",
    "checklist": "checklist.schema.json",
    "decision_log": "decision-log.schema.json",
}

PROJECT_FILES: Mapping[str, str] = {
    "source_catalog": "source-catalog.json",
    "research_evidence": "research-evidence.json",
    "corpus_snapshot": "corpus-snapshot.json",
    "findings": "findings.json",
    "checklist": "checklist.json",
    "decision_log": "decision-log.json",
}


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    try:
        return sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise InputFileError(f"cannot read {path}: {exc}") from exc


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputFileError(f"missing input file: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputFileError(f"invalid JSON input {path}: {exc}") from exc


def stable_fingerprint(*parts: Any) -> str:
    payload = canonical_json_bytes(parts)
    return f"FP-{sha256_bytes(payload)[:24].upper()}"


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def validate_schema(value: Any, schema: Mapping[str, Any], location: str = "$") -> List[str]:
    """Validate the intentionally small JSON Schema subset used by this toolkit."""

    errors: List[str] = []
    expected = schema.get("type")
    if isinstance(expected, list):
        if not any(_matches_type(value, candidate) for candidate in expected):
            return [f"{location}: expected one of {expected}"]
    elif isinstance(expected, str) and not _matches_type(value, expected):
        return [f"{location}: expected {expected}"]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: value is not in enum {schema['enum']}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{location}: string is shorter than {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{location}: string is longer than {schema['maxLength']}")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            errors.append(f"{location}: string does not match {schema['pattern']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{location}: array has fewer than {schema['minItems']} items")
        if schema.get("uniqueItems"):
            encoded = [canonical_json_bytes(item) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{location}: array items are not unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_schema(item, item_schema, f"{location}[{index}]"))
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{location}: missing required property {key}")
        properties = schema.get("properties", {})
        for key, child in value.items():
            if key in properties:
                errors.extend(validate_schema(child, properties[key], f"{location}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{location}: unexpected property {key}")
    return errors


def load_and_validate(path: Path, schema_path: Path) -> Any:
    value = read_json(path)
    schema = read_json(schema_path)
    errors = validate_schema(value, schema)
    if errors:
        raise SchemaError(f"{path}: " + "; ".join(errors))
    return value


def _unique_ids(items: Iterable[Mapping[str, Any]], key: str, label: str) -> Tuple[set[str], List[str]]:
    values: set[str] = set()
    errors: List[str] = []
    for item in items:
        value = item.get(key)
        if value in values:
            errors.append(f"duplicate {label}: {value}")
        elif isinstance(value, str):
            values.add(value)
    return values, errors


def validate_consistency(documents: Mapping[str, Any]) -> List[str]:
    """Validate cross-file references and formal-output governance gates."""

    errors: List[str] = []
    catalog = documents.get("source_catalog", {"sources": []})
    evidence_doc = documents.get("research_evidence", {"evidence": [], "claims": []})
    source_ids, source_errors = _unique_ids(catalog.get("sources", []), "source_id", "source ID")
    evidence_ids, evidence_errors = _unique_ids(evidence_doc.get("evidence", []), "evidence_id", "evidence ID")
    claim_ids, claim_errors = _unique_ids(evidence_doc.get("claims", []), "claim_id", "claim ID")
    errors.extend(source_errors + evidence_errors + claim_errors)

    evidence_by_id = {item["evidence_id"]: item for item in evidence_doc.get("evidence", []) if "evidence_id" in item}
    for item in evidence_doc.get("evidence", []):
        for ref in item.get("source_refs", []):
            if ref.get("source_id") not in source_ids:
                errors.append(f"evidence {item.get('evidence_id')} references missing source {ref.get('source_id')}")

    for claim in evidence_doc.get("claims", []):
        formal = claim.get("status") in {"reviewed", "confirmed"} and claim.get("active") is True
        linked = claim.get("evidence_ids", [])
        if formal and not linked:
            errors.append(f"formal claim {claim.get('claim_id')} has no evidence")
        for evidence_id in linked:
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                errors.append(f"claim {claim.get('claim_id')} references missing evidence {evidence_id}")
                continue
            if formal and not evidence.get("source_refs"):
                errors.append(f"formal claim {claim.get('claim_id')} uses source-free evidence {evidence_id}")
            if formal and evidence.get("status") != "reviewed":
                errors.append(f"formal claim {claim.get('claim_id')} uses unreviewed evidence {evidence_id}")
            if formal and evidence.get("classification") == "derived":
                derivation = evidence.get("derivation") or {}
                if derivation.get("reproducible") is not True:
                    errors.append(f"formal claim {claim.get('claim_id')} uses non-reproducible derived evidence {evidence_id}")

    snapshot = documents.get("corpus_snapshot", {})
    for source_id in snapshot.get("included_source_ids", []):
        if source_id not in source_ids:
            errors.append(f"snapshot references missing source {source_id}")

    findings = documents.get("findings", {}).get("findings", [])
    finding_ids, finding_errors = _unique_ids(findings, "finding_id", "finding ID")
    errors.extend(finding_errors)
    valid_targets = source_ids | evidence_ids | claim_ids
    for finding in findings:
        for target_id in finding.get("target_ids", []):
            if target_id not in valid_targets:
                errors.append(f"finding {finding.get('finding_id')} references missing target {target_id}")
        for source_id in finding.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"finding {finding.get('finding_id')} references missing source {source_id}")

    checklist = documents.get("checklist", {}).get("items", [])
    fingerprints, fingerprint_errors = _unique_ids(checklist, "fingerprint", "checklist fingerprint")
    errors.extend(fingerprint_errors)
    for item in checklist:
        if item.get("finding_id") not in finding_ids:
            errors.append(f"checklist {item.get('fingerprint')} references missing finding {item.get('finding_id')}")

    decisions = documents.get("decision_log", {}).get("decisions", [])
    _, decision_errors = _unique_ids(decisions, "decision_id", "decision ID")
    errors.extend(decision_errors)
    for decision in decisions:
        if decision.get("fingerprint") not in fingerprints:
            errors.append(f"decision {decision.get('decision_id')} references missing checklist fingerprint")
        if decision.get("action") == "waive":
            for field in ("approver", "approved_at"):
                if not decision.get(field):
                    errors.append(f"waiver {decision.get('decision_id')} lacks {field}")
    return errors


def load_project(project_dir: Path, schema_dir: Path, required: Sequence[str] = ("source_catalog", "research_evidence")) -> Dict[str, Any]:
    documents: Dict[str, Any] = {}
    for key, filename in PROJECT_FILES.items():
        path = project_dir / filename
        if not path.exists():
            if key in required:
                raise InputFileError(f"missing required project file: {path}")
            continue
        schema_path = schema_dir / SCHEMA_FILES[key]
        documents[key] = load_and_validate(path, schema_path)
    errors = validate_consistency(documents)
    if errors:
        raise ConsistencyError("; ".join(errors))
    return documents


def resolve_schema_dir(script_path: Path, provided: Optional[Path]) -> Path:
    if provided is not None:
        return provided.resolve()
    repository_candidate = script_path.resolve().parents[1] / "shared" / "schemas"
    packaged_candidate = script_path.resolve().parents[1] / "assets" / "schemas"
    for candidate in (repository_candidate, packaged_candidate):
        if candidate.is_dir():
            return candidate
    raise InputFileError("cannot locate schema directory; pass --schema-dir")


def atomic_write_many(
    outputs: Mapping[Path, bytes],
    *,
    replace_func: Callable[[str, str], None] = os.replace,
) -> None:
    """Replace several files and restore prior bytes when any replacement fails."""

    if not outputs:
        return
    originals: Dict[Path, Optional[bytes]] = {}
    temporary: Dict[Path, Path] = {}
    replaced: List[Path] = []
    try:
        for target, content in outputs.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            originals[target] = target.read_bytes() if target.exists() else None
            handle, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
            with os.fdopen(handle, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            temporary[target] = Path(temp_name)
        for target, temp_path in temporary.items():
            replace_func(str(temp_path), str(target))
            replaced.append(target)
    except OSError as exc:
        for target in reversed(replaced):
            original = originals[target]
            try:
                if original is None:
                    target.unlink(missing_ok=True)
                else:
                    target.write_bytes(original)
            except OSError:
                pass
        raise OutputError(f"atomic update failed and rollback was attempted: {exc}") from exc
    finally:
        for temp_path in temporary.values():
            temp_path.unlink(missing_ok=True)


def refuse_overwrite(paths: Iterable[Path], force: bool) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing and not force:
        raise OutputError("refusing to overwrite existing output: " + ", ".join(existing))


def print_error(exc: GovernanceError) -> int:
    import sys

    print(f"ERROR: {exc}", file=sys.stderr)
    return int(exc.exit_code)
