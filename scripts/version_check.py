#!/usr/bin/env python3
"""Check that version strings are synchronized across files.

The version is sourced from ``setup.py`` and verified against a list of
other files that should contain the same version identifier.  The check is
light‑weight and intended to be used as a pre‑commit hook to prevent commits
that forget to bump one of the files when the project version changes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


SETUP_VERSION_RE = re.compile(r"version\s*=\s*['\"](\d+\.\d+\.\d+)['\"]")
VERSION_LINE_RE = re.compile(r"^\s*version\s*:\s*(\d+\.\d+\.\d+)\b", re.IGNORECASE)


FILES_TO_CHECK = [
    Path("READ.md"),
    Path("app/__init__.py"),
]


def get_repo_version() -> str:
    """Extract the version string from ``setup.py``."""
    setup_text = Path("setup.py").read_text()
    match = SETUP_VERSION_RE.search(setup_text)
    if not match:
        print("Unable to determine version from setup.py", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def file_has_version(path: Path, version: str) -> bool:
    """Return ``True`` if *path* contains the expected version line."""
    lines = path.read_text().splitlines()[:10]
    for line in lines:
        match = VERSION_LINE_RE.search(line)
        if match:
            found = match.group(1)
            if found != version:
                print(
                    f"{path}: version mismatch (found {found}, expected {version})",
                    file=sys.stderr,
                )
                return False
            return True

    print(f"{path}: missing version line for {version}", file=sys.stderr)
    return False


def main() -> None:
    version = get_repo_version()

    ok = True
    for path in FILES_TO_CHECK:
        if not path.exists():
            print(f"{path}: file not found", file=sys.stderr)
            ok = False
            continue
        if not file_has_version(path, version):
            ok = False

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()

