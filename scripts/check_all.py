"""Run all local quality checks and stop at the first failure."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    commands: List[List[str]] = [
        [sys.executable, "-m", "compileall", "-q", "build.py", "scripts", "tests"],
        [sys.executable, "-m", "pytest", "-q"],
        [sys.executable, "scripts/validate_repository.py"],
        [sys.executable, "scripts/privacy_scan.py"],
        [sys.executable, "build.py", "--check"],
    ]
    for command in commands:
        print(f"Running: {' '.join(command)}", flush=True)
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            return result.returncode
    with tempfile.TemporaryDirectory(prefix="rww-package-") as temp_dir:
        command = [sys.executable, "scripts/package_skill.py", "--output-dir", temp_dir]
        print(f"Running: {' '.join(command)}", flush=True)
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            return result.returncode
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
