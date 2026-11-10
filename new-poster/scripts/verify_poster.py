#!/usr/bin/env python3
"""Conservative release gate for a generated Poster Harness project.

Checks only objectively detectable problems. Scientific correctness, source
coverage, figure readability, and QR scannability still need human review.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


def verify(folder):
    errors = []
    required = ("brief.md", "outline.md", "content.tex", "main.tex",
                "output/pdf/main.pdf", "sources/citations.json")
    for rel in required:
        if not (folder / rel).is_file():
            errors.append(f"Missing {rel}")
    for rel in ("brief.md", "outline.md", "content.tex"):
        path = folder / rel
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            if re.search(r"TODO\[|https?://example\.(?:com|org)|\\FigurePlaceholder\b", text):
                errors.append(f"Unresolved placeholder/link in {rel}")
    citations = folder / "sources/citations.json"
    if citations.is_file():
        try:
            data = json.loads(citations.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not data:
                errors.append("sources/citations.json must be a nonempty keyed object")
        except (ValueError, UnicodeError) as exc:
            errors.append(f"Invalid sources/citations.json: {exc}")
    pdf = folder / "output/pdf/main.pdf"
    if pdf.is_file():
        try:
            result = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                                    text=True, check=True)
            pages = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
            if pages is None or pages.group(1) != "1":
                errors.append("Expected a single-page PDF")
        except FileNotFoundError:
            errors.append("pdfinfo is required for PDF page-count verification")
        except subprocess.CalledProcessError as exc:
            errors.append(f"pdfinfo failed: {exc.stderr.strip()}")
    if errors:
        for issue in errors:
            print(f"FAIL: {issue}", file=sys.stderr)
        return 1
    print("PASS: scaffold, obvious placeholders, citation register, and one-page PDF")
    print("STILL REQUIRED: inspect rendered PDF, source claims/figures, QR codes, print legibility")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="independent poster project directory")
    args = parser.parse_args()
    return verify(args.project.expanduser().resolve())


if __name__ == "__main__":
    sys.exit(main())
