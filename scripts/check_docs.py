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
TEACHING_MARKDOWN = [
    path
    for path in ACTIVE_MARKDOWN
    if "docs/exam-201" in path.as_posix()
    or "docs/exam-202" in path.as_posix()
    or path.as_posix().endswith("appendices/web-stacks.md")
]

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
OBJECTIVE_RE = re.compile(r"(?<![\d.])(?:20[0-9]|21[0-2])\.[1-5](?![\d.])")
EXPLANATION_ROW_RE = re.compile(r"^\| \d+ \|")
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


def check_teaching_structure(path: Path, text: str, errors: list[str]) -> None:
    if "BEGIN BEGINNER FOUNDATION" not in text:
        errors.append(f"{relative(path)}: missing beginner theory section")

    lines = text.splitlines()
    in_fence = False
    fence_token = ""
    code_start = 0
    nonempty_code_lines = 0

    for index, line in enumerate(lines):
        stripped = line.lstrip()
        is_fence = (
            stripped.startswith(BACKTICK_FENCE)
            or stripped.startswith(TILDE_FENCE)
        )
        if not in_fence and is_fence:
            in_fence = True
            fence_token = stripped[:3]
            code_start = index + 1
            nonempty_code_lines = 0
            continue
        if not in_fence:
            continue
        if is_fence and stripped[:3] == fence_token:
            in_fence = False
            cursor = index + 1
            while cursor < len(lines) and not lines[cursor].strip():
                cursor += 1
            if (
                cursor >= len(lines)
                or not lines[cursor].startswith("<!-- LINE-BY-LINE ")
            ):
                errors.append(
                    f"{relative(path)}:{code_start}: "
                    "code block has no immediate line-by-line explanation"
                )
                continue
            row_count = 0
            cursor += 1
            while cursor < len(lines) and row_count == 0:
                if EXPLANATION_ROW_RE.match(lines[cursor]):
                    break
                cursor += 1
            while cursor < len(lines) and EXPLANATION_ROW_RE.match(lines[cursor]):
                row_count += 1
                cursor += 1
            if row_count != nonempty_code_lines:
                errors.append(
                    f"{relative(path)}:{code_start}: "
                    f"{nonempty_code_lines} non-empty code lines but "
                    f"{row_count} explanation rows"
                )
            continue
        if line.strip():
            nonempty_code_lines += 1


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

    for path in TEACHING_MARKDOWN:
        check_teaching_structure(path, path.read_text(encoding="utf-8"), errors)

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
        f"Validated {len(ALL_MARKDOWN)} Markdown files, "
        f"{len(EXPECTED_OBJECTIVES)} LPIC-2 objectives, and "
        f"{len(TEACHING_MARKDOWN)} beginner-first teaching files."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
