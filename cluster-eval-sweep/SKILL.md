---
name: cluster-eval-sweep
description: Set up an on-demand notification flow for SLURM eval sweeps so completed jobs surface at the next user prompt without agents polling. Use when the user is about to launch >2 GPU eval jobs that span allocations or take >30 min, when an aggregator must fire only after the last sentinel lands, or when they're tired of agents that "watch" jobs and burn tokens re-loading context every wakeup.
---

# Cluster Eval Sweep

## Overview

A cluster eval sweep is a multi-job set of SLURM evaluations whose individual
jobs may outlive the conversation that launched them, span more than one
allocation barrier, or run long enough that an agent should not babysit them.

This skill packages the canonical *on-demand inversion of control* pattern for
that situation: the SLURM jobs themselves write a sentinel file when they exit,
a Stop-hook scans for new sentinels at conversation idle, and the next user
prompt receives a `<system-reminder>` describing what landed since the agent
last spoke. There is no agent-side polling of `squeue`, no periodic wakeup,
and no `--poll` opt-out.

The skill produces three artifacts:

1. a sentinel-writing trailer added to the user's eval sbatch script,
2. a Stop-hook configuration snippet for `~/.claude/settings.json` (delegate to
   `update-config` for the actual install),
3. an aggregator-trigger rule that fires once when the final expected sentinel
   appears.

## When to use

- The user is about to launch > 2 GPU eval jobs.
- The sweep crosses allocation barriers (e.g. multiple `short-unkillable`
  slots, a mix of `short-unkillable` + `long-cpu`, a job that gets requeued).
- Any single eval job is expected to take > 30 min.
- An aggregator (notebook, table-builder, plot script) should run *exactly
  once* after the last job lands, not repeatedly.
- The user wants to walk away and learn about completion the next time they
  type, without an agent checking on jobs in the background.
- The user has explicitly killed a polling-style watcher and wants a
  notification-style replacement.

## When NOT to use

- One-shot: a single eval job, run interactively. Just `srun` it or watch the
  log; the skill is overkill.
- Synchronous parallel runner inside one allocation where the parent shell
  already waits on `pids` (e.g. `run_qwen_baselines_parallel.sh`). The shell
  itself is the sentinel; sentinels add nothing. Add this skill on top *only*
  when the runner's allocation can die before all jobs finish (the canonical
  motivating case: a 4-way batch where the slot expires mid-batch).
- Quick iterative debugging where the next agent action depends on the
  immediate run output. Use a foreground job for that.

## Decision rule

Cheap one-shot or fully-supervised: ad hoc.
Multi-job sweep across allocation barriers, or any job whose runtime exceeds
the user's likely conversation length: this skill.

State the chosen mode (`ad-hoc` or `cluster-eval-sweep`) explicitly when
recommending an eval launch plan.

## Inputs

The skill accepts one of:

- An **eval declaration list** — one entry per job, each carrying:
  - `model_dir` (or HF ref) — what to evaluate.
  - `model_label` — short slug, used in sentinel filenames and surfaced in
    the notification.
  - `output_path` — lm_eval / runner output dir, used to detect resume.
  - `eval_args` — per-job CLI overrides (tasks, limits, GPU id, etc.).
- An **existing eval-runner script path** plus the *topic* name. The skill
  then wraps the script's per-job invocation with a sentinel trailer rather
  than rewriting it.

Required regardless of input form:

- `topic` — short kebab-case label (e.g. `qwen-merge-eval`,
  `vit-l14-task-arith`). Used as the sentinel directory name and in the
  notification header. Must be unique to this sweep.
- `expected_count` — total jobs the sweep will produce. The aggregator
  fires only when sentinel count reaches this number (or all are accounted
  for as failed, see *Quality bars*).

Optional:

- `aggregator_cmd` — command line to run when the last sentinel lands.
  When omitted, the skill surfaces "all sentinels in" but does not auto-run
  anything; the user decides whether to invoke their notebook / aggregator.

## Output template — what the skill generates and where

### 1. Sentinel directory

```text
$SCRATCH/logs/<topic>-done/
```

One JSON file per job is written here on job exit. Filename:
`<job_id>.json`. Contents:

