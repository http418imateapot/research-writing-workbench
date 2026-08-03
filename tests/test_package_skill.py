from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.package_skill import SKILL_NAME, package_skill


ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


class PackageSkillTests(unittest.TestCase):
    def test_package_contains_only_canonical_skill_in_sorted_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            zip_path, manifest = package_skill(ROOT, Path(temp))
            self.assertEqual(f"{SKILL_NAME}-skill-v{VERSION}.zip", zip_path.name)
            self.assertTrue(manifest.is_file())
            with zipfile.ZipFile(zip_path) as archive:
                names = archive.namelist()
            self.assertEqual(sorted(names), names)
            self.assertIn(f"{SKILL_NAME}/SKILL.md", names)
            self.assertTrue(all(name.startswith(f"{SKILL_NAME}/") for name in names))
            self.assertFalse(any("tests/" in name or "fixtures/" in name for name in names))

    def test_package_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            zip_one, _ = package_skill(ROOT, Path(first))
            zip_two, _ = package_skill(ROOT, Path(second))
            self.assertEqual(zip_one.read_bytes(), zip_two.read_bytes())


if __name__ == "__main__":
    unittest.main()
