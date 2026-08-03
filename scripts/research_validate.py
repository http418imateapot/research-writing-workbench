"""Validate governed research JSON and cross-file references."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

try:
    from ._common import GovernanceError, load_project, print_error, resolve_schema_dir
except ImportError:  # Direct script execution and packaged Skill layout.
    from _common import GovernanceError, load_project, print_error, resolve_schema_dir


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate governed research records and references.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--schema-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        schema_dir = resolve_schema_dir(Path(__file__), args.schema_dir)
        documents = load_project(args.project_dir.resolve(), schema_dir)
    except GovernanceError as exc:
        return print_error(exc)
    print(f"Validation passed for {len(documents)} governed document(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
