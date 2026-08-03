#!/usr/bin/env python3
"""Validate the lightweight research-kb conventions.

Uses only the Python standard library. It intentionally validates a small set
of high-value invariants rather than attempting to parse all of Obsidian.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

BLOCK_ID_RE = re.compile(r"(?m)^\^([A-Za-z0-9][A-Za-z0-9-]*)\s*$")
TEMPLATE_RE = re.compile(r"\{\{[^}]+\}\}")
MARKDOWN_LINK_URL_RE = re.compile(r"https?://[^\s)>\"']+")

EXPECTED = {
    "10 Sources": "source",
    "20 Concepts": "concept",
    "30 Projects": "project",
    "40 Syntheses": "synthesis",
}
ALLOWED_ACCESS = {"full-text", "abstract-only", "secondary", "unavailable"}


def iter_markdown(root: Path, folder: str) -> Iterable[Path]:
    base = root / folder
    if not base.exists():
        return []
    return (
        path
        for path in base.rglob("*.md")
        if not any(part.startswith(".") for part in path.relative_to(root).parts)
    )


def parse_frontmatter(text: str) -> tuple[dict[str, str], int]:
    """Parse simple top-level YAML scalars from frontmatter.

    This is deliberately not a full YAML parser. It is enough for invariant
    checks and avoids adding PyYAML as a dependency.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, 0

    data: dict[str, str] = {}
    end = 0
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = index + 1
            break
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data, end


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Vault root (default: current directory)",
    )
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()

    errors: list[str] = []
    warnings: list[str] = []
    block_locations: dict[str, list[str]] = defaultdict(list)
    source_urls: dict[str, list[str]] = defaultdict(list)

    if not (root / "AGENTS.md").exists():
        warnings.append("Missing AGENTS.md at vault root.")
    if not (root / "KB_SCHEMA.md").exists():
        warnings.append("Missing KB_SCHEMA.md at vault root.")

    for folder, expected_type in EXPECTED.items():
        base = root / folder
        if not base.exists():
            warnings.append(f"Missing expected folder: {folder}/")
            continue

        for path in iter_markdown(root, folder):
            relative = path.relative_to(root)
            text = path.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(text)

            if not frontmatter:
                errors.append(f"{relative}: missing YAML frontmatter.")
            elif frontmatter.get("type") != expected_type:
                errors.append(
                    f"{relative}: expected type '{expected_type}', "
                    f"found '{frontmatter.get('type', '')}'."
                )

            for match in BLOCK_ID_RE.finditer(text):
                block_id = match.group(1)
                block_locations[block_id].append(
                    f"{relative}:{line_number(text, match.start())}"
                )

            for match in TEMPLATE_RE.finditer(text):
                warnings.append(
                    f"{relative}:{line_number(text, match.start())}: "
                    f"unresolved template placeholder {match.group(0)!r}."
                )

            if expected_type == "source":
                url = frontmatter.get("url", "")
                access = frontmatter.get("source_access", "")
                title = frontmatter.get("title", "")

                if not title:
                    errors.append(f"{relative}: source note has no title.")
                if not url:
                    errors.append(f"{relative}: source note has no url.")
                elif not MARKDOWN_LINK_URL_RE.fullmatch(url):
                    errors.append(f"{relative}: invalid or non-HTTP source url: {url!r}.")
                else:
                    canonical = url.rstrip("/")
                    source_urls[canonical].append(str(relative))

                if access not in ALLOWED_ACCESS:
                    errors.append(
                        f"{relative}: source_access must be one of "
                        f"{sorted(ALLOWED_ACCESS)}, found {access!r}."
                    )

                if access in {"abstract-only", "secondary", "unavailable"}:
                    locator_claims = re.findall(
                        r"(?im)^\*\*Locator:\*\*\s*(.+)$", text
                    )
                    suspicious = [
                        item
                        for item in locator_claims
                        if re.search(
                            r"\b(table|figure|equation|theorem|appendix|algorithm)\b",
                            item,
                            flags=re.IGNORECASE,
                        )
                    ]
                    if suspicious:
                        warnings.append(
                            f"{relative}: detailed locators occur despite "
                            f"source_access={access!r}; verify they were not inferred."
                        )

    for block_id, locations in sorted(block_locations.items()):
        if len(locations) > 1:
            errors.append(
                f"Duplicate block ID ^{block_id}: " + ", ".join(locations)
            )

    for url, locations in sorted(source_urls.items()):
        if len(locations) > 1:
            warnings.append(
                f"Duplicate source URL {url}: " + ", ".join(locations)
            )

    print(f"Research KB validation: {root}")
    print(f"Errors: {len(errors)}")
    for item in errors:
        print(f"  ERROR: {item}")
    print(f"Warnings: {len(warnings)}")
    for item in warnings:
        print(f"  WARN:  {item}")

    if errors:
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
