from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.privacy_scan import scan


class PrivacyScanTests(unittest.TestCase):
    def test_safe_synthetic_content_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "safe.md").write_text("Artifact maturity: planned.\n", encoding="utf-8")
            self.assertEqual([], scan(root))

    def test_unsafe_patterns_are_detected(self) -> None:
        source = Path(__file__).parent / "fixtures/unsafe/content.txt"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "content.txt").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            findings = scan(root)
            joined = "\n".join(findings)
            for rule in ("email", "secret-assignment", "windows-home", "connection-string"):
                self.assertIn(rule, joined)

    def test_allowlist_excludes_explicit_examples(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "content.md").write_text("nobody@example.invalid\n", encoding="utf-8")
            allowlist = root / ".privacy-allowlist"
            allowlist.write_text(r"example\.invalid" + "\n", encoding="utf-8")
            self.assertEqual([], scan(root, allowlist))

    def test_allowlist_can_scope_public_bibliographic_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "citation.md").write_text("isbn = 9789863128601\n", encoding="utf-8")
            allowlist = root / ".privacy-allowlist"
            allowlist.write_text(r"9789863128601" + "\n", encoding="utf-8")
            self.assertEqual([], scan(root, allowlist))

    def test_allowlist_file_is_not_scanned_as_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            allowlist = root / ".privacy-allowlist"
            allowlist.write_text(r"books\.example/public-id" + "\n", encoding="utf-8")
            self.assertEqual([], scan(root, allowlist))


if __name__ == "__main__":
    unittest.main()
