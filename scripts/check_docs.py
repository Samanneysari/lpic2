#!/usr/bin/env python3
"""Validate the active LPIC-2 Markdown guide with the Python standard library."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ALL_MARKDOWN = sorted(ROOT.rglob("*.md"))
ACTIVE_MARKDOWN = [path for path in ALL_MARKDOWN if "legacy" not in path.parts]

EXPECTED_OBJECTIVES = {
    "200.1", "200.2",
    "201.1", "201.2", "201.3",
    "202.1", "202.2", "202.3",
    "203.1", "203.2", "203.3",
    "204.1", "204.2", "204.3",
    "205.1", "205.2", "205.3",
    "206.1", "206.2", "206.3",
    "207.1", "207.2", "207.3",
    "208.1", "208.2", "208.3", "208.4",
    "209.1", "209.2",
    "210.1", "210.2", "210.3", "210.4",
    "211.1", "211.2", "211.3",
    "212.1", "212.2", "212.3", "212.4", "212.5",
}

UNSAFE_PATTERNS = {
    "[cite:": "unresolved generated citation",
    "PLEASE DISABLE SELINUX": "unsafe SELinux instruction",
    "chmod -R 755": "overly broad recursive permissions",
    "dnf module list reset php": "invalid dnf module command",
    "IDENTIFIED BY 'password'": "literal weak database password",
}

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
OBJECTIVE_RE = re.compile(r"\b(?:20[0-9]|21[0-2])\.\d\b")
BACKTICK_FENCE = chr(96) * 3
TILDE_FENCE = "~" * 3


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def check_fences(path: Path, text: str, errors: list[str]) -> None:
    stack: list[tuple[str, int]] = []
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if not (
            stripped.startswith(BACKTICK_FENCE)
            or stripped.startswith(TILDE_FENCE)
        ):
            continue
        token = stripped[:3]
        if stack and stack[-1][0] == token:
            stack.pop()
        elif not stack:
            stack.append((token, number))
        else:
            errors.append(
                f"{relative(path)}:{number}: mixed fence closes {stack[-1][0]}"
            )
    for token, number in stack:
        errors.append(f"{relative(path)}:{number}: unclosed {token} fence")


def check_links(path: Path, text: str, errors: list[str]) -> None:
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = unquote(target.split("#", 1)[0])
        if not clean:
            continue
        destination = (path.parent / clean).resolve()
        try:
            destination.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{relative(path)}: link leaves repository: {target}")
            continue
        if not destination.exists():
            errors.append(f"{relative(path)}: missing local link target: {target}")


def main() -> int:
    errors: list[str] = []
    found_objectives: set[str] = set()

    if not ALL_MARKDOWN:
        errors.append("No Markdown files found.")

    for path in ALL_MARKDOWN:
        text = path.read_text(encoding="utf-8")
        check_fences(path, text, errors)

    for path in ACTIVE_MARKDOWN:
        text = path.read_text(encoding="utf-8")
        found_objectives.update(OBJECTIVE_RE.findall(text))
        check_links(path, text, errors)

        for line_number, line in enumerate(text.splitlines(), 1):
            if line.rstrip() != line:
                errors.append(f"{relative(path)}:{line_number}: trailing whitespace")
            for pattern, message in UNSAFE_PATTERNS.items():
                if pattern in line:
                    errors.append(
                        f"{relative(path)}:{line_number}: {message}: {pattern}"
                    )

    missing = sorted(EXPECTED_OBJECTIVES - found_objectives)
    unknown = sorted(found_objectives - EXPECTED_OBJECTIVES)
    if missing:
        errors.append("Missing objective references: " + ", ".join(missing))
    if unknown:
        errors.append("Unknown objective references: " + ", ".join(unknown))

    if errors:
        print("Documentation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {len(ALL_MARKDOWN)} Markdown files and "
        f"{len(EXPECTED_OBJECTIVES)} LPIC-2 objectives."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
