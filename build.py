"""Build reproducible, self-contained Agent Skill distribution artifacts."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parent
SOURCE_SKILL_ROOT = Path("skills")
FIXED_ZIP_TIME = (2020, 1, 1, 0, 0, 0)
SEMVER = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
SKILL_NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*$")

SKILL_NAMES: Tuple[str, ...] = (
    "evidence-extract",
    "literature-discovery",
    "methodology-review",
    "research-export",
    "research-planning",
    "research-risk-watch",
    "research-synthesis",
    "research-writing",
    "research-writing-workbench",
)

SCRIPT_MAP: Mapping[str, Tuple[str, ...]] = {
    "evidence-extract": ("_common.py", "research_validate.py"),
    "literature-discovery": ("_common.py", "research_validate.py"),
    "methodology-review": ("_common.py", "research_validate.py", "research_checklist.py", "research_resolve.py"),
    "research-export": ("_common.py", "research_validate.py", "research_export.py"),
    "research-planning": (),
    "research-risk-watch": ("_common.py", "research_validate.py", "research_checklist.py", "research_resolve.py"),
    "research-synthesis": ("_common.py", "research_validate.py"),
    "research-writing": ("_common.py", "research_validate.py"),
    "research-writing-workbench": (
        "_common.py",
        "research_validate.py",
        "research_checklist.py",
        "research_resolve.py",
        "research_export.py",
    ),
}

SCHEMA_MAP: Mapping[str, Tuple[str, ...]] = {
    "evidence-extract": ("source-catalog.schema.json", "research-evidence.schema.json"),
    "literature-discovery": ("source-catalog.schema.json", "corpus-snapshot.schema.json"),
    "methodology-review": (
        "source-catalog.schema.json",
        "research-evidence.schema.json",
        "corpus-snapshot.schema.json",
        "findings.schema.json",
        "checklist.schema.json",
        "decision-log.schema.json",
    ),
    "research-export": (
        "source-catalog.schema.json",
        "research-evidence.schema.json",
        "corpus-snapshot.schema.json",
        "findings.schema.json",
        "checklist.schema.json",
        "decision-log.schema.json",
    ),
    "research-planning": (),
    "research-risk-watch": (
        "source-catalog.schema.json",
        "research-evidence.schema.json",
        "corpus-snapshot.schema.json",
        "findings.schema.json",
        "checklist.schema.json",
        "decision-log.schema.json",
    ),
    "research-synthesis": ("source-catalog.schema.json", "research-evidence.schema.json", "findings.schema.json"),
    "research-writing": ("source-catalog.schema.json", "research-evidence.schema.json"),
    "research-writing-workbench": (
        "source-catalog.schema.json",
        "research-evidence.schema.json",
        "corpus-snapshot.schema.json",
        "findings.schema.json",
        "checklist.schema.json",
        "decision-log.schema.json",
    ),
}

REFERENCE_GROUPS: Mapping[str, Tuple[str, ...]] = {
    "evidence-extract": ("prompt-template.md",),
    "literature-discovery": ("prompt-template.md",),
    "methodology-review": ("prompt-template.md",),
    "research-export": ("prompt-template.md",),
    "research-planning": ("prompt-template.md",),
    "research-risk-watch": ("prompt-template.md",),
    "research-synthesis": ("prompt-template.md",),
    "research-writing": ("prompt-template.md",),
    "research-writing-workbench": (
        "01-domain-and-ctcc.md",
        "02-contract-and-comparison.md",
        "03-trace-and-evidence.md",
        "04-counterexamples.md",
        "05-bounded-writing.md",
        "06-ai-audit-and-release.md",
        "prompt-template.md",
    ),
}

ASSET_MAP: Mapping[str, Tuple[str, ...]] = {
    name: () for name in SKILL_NAMES
}
ASSET_MAP = {
    **ASSET_MAP,
    "research-writing-workbench": (
        "templates/ai-use-record.md",
        "templates/bounded-claim-record.md",
        "templates/counterexample-review.md",
        "templates/engineering-question-brief.md",
        "templates/execution-record.md",
        "templates/release-check.md",
        "templates/scenario-matrix.md",
        "templates/trace-index.md",
        "templates/validation-contract.md",
    ),
}

DISTRIBUTION_FILE_MAP: Mapping[str, str] = {
    "README.md": "toolkit/README.md",
    "INSTALL.md": "docs/INSTALL.md",
    "VERSION": "VERSION",
}


class BuildError(Exception):
    pass


def run_available_official_validator(root: Path) -> Tuple[bool, str]:
    candidates: List[Path] = []
    configured = os.environ.get("RWW_SKILL_VALIDATOR")
    if configured:
        candidates.append(Path(configured))
    candidates.append(Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py")
    validator = next((path.resolve() for path in candidates if path.is_file()), None)
    if validator is None:
        return False, "official validator not found; built-in validation used"
    dependency = subprocess.run(
        [sys.executable, "-X", "utf8", "-c", "import yaml"],
        text=True,
        capture_output=True,
        check=False,
    )
    if dependency.returncode != 0:
        return False, "official validator found but PyYAML is unavailable; built-in validation used"
    for skill_name in SKILL_NAMES:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(validator), str(root / SOURCE_SKILL_ROOT / skill_name)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stdout.strip() or result.stderr.strip() or "unknown validator error"
            raise BuildError(f"official validator failed for {skill_name}: {detail}")
    return True, f"official validator passed for {len(SKILL_NAMES)} skill(s)"


def read_version(root: Path) -> str:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        raise BuildError(f"VERSION is not valid SemVer: {version!r}")
    return version


def parse_frontmatter(path: Path) -> Dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise BuildError(f"missing frontmatter: {path}")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise BuildError(f"unterminated frontmatter: {path}") from exc
    result: Dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            raise BuildError(f"invalid frontmatter line in {path}: {line}")
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def parse_openai_yaml(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s{2}(display_name|short_description|default_prompt):\s*\"(.*)\"\s*$", line)
        if match:
            values[match.group(1)] = match.group(2)
    return values


def markdown_links(path: Path) -> Iterable[str]:
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        yield match.group(1).split("#", 1)[0].strip()


def validate_links(skill_dir: Path) -> None:
    for markdown in sorted(skill_dir.rglob("*.md")):
        for target in markdown_links(markdown):
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            normalized = target.replace("%20", " ")
            parts = Path(normalized).parts
            if Path(normalized).is_absolute() or ".." in parts:
                raise BuildError(f"skill link must stay inside the skill without '..': {markdown}: {target}")
            resolved = (markdown.parent / normalized).resolve()
            try:
                resolved.relative_to(skill_dir.resolve())
            except ValueError as exc:
                raise BuildError(f"skill link escapes skill directory: {markdown}: {target}") from exc
            if not resolved.exists():
                raise BuildError(f"skill link target is missing: {markdown}: {target}")


def assert_no_symlinks(path: Path) -> None:
    for candidate in [path, *path.rglob("*")]:
        if candidate.is_symlink():
            raise BuildError(f"symlink is not allowed in build inputs: {candidate}")


def expected_source_files(skill_name: str) -> set[str]:
    files = {"SKILL.md", "agents/openai.yaml"}
    files.update(f"references/{name}" for name in REFERENCE_GROUPS[skill_name])
    files.update(f"assets/{name}" for name in ASSET_MAP[skill_name])
    return files


def validate_skill(root: Path, skill_name: str) -> None:
    if len(skill_name) > 64 or not SKILL_NAME_RE.fullmatch(skill_name):
        raise BuildError(f"invalid skill name: {skill_name}")
    skill_dir = root / SOURCE_SKILL_ROOT / skill_name
    if not skill_dir.is_dir():
        raise BuildError(f"missing skill directory: {skill_dir}")
    assert_no_symlinks(skill_dir)
    actual = {
        path.relative_to(skill_dir).as_posix()
        for path in skill_dir.rglob("*")
        if path.is_file()
    }
    expected = expected_source_files(skill_name)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise BuildError(f"skill whitelist mismatch for {skill_name}; missing={missing}, unexpected={unexpected}")

    skill_md = skill_dir / "SKILL.md"
    metadata = parse_frontmatter(skill_md)
    if set(metadata) != {"name", "description"}:
        raise BuildError(f"SKILL.md frontmatter must contain only name and description: {skill_name}")
    if metadata["name"] != skill_name or not metadata["description"].strip():
        raise BuildError(f"SKILL.md metadata does not match directory: {skill_name}")
    if len(skill_md.read_text(encoding="utf-8").splitlines()) >= 500:
        raise BuildError(f"SKILL.md has 500 or more lines: {skill_name}")
    yaml_values = parse_openai_yaml(skill_dir / "agents" / "openai.yaml")
    if set(yaml_values) != {"display_name", "short_description", "default_prompt"}:
        raise BuildError(f"agents/openai.yaml is incomplete: {skill_name}")
    if not 25 <= len(yaml_values["short_description"]) <= 64:
        raise BuildError(f"short_description must be 25-64 characters: {skill_name}")
    if f"${skill_name}" not in yaml_values["default_prompt"]:
        raise BuildError(f"default_prompt must mention ${skill_name}")
    validate_links(skill_dir)


def validate_private_imports(root: Path, skill_name: str) -> None:
    packaged = set(SCRIPT_MAP[skill_name])
    for script_name in packaged:
        tree = ast.parse((root / "scripts" / script_name).read_text(encoding="utf-8"), filename=script_name)
        for node in ast.walk(tree):
            module: Optional[str] = None
            if isinstance(node, ast.ImportFrom):
                module = node.module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("_") and not alias.name.startswith("__") and f"{alias.name}.py" not in packaged:
                        raise BuildError(f"{skill_name} misses private import {alias.name} required by {script_name}")
            if module and module.startswith("_") and not module.startswith("__") and f"{module.split('.')[0]}.py" not in packaged:
                raise BuildError(f"{skill_name} misses private import {module} required by {script_name}")


def copy_file(source: Path, target: Path) -> None:
    if source.is_symlink():
        raise BuildError(f"refusing symlinked build input: {source}")
    if not source.is_file():
        raise BuildError(f"missing whitelisted build input: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def assemble_skill(root: Path, skill_name: str, destination: Path, version: str) -> Path:
    validate_skill(root, skill_name)
    validate_private_imports(root, skill_name)
    source_dir = root / SOURCE_SKILL_ROOT / skill_name
    skill_dir = destination / skill_name
    for rel in sorted(expected_source_files(skill_name)):
        copy_file(source_dir / rel, skill_dir / rel)
    for script_name in SCRIPT_MAP[skill_name]:
        copy_file(root / "scripts" / script_name, skill_dir / "scripts" / script_name)
    for schema_name in SCHEMA_MAP[skill_name]:
        copy_file(root / "shared" / "schemas" / schema_name, skill_dir / "assets" / "schemas" / schema_name)
    (skill_dir / "VERSION").write_text(version + "\n", encoding="utf-8", newline="\n")
    return skill_dir


def write_zip(source_root: Path, archive_path: Path, top_level: Optional[str] = None) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    entries = sorted((path for path in source_root.rglob("*") if path.is_file()), key=lambda path: path.relative_to(source_root).as_posix())
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in entries:
            relative = path.relative_to(source_root).as_posix()
            arcname = f"{top_level}/{relative}" if top_level else relative
            info = zipfile.ZipInfo(arcname, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def verify_zip(path: Path, expected_top: Optional[str]) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if not names or names != sorted(names):
            raise BuildError(f"ZIP is empty or unsorted: {path}")
        if expected_top and any(not name.startswith(expected_top + "/") for name in names):
            raise BuildError(f"ZIP contains paths outside {expected_top}: {path}")
        if expected_top and f"{expected_top}/SKILL.md" not in names:
            raise BuildError(f"ZIP misses {expected_top}/SKILL.md: {path}")


def write_checksums(dist_dir: Path) -> None:
    lines: List[str] = []
    for path in sorted((item for item in dist_dir.rglob("*") if item.is_file() and item.name != "checksums.sha256"), key=lambda item: item.relative_to(dist_dir).as_posix()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(dist_dir).as_posix()}")
    (dist_dir / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def verify_checksums(dist_dir: Path) -> None:
    for line in (dist_dir / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        path = dist_dir / Path(rel)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise BuildError(f"checksum mismatch: {rel}")


def build_distribution(root: Path, dist_dir: Path) -> str:
    version = read_version(root)
    assert_no_symlinks(root / SOURCE_SKILL_ROOT)
    assert_no_symlinks(root / "shared")
    assembled = dist_dir / ".assembled"
    assembled.mkdir(parents=True)
    for skill_name in SKILL_NAMES:
        skill_dir = assemble_skill(root, skill_name, assembled, version)
        shutil.copytree(skill_dir, dist_dir / "agents-skills" / skill_name)
        archive_path = dist_dir / "claude" / f"{skill_name}-{version}.zip"
        write_zip(skill_dir, archive_path, skill_name)
        verify_zip(archive_path, skill_name)

    pack_root = dist_dir / ".pack"
    for output_name, source_name in DISTRIBUTION_FILE_MAP.items():
        copy_file(root / source_name, pack_root / output_name)
        copy_file(root / source_name, dist_dir / output_name)
    for skill_name in SKILL_NAMES:
        shutil.copytree(assembled / skill_name, pack_root / skill_name)
    pack_path = dist_dir / f"pack-{version}.zip"
    write_zip(pack_root, pack_path)
    verify_zip(pack_path, None)
    shutil.rmtree(assembled)
    shutil.rmtree(pack_root)
    write_checksums(dist_dir)
    verify_checksums(dist_dir)
    return version


def safe_replace_dist(root: Path, staged_dist: Path) -> Path:
    target = (root / "dist").resolve()
    if target.parent != root.resolve() or target.name != "dist":
        raise BuildError(f"unsafe dist target: {target}")
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(staged_dist), str(target))
    return target


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build reproducible Agent Skill distribution artifacts.")
    parser.add_argument("--check", action="store_true", help="Validate and assemble in a temporary directory without replacing dist/.")
    args = parser.parse_args(argv)
    try:
        _, validator_status = run_available_official_validator(ROOT)
        with tempfile.TemporaryDirectory(prefix="rww-build-") as temp:
            staged_dist = Path(temp) / "dist"
            staged_dist.mkdir()
            version = build_distribution(ROOT, staged_dist)
            if args.check:
                print(f"Build check passed for {len(SKILL_NAMES)} skill(s), version {version}.")
                print(f"Official external validator: {validator_status}.")
                return 0
            output = safe_replace_dist(ROOT, staged_dist)
        print(f"Built local release candidate: {output}")
        print(f"Official external validator: {validator_status}.")
        return 0
    except (BuildError, OSError, UnicodeError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 6


if __name__ == "__main__":
    sys.exit(main())
