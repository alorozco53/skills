---
name: scratch-tidy
description: End-of-task cleanup routine for an agent's own work in a scratch tmp tree (default $SCRATCH/tmp). Categorizes everything in the tree, attributes each item to its origin, and for items the calling agent owns, decides keep / persist / purge — never auto-deletes items it does not own (only flags them). Use right before handoff or session shutdown to leave the tmp tree tidier than you found it.
---

# scratch-tidy

## What this skill does

Walks a scratch tmp tree (default `$SCRATCH/tmp`) and produces a *tidy plan*:
1. **Categorize** every path (system socket, wandb tmp, torch compile cache, agent-authored output, experiment scratch, unknown, …).
2. **Attribute** each path to its likely origin via a per-session **manifest** that the agent maintains during work, plus mtime/path heuristics.
3. **Decide**, *only for items the calling agent created in this session*: `keep` | `persist <to-path>` | `purge`.
4. **Flag** everything else with category, size, age, and likely owner — so the human can act on it later. Never auto-delete non-own items unless `--include-unowned` is set.

This skill is **agent-self-cleanup**: scoped to one agent, one session. It is not a multi-agent reconciler.

## When to invoke

- Right before handing off a task to another agent (so the next agent finds a clean tree).
- At the end of a long-running session that created intermediate caches, scripts, or logs.
- After a diagnostic / one-shot run that wrote scratch artifacts the agent does not need to keep.
- Whenever the user asks "clean up after yourself" or "what's left in tmp from your work."

## When NOT to invoke

- Mid-task — registration is fine mid-task, but `apply` should run only at the end.
- When another agent is actively reading from `$SCRATCH/tmp/<dir>/` (verify by checking the manifest reports of other recent sessions and by asking the user if unsure).
- For sweeping non-own legacy clutter: this skill flags it but does not delete it. Use a separate dedicated cleanup pass for that, with explicit user approval.

## The two phases of the routine

### Phase 1 — Register as you go (during the task)

Whenever the agent creates a scratch path it intends to manage, it appends a row to its session manifest:

```bash
$SCRATCH_TIDY_SESSION="<short-stable-id>"  # set once at session start, e.g. "diag-math-pair-2026-05-06-1346"
~/.codex/skills/scratch-tidy/bin/register.sh "<path>" "<intent>" "<lifetime>"
```

- `<intent>` ∈ `cache | output | script | log | input`
- `<lifetime>` ∈ `ephemeral | persistent`

Manifest path: `$SCRATCH/tmp/.tidy_manifest/<session>.tsv`.

The agent should register paths even when they look small or obvious. Registration is a two-byte append; the cost is negligible and the value at end-of-task is high.

### Phase 2 — Audit, decide, execute (at end of task)

```bash
# 1. Audit (dry run, default). Writes a plan CSV + prints summary.
~/.codex/skills/scratch-tidy/bin/tidy.py audit --session "$SCRATCH_TIDY_SESSION"

# 2. Edit the plan if needed (the CSV is just a file).

# 3. Apply.
~/.codex/skills/scratch-tidy/bin/tidy.py apply --session "$SCRATCH_TIDY_SESSION" --plan <path-to-csv>
```

Or, in a single shot with confirmation:
```bash
~/.codex/skills/scratch-tidy/bin/tidy.py apply --session "$SCRATCH_TIDY_SESSION" --confirm
```

## Category taxonomy

