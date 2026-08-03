from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from build import SCRIPT_MAP, SKILL_NAMES, build_distribution


ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def zip_hashes(dist: Path):
    return {
        path.relative_to(dist).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(dist.rglob("*.zip"))
    }


class BuildTests(unittest.TestCase):
    def build_temp(self):
        temp = tempfile.TemporaryDirectory()
        dist = Path(temp.name) / "dist"
        dist.mkdir()
        build_distribution(ROOT, dist)
        return temp, dist

    def test_distribution_shapes_and_manifest(self) -> None:
        temp, dist = self.build_temp()
        self.addCleanup(temp.cleanup)
        self.assertTrue((dist / f"pack-{VERSION}.zip").is_file())
        manifest = (dist / "checksums.sha256").read_text(encoding="utf-8")
        self.assertNotIn("checksums.sha256", manifest)
        for skill_name in SKILL_NAMES:
            self.assertTrue((dist / "agents-skills" / skill_name / "SKILL.md").is_file())
            self.assertEqual(VERSION, (dist / "agents-skills" / skill_name / "VERSION").read_text(encoding="utf-8").strip())
            archive = dist / "claude" / f"{skill_name}-{VERSION}.zip"
            with zipfile.ZipFile(archive) as handle:
                names = handle.namelist()
            self.assertIn(f"{skill_name}/SKILL.md", names)
            self.assertTrue(all(name.startswith(f"{skill_name}/") for name in names))
            self.assertFalse(any("tests/" in name or "fixtures/" in name or ".work/" in name for name in names))
        with zipfile.ZipFile(dist / f"pack-{VERSION}.zip") as handle:
            pack_names = handle.namelist()
        self.assertIn("README.md", pack_names)
        self.assertIn("INSTALL.md", pack_names)
        self.assertTrue(all(not name.startswith("tests/") and not name.startswith("fixtures/") for name in pack_names))

    def test_two_builds_are_byte_reproducible(self) -> None:
        first_temp, first = self.build_temp()
        second_temp, second = self.build_temp()
        self.addCleanup(first_temp.cleanup)
        self.addCleanup(second_temp.cleanup)
        self.assertEqual(zip_hashes(first), zip_hashes(second))

    def test_packaged_public_scripts_are_self_contained(self) -> None:
        temp, dist = self.build_temp()
        self.addCleanup(temp.cleanup)
        for skill_name, scripts in SCRIPT_MAP.items():
            for script_name in scripts:
                if script_name.startswith("_"):
                    continue
                script = dist / "agents-skills" / skill_name / "scripts" / script_name
                result = subprocess.run(
                    [sys.executable, str(script), "--help"],
                    cwd=script.parent,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, f"{script}: {result.stderr}")

    def test_build_does_not_modify_source_trees(self) -> None:
        before = {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for base in (ROOT / "skills", ROOT / "shared")
            for path in base.rglob("*")
            if path.is_file()
        }
        temp, _ = self.build_temp()
        self.addCleanup(temp.cleanup)
        after = {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for base in (ROOT / "skills", ROOT / "shared")
            for path in base.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_dist_is_ignored_and_untracked(self) -> None:
        ignored = subprocess.run(
            ["git", "check-ignore", "--no-index", "dist/example"], cwd=ROOT, text=True, capture_output=True, check=False
        )
        self.assertEqual(0, ignored.returncode)
        tracked = subprocess.run(
            ["git", "ls-files", "dist"], cwd=ROOT, text=True, capture_output=True, check=False
        )
        self.assertEqual(0, tracked.returncode)
        self.assertEqual("", tracked.stdout)


if __name__ == "__main__":
    unittest.main()
