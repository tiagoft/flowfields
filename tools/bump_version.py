"""Bump the patch number of the flowfields version (0.1.0 -> 0.1.1).

Updates pyproject.toml, the flowfields entry in uv.lock, and the version of
the npm package in js/package.json and js/package-lock.json, so Python and JS
share one version. The git hooks in .githooks run it on every commit that
lands on main.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def bump(version: str) -> str:
    major, minor, patch = version.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def write_json(path: Path, data: dict) -> None:
    """Writes JSON the way npm does: two spaces and a final newline"""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


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

    package = ROOT / "js" / "package.json"
    package_lock = ROOT / "js" / "package-lock.json"
    if package.exists():
        data = json.loads(package.read_text())
        data["version"] = new
        write_json(package, data)
    if package_lock.exists():
        data = json.loads(package_lock.read_text())
        data["version"] = new
        data["packages"][""]["version"] = new
        write_json(package_lock, data)

    print(f"flowfields {old} -> {new}")


if __name__ == "__main__":
    main()
