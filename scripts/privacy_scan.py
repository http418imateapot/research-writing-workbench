"""Heuristic privacy and secret scan; it does not replace human review."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Pattern

EXCLUDED = {".git", ".work", "dist", "__pycache__"}
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".cff", ".txt", ""}


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: Pattern[str]
    reason: str


RULES = [
    Rule("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "possible private email"),
    Rule("secret-assignment", re.compile(r"\b(?:api[_-]?key|token|secret|password|credential)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{8,}", re.I), "possible credential assignment"),
    Rule("windows-home", re.compile(r"\b[A-Z]:\\Users\\[^\\\s]+", re.I), "personal Windows home path"),
    Rule("unix-home", re.compile(r"/(?:Users|home)/[^/\s]+"), "personal Unix home path"),
    Rule("phone", re.compile(r"(?<!\d)(?:\+\d{1,3}[ -]?)?(?:\(?\d{2,4}\)?[ -]?){2,4}\d{3,4}(?!\d)"), "possible phone number"),
    Rule("private-ip", re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"), "private IPv4 address"),
    Rule("connection-string", re.compile(r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s]+", re.I), "possible connection string"),
    Rule("uuid", re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I), "possible private file or resource ID"),
    Rule("long-token", re.compile(r"\b[A-Za-z0-9-]{40,}\b"), "possible long token"),
    Rule("private-url", re.compile(r"https?://(?:localhost|[^/\s]+\.(?:internal|local|corp))(?:[/:][^\s]*)?", re.I), "private or internal URL"),
    Rule("source-package", re.compile(r"AI_研究架構與寫作工作台_" + r"SKILL_v2|/mnt/" + r"data/|\\Down" + r"loads\\", re.I), "temporary source package or local mount path"),
]


def load_allowlist(path: Optional[Path]) -> List[Pattern[str]]:
    if path is None or not path.is_file():
        return []
    patterns = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            patterns.append(re.compile(line, re.I))
    return patterns


def files_to_scan(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name == ".privacy-allowlist":
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDED for part in rel.parts):
            continue
        if len(rel.parts) >= 3 and rel.parts[:3] == ("tests", "fixtures", "unsafe"):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name.startswith("."):
            yield path


def scan(root: Path, allowlist_path: Optional[Path] = None) -> List[str]:
    root = root.resolve()
    allowlist = load_allowlist(allowlist_path)
    findings = []
    for path in files_to_scan(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, 1):
            for rule in RULES:
                if rule.pattern.search(line) and not any(pattern.search(line) for pattern in allowlist):
                    findings.append(f"{path.relative_to(root)}:{number}: {rule.name}: {rule.reason}")
    return findings


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run a heuristic privacy scan.")
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--allowlist", type=Path)
    args = parser.parse_args(argv)
    allowlist = args.allowlist
    if allowlist is None and (args.root / ".privacy-allowlist").exists():
        allowlist = args.root / ".privacy-allowlist"
    findings = scan(args.root, allowlist)
    if findings:
        for finding in findings:
            print(f"FINDING: {finding}")
        print(f"Privacy scan failed with {len(findings)} finding(s).")
        return 1
    print("Privacy scan passed. This heuristic scan does not replace human review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
