#!/usr/bin/env python3
"""Create a poster via a verified, pinned external Poster Harness checkout.

This adapter contains no Poster Harness template or source code.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

CONFIG = Path(__file__).resolve().parents[1] / "references" / "upstream.json"
REQUIRED = ("scripts/new-poster.py", "AGENTS.md", "brief.md", "outline.md",
            "main.tex", "poster-style.sty", "Makefile")


def command(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def canonical_remote(url):
    """Allow equivalent HTTPS and SSH GitHub remotes, or an exact local fixture."""
    url = url.strip().rstrip("/")
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url.split(":", 1)[1]
    if url.startswith("ssh://git@github.com/"):
        url = "https://github.com/" + url.split("github.com/", 1)[1]
    if url.endswith(".git"):
        url = url[:-4]
    return url.lower() if url.startswith("https://github.com/") else url


def verify_template(folder, repository, pin):
    if not folder.is_dir():
        raise ValueError(f"Poster Harness checkout not found: {folder}")
    origin = command("git", "-C", str(folder), "remote", "get-url", "origin")
    if canonical_remote(origin) != canonical_remote(repository):
        raise ValueError(f"Unexpected template origin: {origin} (expected {repository})")
    current = command("git", "-C", str(folder), "rev-parse", "HEAD")
    if current != pin:
        raise ValueError(f"Template at {current}, but skill pins {pin}. "
                         "Do not auto-pull; review and update the pin explicitly.")
    if command("git", "-C", str(folder), "status", "--porcelain", "--untracked-files=all"):
        raise ValueError(f"Template has uncommitted/untracked changes: {folder}")
    for relative in REQUIRED:
        if not (folder / relative).is_file():
            raise ValueError(f"Pinned template missing {relative}")
    print(f"Verified Poster Harness: {folder} @ {pin}")


def bootstrap(folder, repository, pin):
    if folder.exists():
        return
    folder.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{folder.name}.clone-", dir=folder.parent))
    try:
        subprocess.run(["git", "clone", "--no-checkout", repository, str(staging)], check=True)
        subprocess.run(["git", "-C", str(staging), "checkout", "--detach", pin], check=True)
        verify_template(staging, repository, pin)
        if folder.exists():
            raise ValueError(f"Template path appeared during checkout: {folder}")
        staging.rename(folder)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", help="new independent poster directory")
    parser.add_argument("--template", help="existing pinned checkout (or bootstrap destination)")
    parser.add_argument("--config", type=Path, default=CONFIG,
                        help="upstream pin/config file; intended for testing or explicit upgrades")
    parser.add_argument("--bootstrap", action="store_true",
                        help="clone pinned upstream if checkout is missing (requires network)")
    parser.add_argument("--verify", action="store_true", help="verify checkout without creating a poster")
    args = parser.parse_args()
    if args.verify and args.destination:
        parser.error("--verify cannot be combined with a poster destination")
    if not args.verify and not args.destination:
        parser.error("a poster destination is required unless --verify is set")

    config = json.loads(args.config.read_text(encoding="utf-8"))
    repository, pin = config["repository"], config["commit"]
    if not re.fullmatch(r"[a-fA-F0-9]{40}", pin):
        parser.error("pin must be a complete 40-character commit SHA")
    template = Path(args.template or os.environ.get("POSTER_HARNESS_TEMPLATE")
                    or config["template_dir"]).expanduser().resolve()
    try:
        if args.bootstrap:
            bootstrap(template, repository, pin)
        verify_template(template, repository, pin)
        if args.verify:
            return 0
        destination = Path(args.destination).expanduser().resolve()
        if destination == template or template in destination.parents:
            raise ValueError("Poster destination must be outside the template checkout")
        if destination.exists():
            raise ValueError(f"Poster destination already exists: {destination}")
        # Upstream owns the actual copying and project scaffold.
        subprocess.run([sys.executable, str(template / "scripts" / "new-poster.py"),
                        str(destination)], check=True, cwd=template)
        print(f"Independent poster created at: {destination}")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
