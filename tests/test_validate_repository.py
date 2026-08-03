from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate_repository import validate_repository


ROOT = Path(__file__).resolve().parents[1]


class RepositoryValidationTests(unittest.TestCase):
    def copy_repository(self) -> tuple:
        temp = tempfile.TemporaryDirectory()
        target = Path(temp.name) / "repository"
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", ".work", ".venv", "dist", "__pycache__", "*.pyc"),
        )
        return temp, target

    def test_valid_repository(self) -> None:
        self.assertEqual([], validate_repository(ROOT))

    def test_missing_skill_fails(self) -> None:
        temp, target = self.copy_repository()
        self.addCleanup(temp.cleanup)
        (target / "skills/research-writing-workbench/SKILL.md").unlink()
        self.assertTrue(any("SKILL.md" in error for error in validate_repository(target)))

    def test_wrong_frontmatter_name_fails(self) -> None:
        temp, target = self.copy_repository()
        self.addCleanup(temp.cleanup)
        skill = target / "skills/research-writing-workbench/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace(
            "name: research-writing-workbench", "name: wrong-name", 1
        ), encoding="utf-8")
        self.assertTrue(any("metadata does not match directory" in error for error in validate_repository(target)))

    def test_unclosed_fence_fails(self) -> None:
        temp, target = self.copy_repository()
        self.addCleanup(temp.cleanup)
        readme = target / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "```text\nunclosed\n", encoding="utf-8")
        self.assertTrue(any("unbalanced" in error for error in validate_repository(target)))

    def test_missing_internal_link_fails(self) -> None:
        temp, target = self.copy_repository()
        self.addCleanup(temp.cleanup)
        readme = target / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "[broken](missing-file.md)\n", encoding="utf-8")
        self.assertTrue(any("missing link target" in error for error in validate_repository(target)))

    def test_unexpected_template_fails(self) -> None:
        temp, target = self.copy_repository()
        self.addCleanup(temp.cleanup)
        template = target / "skills/research-writing-workbench/assets/templates/extra.md"
        template.write_text("# Extra\n", encoding="utf-8")
        self.assertTrue(any("whitelist mismatch" in error for error in validate_repository(target)))

    def test_missing_ctcc_marker_fails(self) -> None:
        temp, target = self.copy_repository()
        self.addCleanup(temp.cleanup)
        skill = target / "skills/research-writing-workbench/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace("implementation", "build-statement"),
            encoding="utf-8",
        )
        self.assertTrue(any("lacks CTCC" in error for error in validate_repository(target)))


if __name__ == "__main__":
    unittest.main()
