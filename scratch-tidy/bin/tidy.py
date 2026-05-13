#!/usr/bin/env python3
"""
scratch-tidy/tidy.py — audit + apply driver for the scratch-tidy skill.

Subcommands:
    audit            Walk the tmp tree, attribute via manifest + heuristics,
                     emit a CSV plan and a markdown summary. Dry-run only.
    apply            Execute a plan CSV. Default refuses to delete unowned
                     items; pass --include-unowned (and confirm per item) to
                     allow that.
    list-orphan-manifests   Show manifests whose mtime is older than 30 days.

All paths must live under the target tree (default $SCRATCH/tmp). The script
refuses to act on paths outside that tree as a safety rail.

Pure stdlib — no third-party dependencies.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import shutil
import stat
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

DEFAULT_TARGET = "${SCRATCH}/tmp"

# Auto-purge whitelist. (category, age_days_min). age None = always.
AUTOPURGE = {
    "system-socket": None,
    "hf-lock": None,
    "torch-compile-cache": 7,
    "wandb-tmp": 3,
}

# Recent-window protection: never delete anything modified within this many
# minutes regardless of category, unless --include-recent is set.
RECENT_MINUTES = 60

# Manifest format: TSV with columns ts_iso, path, intent, lifetime.
MANIFEST_COLS = ("ts_iso", "path", "intent", "lifetime")

# CSV plan output columns.
PLAN_COLS = (
    "path", "size_bytes", "mtime_iso", "category", "owner_session",
    "intent", "lifetime", "recommended_action", "destination",
    "confidence", "notes",
)

# -------------------------------------------------------------------------
# Categorization heuristics
# -------------------------------------------------------------------------

EXPERIMENT_DIR_PATTERNS = [
    re.compile(p) for p in [
        r"^vision_.*",
        r"^ninoae_.*",
        r"^qwen-.*",
        r"^qwen_.*",
        r"^task_vectors_.*",
        r"^tv_.*_test",
        r"^pdftools$",
        r"^pptxdeps$",
        r"^pip-cache$",
        r"^codex_eval_status$",
        r"^orozcoca$",
        r"^tamia_.*",
        r"^mila_cheatsheet_pages$",
        r"^wandb_.*",
        r"^relaunch_l14_.*",
        r"^run_thin_.*",
    ]
]

ENV_DUMP_NAMES = re.compile(
    r"(env_names\d*\.txt|ninoautoenc_(env|req)_.*\.txt|reqnames\.txt|"
    r"ninoenv_pip_list\.txt|req_names\d*\.txt)$"
)

WANDB_TMP_PATTERNS = [
    re.compile(r"^tmp[a-z0-9_]+wandb-(artifacts|media)$"),
    re.compile(r"^tmp[a-z0-9_]{4,}$"),
    re.compile(r"^tmp[a-z0-9_]+\.(ptx|json|log)$"),
    re.compile(r"^wandb-\d+-\d+-\d+$"),
    re.compile(r"^wandb_gpu_stats-\d+-\d+-\d+\.sock$"),
    re.compile(r"^wandb_run_state_update_\d+\.\d+\.log$"),
]

TORCH_COMPILE_PATTERNS = [
    re.compile(r"^optim\.gnn_PNAConv_propagate_.*\.py$"),
    re.compile(r"^torchinductor_.*"),
    re.compile(r".*-pycache-.*"),
    re.compile(r"^pycache-.*"),
    re.compile(r"^python-pycache$"),
    re.compile(r"^__pycache__$"),
]

HF_LOCK_PATTERN = re.compile(r"^[0-9a-f]{30,}.*\.lock$")


def is_socket(p: Path) -> bool:
    try:
        return stat.S_ISSOCK(p.lstat().st_mode)
    except OSError:
        return False


def categorize(path: Path, target: Path, manifest: dict) -> tuple[str, str]:
    """Return (category, notes). manifest maps absolute-path-str → entry dict."""
    name = path.name
    rel = path.relative_to(target) if path.is_relative_to(target) else path
    parts = rel.parts
    abs_str = str(path)

    if abs_str in manifest:
        intent = manifest[abs_str].get("intent", "unknown")
        return f"agent-authored-{intent}", "registered in manifest"

    if is_socket(path):
        return "system-socket", "unix socket file"
    if HF_LOCK_PATTERN.match(name):
        return "hf-lock", "huggingface download lock"
    for pat in TORCH_COMPILE_PATTERNS:
        if pat.match(name):
            return "torch-compile-cache", f"matches {pat.pattern}"
    if ENV_DUMP_NAMES.search(name):
        return "env-dump", "env/req dump text file"
    for pat in WANDB_TMP_PATTERNS:
        if pat.match(name):
            return "wandb-tmp", f"matches {pat.pattern}"

    # Top-level dir checks (only for direct children of target)
    if len(parts) == 1:
        for pat in EXPERIMENT_DIR_PATTERNS:
            if pat.match(name):
                # Be careful: 'qwen_paper_tables' is a real research scratch
                # dir, but matches qwen_.* — we still flag it as scratch dir
                # rather than auto-purge.
                return "experiment-scratch-dir", f"top-level dir matches {pat.pattern}"

    return "unknown", "no rule matched"


# -------------------------------------------------------------------------
# Manifest loading
# -------------------------------------------------------------------------


def load_manifest(session: str, target: Path) -> dict:
    """Return {abs_path_str: {intent, lifetime, ts_iso}} — last row wins on dup paths."""
    manifest_path = target / ".tidy_manifest" / f"{session}.tsv"
    if not manifest_path.exists():
        return {}
    out: dict[str, dict] = {}
    with manifest_path.open() as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for row in rdr:
            p = row["path"]
            out[p] = {
                "intent": row["intent"],
                "lifetime": row["lifetime"],
                "ts_iso": row["ts_iso"],
            }
    return out


# -------------------------------------------------------------------------
# Decision rubric (own items)
# -------------------------------------------------------------------------


def recommend(category: str, manifest_entry: dict | None, size_bytes: int,
              age_minutes: float) -> tuple[str, str, str, float]:
    """Return (action, destination, notes, confidence).

    action ∈ {keep, persist, purge, flag}
    """
    # Auto-purge whitelist (regardless of ownership)
    if category in AUTOPURGE:
        threshold = AUTOPURGE[category]
        if threshold is None or age_minutes >= threshold * 1440:
            return "purge", "", f"auto-purge: {category}", 0.95
        return "flag", "", f"would auto-purge but age below threshold ({threshold}d)", 0.7

    if not category.startswith("agent-authored-"):
        return "flag", "", f"non-own category: {category}", 0.6

    # Own — apply intent × lifetime rubric
    intent = manifest_entry.get("intent", "unknown") if manifest_entry else "unknown"
    lifetime = manifest_entry.get("lifetime", "ephemeral") if manifest_entry else "ephemeral"

    if intent == "input":
        return "keep", "", "input — leave alone", 0.9

    if intent == "log":
        if lifetime == "persistent":
            return "persist", "${SCRATCH}/logs/<project>/<date>/", "log persistence (review path)", 0.7
        return "purge", "", "ephemeral log", 0.85

    if intent == "cache":
        if lifetime == "persistent":
            return "persist", "${SCRATCH}/<project>/cache/", "persistent cache (review path)", 0.65
        return "purge", "", "ephemeral cache", 0.9

    if intent == "script":
        if lifetime == "persistent":
            return "persist", "~/<repo>/scripts/", "script persistence — dedup-check before move", 0.55
        return "purge", "", "one-shot script", 0.85

    if intent == "output":
        if lifetime == "persistent":
            # Try to suggest based on extension
            return "persist", "~/merging/.workspace/notes/  OR  ${SCRATCH}/<project>/", "persistent output (review destination)", 0.7
        # Ephemeral output: keep iff non-trivial size
        if size_bytes > 1_000_000:
            return "persist", "${SCRATCH}/<project>/", "ephemeral output but >1 MB — consider persisting", 0.5
        return "purge", "", "small ephemeral output", 0.7

    return "flag", "", f"unrecognized intent: {intent}", 0.3


# -------------------------------------------------------------------------
# Walk & build plan
# -------------------------------------------------------------------------


@dataclass
class PlanRow:
    path: str
    size_bytes: int
    mtime_iso: str
    category: str
    owner_session: str
    intent: str
    lifetime: str
    recommended_action: str
    destination: str
    confidence: float
    notes: str


def walk_target(target: Path, manifest: dict) -> list[Path]:
    """Yield top-level children of target PLUS any manifest-registered paths
    (which may be nested). Top-level dirs are reported as a unit; nested
    registered items are reported individually so they can be cleaned up
    even when their parent dir contains other (un-owned) files."""
    if not target.exists():
        return []
    result: list[Path] = []
    seen: set[str] = set()
    for p in target.iterdir():
        if p.name in (".tidy_manifest", ".tidy_reports"):
            continue
        sp = str(p)
        if sp not in seen:
            result.append(p)
            seen.add(sp)
    target_resolved = target.resolve()
    for abs_str in manifest:
        p = Path(abs_str)
        sp = str(p)
        if sp in seen:
            continue
        try:
            if not p.resolve().is_relative_to(target_resolved):
                continue
        except (OSError, ValueError):
            continue
        result.append(p)
        seen.add(sp)
    return result


def get_size_bytes(p: Path) -> int:
    if not p.exists():
        return 0
    try:
        if p.is_symlink():
            return 0
        if p.is_file():
            return p.stat().st_size
        if p.is_dir():
            total = 0
            for sub in p.rglob("*"):
                try:
                    if sub.is_file() and not sub.is_symlink():
                        total += sub.stat().st_size
                except OSError:
                    pass
            return total
    except OSError:
        return 0
    return 0


def build_plan(target: Path, session: str, include_recent: bool = False) -> list[PlanRow]:
    manifest = load_manifest(session, target)
    rows: list[PlanRow] = []
    now = dt.datetime.now()

    seen_paths: set[str] = set()

    # Pre-compute "owned children inside dir" for top-level dirs, so we can
    # surface "X owned items inside" on the parent dir's row.
    owned_children: dict[str, int] = {}
    target_resolved = target.resolve()
    for abs_str in manifest:
        p = Path(abs_str)
        try:
            rel = p.resolve().relative_to(target_resolved)
        except (OSError, ValueError):
            continue
        if len(rel.parts) >= 2:
            top_dir = str(target / rel.parts[0])
            owned_children[top_dir] = owned_children.get(top_dir, 0) + 1

    # First, walk the actual filesystem under target.
    for p in walk_target(target, manifest):
        abs_str = str(p)
        seen_paths.add(abs_str)
        try:
            mtime = dt.datetime.fromtimestamp(p.lstat().st_mtime)
        except OSError:
            mtime = now
        age_minutes = (now - mtime).total_seconds() / 60.0
        size = get_size_bytes(p)
        category, notes = categorize(p, target, manifest)
        manifest_entry = manifest.get(abs_str)
        owner = session if manifest_entry else ""
        intent = manifest_entry.get("intent", "") if manifest_entry else ""
        lifetime = manifest_entry.get("lifetime", "") if manifest_entry else ""
        action, dest, action_notes, conf = recommend(category, manifest_entry, size, age_minutes)
        # If this top-level dir contains owned items, append a note (don't change action)
        if abs_str in owned_children and not manifest_entry:
            notes = f"{notes}; contains {owned_children[abs_str]} owned items".lstrip("; ")

        # Recent-window protection
        if action == "purge" and age_minutes < RECENT_MINUTES and not include_recent:
            action = "flag"
            action_notes = f"recently modified ({int(age_minutes)} min) — protected"
            conf = max(conf - 0.2, 0.3)

        rows.append(PlanRow(
            path=abs_str,
            size_bytes=size,
            mtime_iso=mtime.isoformat(timespec="seconds"),
            category=category,
            owner_session=owner,
            intent=intent,
            lifetime=lifetime,
            recommended_action=action,
            destination=dest,
            confidence=round(conf, 2),
            notes="; ".join(x for x in (notes, action_notes) if x),
        ))

    # Manifest entries that didn't match any filesystem path (already moved/deleted)
    for abs_str, entry in manifest.items():
        if abs_str in seen_paths:
            continue
        rows.append(PlanRow(
            path=abs_str,
            size_bytes=0,
            mtime_iso="",
            category=f"agent-authored-{entry.get('intent','unknown')}",
            owner_session=session,
            intent=entry.get("intent", ""),
            lifetime=entry.get("lifetime", ""),
            recommended_action="skip",
            destination="",
            confidence=1.0,
            notes="missing from filesystem (already moved or deleted)",
        ))

    rows.sort(key=lambda r: (-r.size_bytes, r.path))
    return rows


# -------------------------------------------------------------------------
# Output
# -------------------------------------------------------------------------


def write_plan_csv(rows: list[PlanRow], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PLAN_COLS)
        w.writeheader()
        for r in rows:
            w.writerow({k: getattr(r, k) for k in PLAN_COLS})


def fmt_size(n: int) -> str:
    for unit in ("B", "K", "M", "G", "T"):
        if n < 1024:
            return f"{n:>4.0f}{unit}"
        n /= 1024
    return f"{n:.0f}P"


def print_summary(rows: list[PlanRow]) -> None:
    by_cat: dict[str, list[PlanRow]] = {}
    for r in rows:
        by_cat.setdefault(r.category, []).append(r)
    cats_sorted = sorted(by_cat.items(), key=lambda kv: -sum(r.size_bytes for r in kv[1]))
    total_bytes = sum(r.size_bytes for r in rows)
    total_count = len(rows)
    print()
    print(f"# scratch-tidy audit: {total_count} entries, {fmt_size(total_bytes)} total")
    print()
    print("| category | count | size | actions |")
    print("|---|---|---|---|")
    for cat, group in cats_sorted:
        size = sum(r.size_bytes for r in group)
        actions = {}
        for r in group:
            actions[r.recommended_action] = actions.get(r.recommended_action, 0) + 1
        action_str = ", ".join(f"{k}:{v}" for k, v in sorted(actions.items()))
        print(f"| {cat} | {len(group)} | {fmt_size(size)} | {action_str} |")
    print()
    # Top-10 biggest items
    print("## top items by size")
    for r in rows[:10]:
        marker = "[OWN]" if r.owner_session else "[---]"
        print(f"  {marker} {fmt_size(r.size_bytes)} {r.recommended_action:>8}  {r.path} ({r.category})")
    print()


# -------------------------------------------------------------------------
# Apply
# -------------------------------------------------------------------------


def apply_plan(plan_csv: Path, target: Path, include_unowned: bool, include_recent: bool,
               yes: bool, session: str) -> Path:
    """Read plan_csv and execute. Refuses unowned destructive actions unless flag is set."""
    applied_csv = plan_csv.with_name(plan_csv.stem + "_applied.csv")
    actions_log: list[dict] = []

    rows: list[dict] = []
    with plan_csv.open() as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            rows.append(row)

    target_str = str(target.resolve())

    for row in rows:
        path = Path(row["path"])
        action = row["recommended_action"]
        is_own = bool(row.get("owner_session"))

        # Safety: only act on paths under target
        try:
            resolved = path.resolve()
        except Exception:
            resolved = path
        if not str(resolved).startswith(target_str):
            actions_log.append({**row, "applied": "SKIP", "reason": "outside target tree"})
            continue

        if action in ("keep", "skip", "flag"):
            actions_log.append({**row, "applied": "noop", "reason": action})
            continue

        # Unowned destructive: require explicit flag and confirmation
        if not is_own and action in ("purge", "persist") and not include_unowned:
            actions_log.append({**row, "applied": "SKIP", "reason": "unowned, --include-unowned not set"})
            continue

        if action == "purge":
            if not yes:
                resp = input(f"PURGE {row['size_bytes']}B  {path} ? [y/N] ").strip().lower()
                if resp != "y":
                    actions_log.append({**row, "applied": "SKIP", "reason": "user declined"})
                    continue
            try:
                if path.is_symlink() or path.is_file() or is_socket(path):
                    path.unlink(missing_ok=True)
                elif path.is_dir():
                    shutil.rmtree(path, ignore_errors=False)
                actions_log.append({**row, "applied": "PURGED", "reason": ""})
            except Exception as exc:
                actions_log.append({**row, "applied": "ERROR", "reason": str(exc)})
            continue

        if action == "persist":
            dest = row.get("destination", "").strip()
            if not dest or "<" in dest:
                actions_log.append({**row, "applied": "SKIP", "reason": "destination not concrete (review CSV)"})
                continue
            dest_path = Path(os.path.expandvars(os.path.expanduser(dest)))
            if dest_path.is_dir():
                dest_path = dest_path / path.name
            if dest_path.exists():
                ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_path = dest_path.with_name(f"{dest_path.stem}_{ts}{dest_path.suffix}")
            if not yes:
                resp = input(f"PERSIST {path} → {dest_path} ? [y/N] ").strip().lower()
                if resp != "y":
                    actions_log.append({**row, "applied": "SKIP", "reason": "user declined"})
                    continue
            try:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), str(dest_path))
                actions_log.append({**row, "applied": "PERSISTED", "reason": str(dest_path)})
            except Exception as exc:
                actions_log.append({**row, "applied": "ERROR", "reason": str(exc)})
            continue

    # Write applied log
    cols = list(PLAN_COLS) + ["applied", "reason"]
    with applied_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in actions_log:
            w.writerow({k: row.get(k, "") for k in cols})

    # Print summary
    counts: dict[str, int] = {}
    for r in actions_log:
        counts[r["applied"]] = counts.get(r["applied"], 0) + 1
    print(f"applied — log at {applied_csv}")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    return applied_csv


# -------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------


def expand_target(s: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(s))).resolve()


def cmd_audit(args) -> int:
    target = expand_target(args.target)
    if not target.exists():
        print(f"ERROR: target {target} does not exist", file=sys.stderr)
        return 2
    rows = build_plan(target, args.session, include_recent=args.include_recent)
    ts = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    out_csv = target / ".tidy_reports" / f"{args.session}_{ts}.csv"
    write_plan_csv(rows, out_csv)
    print_summary(rows)
    print(f"plan CSV: {out_csv}")
    return 0


def cmd_apply(args) -> int:
    target = expand_target(args.target)
    if args.plan:
        plan_csv = Path(args.plan).expanduser().resolve()
    else:
        # latest report for this session
        reports = sorted((target / ".tidy_reports").glob(f"{args.session}_*.csv"))
        if not reports:
            print("ERROR: no plan CSV found; run audit first or pass --plan", file=sys.stderr)
            return 2
        plan_csv = reports[-1]
    print(f"applying plan: {plan_csv}")
    apply_plan(plan_csv, target,
               include_unowned=args.include_unowned,
               include_recent=args.include_recent,
               yes=args.yes,
               session=args.session)
    return 0


def cmd_list_orphans(args) -> int:
    target = expand_target(args.target)
    md = target / ".tidy_manifest"
    if not md.exists():
        print(f"(no manifest dir at {md})")
        return 0
    threshold = dt.datetime.now() - dt.timedelta(days=args.days)
    print(f"manifests older than {args.days}d under {md}:")
    found = 0
    for p in sorted(md.glob("*.tsv")):
        mtime = dt.datetime.fromtimestamp(p.stat().st_mtime)
        if mtime < threshold:
            print(f"  {mtime.isoformat(timespec='seconds')}  {p}")
            found += 1
    if not found:
        print("  (none)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="tidy.py", description=__doc__)
    p.add_argument("--target", default=DEFAULT_TARGET, help="target tree (default $SCRATCH/tmp)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("audit", help="walk tree, emit plan CSV (dry-run)")
    pa.add_argument("--session", required=True)
    pa.add_argument("--include-recent", action="store_true",
                    help=f"do not protect items modified in the last {RECENT_MINUTES} min")
    pa.set_defaults(func=cmd_audit)

    pp = sub.add_parser("apply", help="execute a plan CSV")
    pp.add_argument("--session", required=True)
    pp.add_argument("--plan", help="explicit plan CSV; default = latest for this session")
    pp.add_argument("--include-unowned", action="store_true",
                    help="allow destructive actions on items not in the manifest")
    pp.add_argument("--include-recent", action="store_true",
                    help=f"do not protect items modified in the last {RECENT_MINUTES} min")
    pp.add_argument("--yes", action="store_true", help="skip per-item confirmation prompts")
    pp.add_argument("--confirm", dest="yes", action="store_true",
                    help="alias for --yes")
    pp.set_defaults(func=cmd_apply)

    po = sub.add_parser("list-orphan-manifests", help="report stale session manifests")
    po.add_argument("--days", type=int, default=30)
    po.set_defaults(func=cmd_list_orphans)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
