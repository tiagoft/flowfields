"""Bump the patch number of the flowfields version (0.1.0 -> 0.1.1).

Updates pyproject.toml and the flowfields entry in uv.lock. The git hooks in
.githooks run it on every commit that lands on main.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def bump(version: str) -> str:
    major, minor, patch = version.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def main() -> None:
    pyproject = ROOT / "pyproject.toml"
    text = pyproject.read_text()
    match = re.search(r'^version = "(\d+\.\d+\.\d+)"$', text, re.MULTILINE)
    if match is None:
        sys.exit("bump_version: no version = \"X.Y.Z\" line in pyproject.toml")
    old = match.group(1)
    new = bump(old)
    pyproject.write_text(text[: match.start(1)] + new + text[match.end(1) :])

    lock = ROOT / "uv.lock"
    if lock.exists():
        entry = 'name = "flowfields"\nversion = "{}"\n'
        lock_text = lock.read_text()
        if entry.format(old) not in lock_text:
            sys.exit(f"bump_version: flowfields {old} not found in uv.lock")
        lock.write_text(lock_text.replace(entry.format(old), entry.format(new), 1))

    print(f"flowfields {old} -> {new}")


if __name__ == "__main__":
    main()
