"""Validate repository structure and text contracts without runtime dependencies."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build import BuildError, SKILL_NAMES, SOURCE_SKILL_ROOT, read_version, validate_skill


REQUIRED_FILES = [
    Path("README.md"), Path("README.zh-TW.md"), Path("README.en.md"),
    Path("AGENTS.md"), Path("ARCHITECTURE.md"), Path("VERSION"),
    Path("CITATION.cff"), Path("CHANGELOG.md"), Path("LICENSE"),
    Path("NOTICE"), Path("CONTRIBUTING.md"), Path("CODE_OF_CONDUCT.md"),
    Path("SECURITY.md"), Path("build.py"), Path("build.sh"), Path("build.bat"),
    Path("docs/DATA-CONTRACTS.md"), Path("docs/INSTALL.md"),
    Path("docs/USAGE.zh-TW.md"), Path("docs/MIGRATION-1.0.md"), Path("toolkit/README.md"),
    Path("prompts/commands.zh-TW.md"),
]
REQUIRED_DIRS = [
    Path("skills"), Path("shared/schemas"), Path("shared/prompts"),
    Path("shared/rules"), Path("shared/checklists"), Path("fixtures"),
    Path("docs"), Path("prompts"), Path("scripts"), Path("tests"),
]
REQUIRED_METHOD_MARKERS = [
    "契約—軌跡—反例—主張", "planned", "reproduced",
    "implementation", "withdraw", "[未取得產物]",
]
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".cff", ".txt", ""}
EXCLUDED_PARTS = {".git", ".work", ".venv", "dist", "reports", "exports", "__pycache__"}


def text_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name.startswith("."):
            yield path


def markdown_fences_balanced(text: str) -> bool:
    active = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if not match:
            continue
        marker = match.group(1)[0]
        if active is None:
            active = marker
        elif active == marker:
            active = None
    return active is None


def link_errors(root: Path, path: Path, text: str) -> List[str]:
    errors: List[str] = []
    for match in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        target = match.group(1).strip().split("#", 1)[0]
        if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
            continue
        target = target.replace("%20", " ")
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{path.relative_to(root)}: link escapes repository: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{path.relative_to(root)}: missing link target: {target}")
    return errors


def tracked_ignored_paths(root: Path) -> List[str]:
    if not (root / ".git").exists():
        return []
    result = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return ["unable to inspect tracked files with git ls-files"]
    bad: List[str] = []
    for name in result.stdout.splitlines():
        if any(part in {"dist", ".work", ".venv", "__pycache__"} for part in Path(name).parts):
            bad.append(f"ignored path is tracked: {name}")
    return bad


def validate_repository(root: Path) -> List[str]:
    root = root.resolve()
    errors: List[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel.as_posix()}")
    for rel in REQUIRED_DIRS:
        if not (root / rel).is_dir():
            errors.append(f"missing required directory: {rel.as_posix()}")

    actual_skills = tuple(sorted(path.parent.name for path in (root / SOURCE_SKILL_ROOT).glob("*/SKILL.md"))) if (root / SOURCE_SKILL_ROOT).exists() else ()
    if actual_skills != SKILL_NAMES:
        errors.append(f"skill source set mismatch: expected={SKILL_NAMES}, actual={actual_skills}")
    if (root / ".agents" / "skills").exists():
        errors.append("legacy .agents/skills source must not duplicate canonical skills/")
    for skill_name in SKILL_NAMES:
        try:
            validate_skill(root, skill_name)
        except (BuildError, OSError, UnicodeError) as exc:
            errors.append(str(exc))

    core_path = root / SOURCE_SKILL_ROOT / "research-writing-workbench" / "SKILL.md"
    if core_path.is_file():
        skill_text = core_path.read_text(encoding="utf-8")
        for marker in REQUIRED_METHOD_MARKERS:
            if marker not in skill_text:
                errors.append(f"core SKILL.md lacks CTCC method marker: {marker}")

    try:
        version = read_version(root)
    except (BuildError, OSError) as exc:
        errors.append(str(exc))
        version = ""
    citation = root / "CITATION.cff"
    if citation.is_file() and version:
        match = re.search(r'^version:\s*["\']?([^"\'\s]+)', citation.read_text(encoding="utf-8"), re.M)
        if not match or match.group(1) != version:
            errors.append("CITATION.cff version does not match VERSION")

    for path in text_files(root):
        try:
            data = path.read_bytes()
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"invalid UTF-8: {path.relative_to(root)}: {exc}")
            continue
        if path.suffix.lower() == ".md":
            if not markdown_fences_balanced(text):
                errors.append(f"unbalanced Markdown fence: {path.relative_to(root)}")
            if data and not data.endswith(b"\n"):
                errors.append(f"Markdown file lacks final newline: {path.relative_to(root)}")
            errors.extend(link_errors(root, path, text))

    for skill_name in SKILL_NAMES:
        prompt = root / SOURCE_SKILL_ROOT / skill_name / "references" / "prompt-template.md"
        if prompt.is_file():
            content = prompt.read_text(encoding="utf-8")
            for heading in ("## Input", "## Output", "## Required", "## Forbidden", "## Positive example", "## Negative example"):
                if heading not in content:
                    errors.append(f"{prompt.relative_to(root)} lacks {heading}")

    errors.extend(tracked_ignored_paths(root))
    return errors


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Research Writing Workbench repository.")
    parser.add_argument("root", nargs="?", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    errors = validate_repository(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Repository validation failed with {len(errors)} issue(s).")
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