```json
{
  "job_id": "<SLURM_JOB_ID or pid for non-SLURM>",
  "topic": "<topic>",
  "model_label": "<label>",
  "status": "done | failed",
  "exit_code": <int>,
  "output_dir": "<absolute path>",
  "started_at": "<ISO-8601 with TZ>",
  "completed_at": "<ISO-8601 with TZ>",
  "host": "<hostname>",
  "elapsed_seconds": <int>,
  "log_path": "<path to per-job stdout/stderr if known>"
}
```

The skill must never write a sentinel mid-job. Sentinels are an *exit*
signal; partial sentinels would corrupt the all-in detection rule below.

### 2. Sbatch trailer

The skill appends (or splices, if a `# --- cluster-eval-sweep trailer ---`
marker exists) a `trap` at the top of the user's eval job script and a
`completed_at` writer at the bottom:

```bash
# --- cluster-eval-sweep trailer ---
CES_TOPIC="<topic>"
CES_DONE_DIR="${SCRATCH}/logs/${CES_TOPIC}-done"
CES_JOB_ID="${SLURM_JOB_ID:-manual-$$-$(date +%s)}"
CES_MODEL_LABEL="${MODEL_LABEL:-unknown}"
CES_OUTPUT_DIR="${OUTPUT_PATH:-unknown}"
CES_STARTED_AT="$(date -Iseconds)"
mkdir -p "$CES_DONE_DIR"

_ces_emit_sentinel() {
    local rc=$?
    local status="done"
    [[ "$rc" -ne 0 ]] && status="failed"
    cat > "$CES_DONE_DIR/${CES_JOB_ID}.json" <<EOF
{
  "job_id": "${CES_JOB_ID}",
  "topic": "${CES_TOPIC}",
  "model_label": "${CES_MODEL_LABEL}",
  "status": "${status}",
  "exit_code": ${rc},
  "output_dir": "${CES_OUTPUT_DIR}",
  "started_at": "${CES_STARTED_AT}",
  "completed_at": "$(date -Iseconds)",
  "host": "$(hostname)",
  "elapsed_seconds": $(( $(date +%s) - $(date -d "${CES_STARTED_AT}" +%s) )),
  "log_path": "${SLURM_SUBMIT_DIR:-$PWD}/logs/${CES_TOPIC}_${CES_JOB_ID}.out"
}
EOF
}
trap _ces_emit_sentinel EXIT
# --- end cluster-eval-sweep trailer ---
```

The trailer must be safe to source under `set -euo pipefail` (the user's
eval scripts use it) and must not change the script's exit code.

### 3. Stop-hook configuration snippet

Generated as a JSON fragment to be merged into `~/.claude/settings.json`
under `hooks.Stop`. The snippet runs at conversation idle and surfaces
*new* sentinels (mtime > last-seen marker) as a `<system-reminder>` block.

State to track between hook invocations:

- `$SCRATCH/logs/<topic>-done/.last_seen` — touch-file holding the highest
  mtime processed. The hook updates it after emitting reminders.

The skill *does not* write `~/.claude/settings.json` directly. It produces
the snippet and instructs the user to install it via the `update-config`
skill. **TODO for the user:** decide whether `cluster-eval-sweep` should
auto-invoke `update-config` on first run; the cross-skill handoff deserves
explicit eyes before being silent.

### 4. Aggregator trigger

The Stop-hook also counts `*.json` files in the topic's done-dir. When the
count reaches `expected_count` (or all remaining unfinished jobs are
flagged failed), and `aggregator_cmd` was supplied, the hook appends a
single `<system-reminder>` saying "all <N> sentinels in — running
aggregator: `<cmd>`" and runs the command in the foreground from the hook.

The aggregator must be **idempotent**. The skill enforces this by writing a
`.aggregator_fired` marker after the first run and refusing to re-run for
the same `topic`. To re-aggregate, the user deletes the marker.

## Skeleton — minimal invocation

```text
/cluster-eval-sweep \
    --topic qwen-merge-eval \
    --expected-count 12 \
    --eval-script ~/merging/nino-autoenc/job-script-qwen-eval.sh \
    --aggregator "ninoenv && python ~/merging/nino-autoenc/analysis/qwen_results/aggregate_results.py"
```

What the skill does on this invocation:

1. Verify `$SCRATCH/logs/<topic>-done/` does not already contain stale
   sentinels from a previous sweep with the same topic. If it does, prompt
   the user to choose `--rotate` (move old sentinels aside) or pick a new
   topic name.
