"""Create a deterministic ZIP containing only the canonical skill directory."""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

SKILL_NAME = "research-writing-workbench"
SKILL_REL = Path("skills") / SKILL_NAME
FIXED_TIME = (2020, 1, 1, 0, 0, 0)


def package_skill(root: Path, output_dir: Path) -> Tuple[Path, Path]:
    root = root.resolve()
    skill_dir = root / SKILL_REL
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
        raise ValueError(f"canonical skill is missing: {skill_dir}")
    output_dir = output_dir if output_dir.is_absolute() else root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"{SKILL_NAME}-skill-v{version}.zip"
    files = sorted(
        (
            path for path in skill_dir.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
            and path.name not in {".DS_Store", "Thumbs.db"}
        ),
        key=lambda path: path.relative_to(skill_dir).as_posix(),
    )
    if not any(path.relative_to(skill_dir).as_posix().startswith("references/") for path in files):
        raise ValueError("skill package has no references")
    if not any(path.relative_to(skill_dir).as_posix().startswith("assets/templates/") for path in files):
        raise ValueError("skill package has no templates")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            arcname = (Path(SKILL_NAME) / path.relative_to(skill_dir)).as_posix()
            info = zipfile.ZipInfo(arcname, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        if not names or names != sorted(names) or f"{SKILL_NAME}/SKILL.md" not in names:
            raise ValueError("package verification failed: missing or unsorted required content")
        if any(not name.startswith(f"{SKILL_NAME}/") for name in names):
            raise ValueError("package contains content outside the canonical skill")
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    manifest_path = output_dir / f"{zip_path.name}.sha256"
    manifest_path.write_bytes(f"{digest}  {zip_path.name}\n".encode("utf-8"))
    return zip_path, manifest_path


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Package the canonical repository skill.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    args = parser.parse_args(argv)
    try:
        zip_path, manifest = package_skill(args.root, args.output_dir)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Created {zip_path}")
    print(f"Created {manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
