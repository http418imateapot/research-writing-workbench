"""Validate repository structure and text contracts without third-party packages."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional

SKILL_REL = Path(".agents/skills/research-writing-workbench")
REQUIRED_FILES = [
    Path("README.md"), Path("README.en.md"), Path("AGENTS.md"),
    Path("ARCHITECTURE.md"), Path("VERSION"), Path("CITATION.cff"),
    Path("CHANGELOG.md"), Path("LICENSE"), Path("NOTICE"),
    Path("CONTRIBUTING.md"), Path("CODE_OF_CONDUCT.md"), Path("SECURITY.md"),
    SKILL_REL / "SKILL.md",
    Path("prompts/master-prompt.zh-TW.md"),
]
REQUIRED_DIRS = [
    SKILL_REL / "references", SKILL_REL / "assets/templates",
    Path("docs"), Path("prompts"), Path("examples"), Path("scripts"), Path("tests"),
]
TEMPLATES = [
    "engineering-question-brief.md", "validation-contract.md", "scenario-matrix.md",
    "trace-index.md", "execution-record.md", "counterexample-review.md",
    "bounded-claim-record.md", "ai-use-record.md", "release-check.md",
]
REFERENCES = [
    "01-domain-and-ctcc.md", "02-contract-and-comparison.md",
    "03-trace-and-evidence.md", "04-counterexamples.md",
    "05-bounded-writing.md", "06-ai-audit-and-release.md",
]
REQUIRED_METHOD_MARKERS = [
    "契約—軌跡—反例—主張", "planned", "reproduced",
    "implementation", "withdraw", "[未取得產物]",
]
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".cff", ".txt", ""}
EXCLUDED_PARTS = {".git", ".work", "dist", "__pycache__"}


def text_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name.startswith("."):
            yield path


def parse_frontmatter(text: str) -> Dict[str, str]:
    lines = text.splitlines()
    if len(lines) < 4 or lines[0] != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    values = {}
    for line in lines[1:end]:
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"\'')
    return values


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
    errors = []
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
    result = subprocess.run(
        ["git", "ls-files"], cwd=root, text=True, capture_output=True, check=False
    )
    if result.returncode != 0:
        return ["unable to inspect tracked files with git ls-files"]
    bad = []
    for name in result.stdout.splitlines():
        parts = Path(name).parts
        if any(part in {"dist", ".work", "__pycache__"} for part in parts):
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

    skill_files = sorted((root / ".agents/skills").glob("*/SKILL.md")) if (root / ".agents/skills").exists() else []
    if len(skill_files) != 1 or (skill_files and skill_files[0].parent.name != "research-writing-workbench"):
        errors.append("repository must contain exactly one canonical skill directory")

    skill_path = root / SKILL_REL / "SKILL.md"
    if skill_path.is_file():
        try:
            metadata = parse_frontmatter(skill_path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as exc:
            metadata = {}
            errors.append(f"invalid UTF-8: {skill_path.relative_to(root)}: {exc}")
        if metadata.get("name") != "research-writing-workbench":
            errors.append("SKILL.md frontmatter name must be research-writing-workbench")
        if not metadata.get("description"):
            errors.append("SKILL.md frontmatter description is required")
        skill_text = skill_path.read_text(encoding="utf-8")
        for marker in REQUIRED_METHOD_MARKERS:
            if marker not in skill_text:
                errors.append(f"SKILL.md lacks CTCC method marker: {marker}")

    version = ""
    version_path = root / "VERSION"
    if version_path.is_file():
        version = version_path.read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
            errors.append("VERSION is not a basic semantic version")
    citation = root / "CITATION.cff"
    if citation.is_file() and version:
        text = citation.read_text(encoding="utf-8")
        match = re.search(r'^version:\s*["\']?([^"\'\s]+)', text, re.M)
        if not match or match.group(1) != version:
            errors.append("CITATION.cff version does not match VERSION")

    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        if "不是通用研究方法" not in text or "CTCC" not in text or "研究者" not in text:
            errors.append("README.md lacks domain positioning, CTCC, or researcher control")

    template_dir = root / SKILL_REL / "assets/templates"
    actual_templates = sorted(path.name for path in template_dir.glob("*.md")) if template_dir.is_dir() else []
    for name in sorted(set(TEMPLATES) - set(actual_templates)):
        errors.append(f"missing release template: {name}")
    for name in sorted(set(actual_templates) - set(TEMPLATES)):
        errors.append(f"unexpected release template: {name}")

    reference_dir = root / SKILL_REL / "references"
    actual_references = sorted(path.name for path in reference_dir.glob("*.md")) if reference_dir.is_dir() else []
    for name in sorted(set(REFERENCES) - set(actual_references)):
        errors.append(f"missing release reference: {name}")
    for name in sorted(set(actual_references) - set(REFERENCES)):
        errors.append(f"unexpected release reference: {name}")

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

    errors.extend(tracked_ignored_paths(root))
    return errors


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Research Writing Workbench repository.")
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
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