2. Splice the sentinel trailer into the eval script (idempotent: the marker
   line guards re-application).
3. Emit the Stop-hook JSON snippet to stdout and instruct the user how to
   install it.
4. Print a one-line summary: topic, sentinel dir, expected count,
   aggregator path (or `(none)`).

## Default behavior

- On-demand only. The skill exposes no `--poll`, no `--watch`, no `--every`.
  Polling-based variants are explicitly out of scope; suggesting them is a
  failure mode.
- `expected_count` is mandatory. Without it, the aggregator-trigger rule
  cannot fire and the skill degrades to a notification-only mode that the
  user almost certainly did not want; ask for it.
- The aggregator runs inside the Stop-hook, blocking the next user turn
  while it runs. Aggregators must be fast (< ~30s typical). For longer
  aggregators, the skill instead emits a `<system-reminder>` saying "ready
  to aggregate, run `<cmd>`" and lets the user trigger it on the next turn.
  This threshold is a heuristic; surface it in the report so the user can
  override.
- Sentinels are namespaced by `topic`. Two concurrent sweeps with different
  topics can coexist; they have separate done-dirs and separate
  `.last_seen` markers.

## Quality bars

- **Every job writes a sentinel.** The trailer uses `trap ... EXIT`, so
  even crashed or signal-killed jobs produce a `failed` sentinel as long as
  the shell got far enough to install the trap.
- **Missing sentinels are real signal, not noise.** A SLURM job whose
  `EXIT` trap never ran (OOM kill before the trap installed, walltime cut
  exactly at exit, node reboot) is a job that died unrecoverably. The
  Stop-hook surfaces the gap explicitly: "expected 12, observed 11; missing
  ids: [<job_id>]". Do not silently retry or paper over.
- **The Stop-hook never re-processes old sentinels.** It compares mtime
  against `.last_seen` and updates `.last_seen` only after the
  notification is composed. A hook crash mid-write would re-emit, which
  is acceptable; double-emission is preferable to silent loss.
- **The aggregator fires once.** The `.aggregator_fired` marker is a hard
  guard. Re-aggregation is a deliberate, user-driven action.
- **Sentinel content is enough to write a status table.** A reader of the
  done-dir, with no other context, can produce the "Final progress" table
  the user keeps in mission logs.

## Failure modes to avoid

- **Mid-job sentinels.** Any sentinel that is not written from an `EXIT`
  trap is a bug. Progress logs go in the per-job stdout, not in a sentinel.
- **Re-introducing polling.** No `--poll`, no agent-side `squeue` loops, no
  `loop` skill scheduled in the background to "check the eval". The whole
  point of this skill is the *absence* of those.
- **Topic collisions.** Two sweeps that share a `topic` will mix their
  sentinels and fire the aggregator at the wrong moment. Refuse to set up
  a sweep whose done-dir already has sentinels unless the user explicitly
  rotates.
- **Aggregator that depends on freshly-imported state from a kernel.**
  The aggregator runs from a Stop-hook subshell, not the user's notebook
  kernel. If the canonical aggregation lives in a notebook, the skill
  should point at a headless `aggregate_results.py` mirror, not at the
  notebook. (See `nino-autoenc/analysis/qwen_results/aggregate_results.py`
  for the pattern.)
- **Writing sentinels under `/tmp`.** Forbidden by project rules. Always
  `$SCRATCH/logs/<topic>-done/`.
- **Hidden behavior.** The skill must print, in its report, the exact
  sentinel dir, the exact Stop-hook snippet, and the exact aggregator
  command. The user reading the report should be able to reconstruct the
  notification flow without re-invoking the skill.

## Pointers

- The motivating sweep:
  `<workspace>/.workspace/notes/QWEN_BASELINES_AND_TA_2026-05-04.md`
  (Final progress table + Bugs hit and fixed sections — what an
  on-demand notification flow would have caught earlier).
- `update-config` skill — owns `~/.claude/settings.json` mutations,
  including hook installs. This skill produces the snippet; that skill
  installs it.
- `mission-log` skill — the natural sibling. A long sweep typically has
  both: a mission log to capture decisions and a `cluster-eval-sweep`
  setup to capture completion events.
