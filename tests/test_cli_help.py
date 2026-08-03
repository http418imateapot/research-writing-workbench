from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CLIS = [
    "build.py",
    "scripts/package_skill.py",
    "scripts/privacy_scan.py",
    "scripts/validate_repository.py",
    "scripts/research_validate.py",
    "scripts/research_checklist.py",
    "scripts/research_resolve.py",
    "scripts/research_export.py",
]


class CliHelpTests(unittest.TestCase):
    def test_every_public_cli_has_successful_help(self) -> None:
        for relative in PUBLIC_CLIS:
            with self.subTest(cli=relative):
                result = subprocess.run(
                    [sys.executable, str(ROOT / relative), "--help"],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("usage:", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