The audit emits one of these categories per path. Short list (the script's heuristics map onto these names exactly):

| category                     | matches                                                                  | default action     |
|------------------------------|--------------------------------------------------------------------------|--------------------|
| `system-socket`              | unix sockets (`stat` reports socket type)                                | auto-purge         |
| `hf-lock`                    | `*.lock` files matching HuggingFace download-lock naming                 | auto-purge         |
| `torch-compile-cache`        | `optim.gnn_*.py`, `torchinductor_*`, `*-pycache-*` dirs                  | auto-purge if >7d  |
| `python-bytecode-cache`      | `__pycache__/`, `pip-cache/`, `pptxdeps/`                                | flag (skip)        |
| `wandb-tmp`                  | `tmp*wandb-*`, `wandb-<digits>-…`, `tmp*.ptx`, anonymous `tmp[a-z0-9]+`  | auto-purge if >3d  |
| `agent-authored-output`      | manifest entry with intent=output                                        | own — decide       |
| `agent-authored-cache`       | manifest entry with intent=cache                                         | own — decide       |
| `agent-authored-script`      | manifest entry with intent=script                                        | own — decide       |
| `agent-authored-log`         | manifest entry with intent=log                                           | own — decide       |
| `experiment-scratch-dir`     | top-level dir matching known experiment patterns (vision_*, qwen-*, …)  | flag (not own)     |
| `env-dump`                   | text files like `*_env_names.txt`, `req*.txt`, `*_pip_list.txt`         | flag (not own)     |
| `unknown`                    | everything else                                                          | flag               |

If the heuristic for category X says "auto-purge" but the manifest claims the path with intent=persistent, **the manifest wins**.

## Decision rubric for own items

Combine `intent × lifetime` into a recommended action:

| intent  | lifetime    | recommended action                                                     |
|---------|-------------|------------------------------------------------------------------------|
| output  | persistent  | persist → `~/merging/.workspace/notes/` (md/csv) or `$SCRATCH/<project>/` |
| output  | ephemeral   | persist if size > 1 MB and not derivable, else purge                   |
| cache   | ephemeral   | purge                                                                  |
| cache   | persistent  | persist → `$SCRATCH/<project>/cache/`                                  |
| script  | persistent  | persist → `~/merging/<project>/scripts/` (after dedup-check)           |
| script  | ephemeral   | purge                                                                  |
| log     | *           | persist → `$SCRATCH/logs/<project>/<date>/` if useful, else purge      |
| input   | *           | keep — likely shared input, do not move or delete                      |

These are *recommendations*. The agent should override per item when the recommendation does not fit. Always print *why* an item gets a non-default action.

## Safety rails

- **Dry-run by default.** `audit` never deletes or moves anything.
- **No silent deletion of unowned paths.** The `apply` command refuses to delete items not in the manifest unless `--include-unowned` is passed AND the user has explicitly approved each non-own destructive action.
- **Auto-purge whitelist** (no per-item approval needed even with `--apply`):
  - `system-socket` (always — these are dead Unix sockets)
  - `hf-lock` (always)
  - `torch-compile-cache` older than 7 days
  - `wandb-tmp` older than 3 days
  Anything outside this whitelist requires either (a) being on the manifest with a `purge` decision, or (b) explicit `--include-unowned` + per-item approval.
- **Bulk operations get a confirmation prompt** unless `--yes` is set.
- **Never delete anything modified in the last 60 minutes**, regardless of category or manifest. Exception: explicit `--include-recent` flag from the user.
- **Manifest sessions older than 30 days** are reported by `list-orphan-manifests` but not auto-cleaned.

## Outputs

Every audit/apply run writes an audit CSV at:
`$SCRATCH/tmp/.tidy_reports/<session>_<YYYYMMDDHHMMSS>.csv`

Columns: `path | size_bytes | mtime_iso | category | owner_session | intent | lifetime | recommended_action | destination | confidence | notes`.

Plus a short markdown summary printed to stdout, grouped by category, sorted by size (largest first).

`apply` writes a sibling `<session>_<timestamp>_applied.csv` with the actual actions taken (and skipped, with reason).

## Failure modes to expect and handle

- **Manifest missing entries for paths you actually created.** Heuristics fall back. The CSV will mark them `confidence=low` so you can spot-check.
- **Two sessions wrote to the same path.** Last writer wins in the manifest. The audit CSV has both rows; the agent picks one.
- **Path was renamed/moved after registration.** The original path won't exist; mark as `missing` and skip in `apply`.
- **Persist destination already exists.** Refuse to overwrite. Append a timestamp suffix, or ask.

## Example session flow

```bash
# session start
export SCRATCH_TIDY_SESSION="diag-math-pair-$(date +%Y%m%d-%H%M%S)"
REG=~/.codex/skills/scratch-tidy/bin/register.sh

# during the work
$REG "$SCRATCH/tmp/qwen_paper_tables/_diag_math_pair_collapse.py"     script  ephemeral
$REG "$SCRATCH/tmp/qwen_paper_tables/_tvcache"                        cache   ephemeral
$REG "$SCRATCH/tmp/qwen_paper_tables/diag_run3.log"                   log     ephemeral
$REG "$SCRATCH/tmp/qwen_paper_tables/math_pair_collapse_diagnostics.csv"  output persistent
$REG "$SCRATCH/tmp/qwen_paper_tables/math_pair_collapse_findings.md"      output persistent

# end of task
~/.codex/skills/scratch-tidy/bin/tidy.py audit --session "$SCRATCH_TIDY_SESSION"
# review the CSV; persist outputs to .workspace/notes if appropriate; purge ephemerals
~/.codex/skills/scratch-tidy/bin/tidy.py apply --session "$SCRATCH_TIDY_SESSION" --confirm
```

## Implementation files

- `bin/register.sh` — manifest appender (one-line append; safe to call repeatedly with the same path).
- `bin/tidy.py` — audit + apply driver. Pure stdlib Python (no heavy deps).

Both are intentionally small. The skill's value is in the categorization, attribution, and decision policy above — the scripts are mechanical.
