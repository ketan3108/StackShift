"""Reject unsupported product claims in shipped text."""

import sys
from pathlib import Path

FORBIDDEN = (
    "proof it won't break",
    "100x cost savings",
    "better than either model",
    "works across providers",
    "<10µs latency",
    "eliminates the rebuild",
)
ROOTS = (Path("README.md"), Path("docs"), Path("src"))
SUFFIXES = {".md", ".py"}


def paths() -> list[Path]:
    """Return product text files, omitting this checker to avoid self-matches."""
    output: list[Path] = []
    for root in ROOTS:
        if root.is_file():
            output.append(root)
        elif root.exists():
            output.extend(path for path in root.rglob("*") if path.suffix in SUFFIXES)
    return [path for path in output if path != Path(__file__)]


def main() -> int:
    """Print all forbidden claims and return a CI-friendly status."""
    failures: list[str] = []
    for path in paths():
        content = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN:
            if phrase in content:
                failures.append(f"{path}: forbidden claim: {phrase}")
    if failures:
        print("\n".join(failures))
        return 1
    print("Claims check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
