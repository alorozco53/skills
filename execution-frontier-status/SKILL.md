---
name: execution-frontier-status
description: >
  Report the state of ongoing research, experiment, engineering, or paper-production work as a stable terminal-readable execution-frontier diagram. Use when the user asks where we are, status, ETA, what is running, what remains, what is blocked, what happens next, or requests an ASCII plan/status diagram; also use at meaningful milestone transitions in long-running work. Recover the prior project structure when available, verify execution state from evidence when tools permit, preserve node names/order across updates, and emphasize the boundary between completed work and the small set of active units gating the deliverable.
---

# Execution Frontier Status

Represent ongoing work as a compact causal project graph whose default human-facing rendering is an ASCII tree.

The user's explicit instructions take precedence over this skill. If the user asks for a different status format, follow that request while preserving the underlying execution-frontier reasoning where useful.

## Core objective

A status update should let the user answer, within seconds:

1. What deliverable or scientific question are we advancing?
2. Which workstreams are genuinely independent?
3. What is happening now?
4. What small set of incomplete units currently gates the result?
5. What becomes actionable automatically or manually after those units finish?

The key concept is the **execution frontier**: the boundary between established upstream evidence and incomplete work that currently advances the deliverable.

## Workflow

1. **Recover the existing project model.**
   - Reuse the most recent status tree or plan from the conversation/repository when one exists.
   - Preserve node names, ordering, and branch meanings unless the actual plan changed.
   - Do not rebuild the diagram from scratch merely because new evidence arrived.

2. **Verify current state before labeling it when tools permit.**
   - Inspect relevant scheduler state, logs, exit states, artifacts, test reports, result counts, or generated outputs.
   - Never infer `[DONE]` only because a process or scheduler job disappeared.
   - Never infer `[RUNNING]` only because work was submitted.
   - Prefer the weaker accurate state when evidence is ambiguous.

3. **Model the work causally, not chronologically.**
   - Root: deliverable, scientific objective, or concrete outcome.
   - Major branch: independent conceptual workstream, intervention, hypothesis, subsystem, or evidence source.
   - Leaf: objectively verifiable experiment, implementation, validation, artifact, or decision point.
   - Edge: containment, decomposition, dependency, or conceptual specialization; not merely "happened after."

4. **Locate the execution frontier.**
   - Identify the smallest currently incomplete units whose completion advances downstream work.
   - Emphasize these over old debugging, resolved failures, obsolete scripts, and distant optional work.
   - Expose the downstream dependencies that are waiting on the frontier.

5. **Render the smallest useful view.**
   - Prefer 2–4 indentation levels.
   - Keep stable completed context only where it makes the active frontier intelligible.
   - For large projects, show a compact macro view plus a focused `Active frontier` view.
   - Keep lines roughly terminal-width friendly, preferably under 90 characters.

6. **Put non-structural information outside the tree.**
   - ETA, scheduler/job IDs, numerical results, commands, artifact paths, stack traces, and methodological interpretation belong in prose/tables/code around the tree rather than inside every node.

7. **End with the implication.**
   - State what the current frontier is and what it gates.
   - Mention the next manual action only if one actually exists; distinguish it from automatic transitions.

## Status vocabulary

Use these labels precisely. Read `references/status-vocabulary.md` when assigning or explaining statuses, especially for scheduler-backed work.

- `[DONE]` — planned work completed and expected artifact exists.
- `[PASSED]` — validation completed successfully.
- `[PARTIAL n/N]` — some independently valid outputs exist; the unit is incomplete.
- `[RUNNING]` — execution is confirmed active.
- `[QUEUED]` — accepted by the scheduler/execution system but not active.
- `[AUTO-NEXT]` — an existing workflow will trigger it automatically.
- `[NEXT]` — planned and ready, but not started/submitted.
- `[WAITING: X]` — cannot start until dependency X completes.
- `[BLOCKED: reason]` — progress requires intervention, information, resources, or a decision.
- `[FAILED: cause]` — terminal failure with a concise known cause.
- `[STALE]` — artifact exists but no longer satisfies the current contract.
- `[DROPPED]` — deliberately removed from scope.
- `[OPTIONAL]` — not required for the principal conclusion/deliverable.

Do not use `[DONE]`, `[PASSED]`, `[RUNNING]`, `[QUEUED]`, `[WAITING]`, and `[BLOCKED]` interchangeably.

## Default response shape

For an ordinary status request, prefer:

```text
<1–4 sentences with current state and ETA if requested>

<ASCII execution-frontier tree>

<1–3 sentences identifying the frontier and downstream implication>

<optional commands, artifacts, or compact numerical results>
```

For a quick request such as "where are we?", compress aggressively:

```text
Outcome
├── established branch ────────────────────────── [DONE]
└── active branch
    ├── validation ─────────────────────────────── [PASSED]
    ├── full evaluation ───────────────────────── [RUNNING]
    └── final plots ───────────────────────────── [WAITING: full evaluation]
```

Then state: `The full evaluation is the current frontier; plotting is downstream of it.`

## Stable-update rule

Repeated status updates should behave like a diff to persistent project state:

```text
previous project graph
        +
new execution evidence
        ↓
minimal status/structure diff
        ↓
updated execution frontier
```

Prefer transitions such as:

```text
[PASSED]  ← [RUNNING]
[RUNNING] ← [NEXT]
[AUTO-NEXT] or [NEXT] ← [WAITING]
```

Do not rename or reorder nodes just to make the new response sound fresh. If the plan itself changed, say so and then update the structure.

## Completed work should fade

Resolved debugging incidents, obsolete scripts, intermediate failures, and fully integrated implementation details should disappear unless they still affect interpretation.

For a mature branch, prefer:

```text
├── Baselines ─────────────────────────────────── [DONE]
```

over repeatedly expanding all completed baseline runs.

## ETA rules

When ETA is requested, distinguish:

- runtime remaining for active work,
- scheduler uncertainty for queued work,
- downstream automatic pipeline time,
- and time until the meaningful deliverable exists.

Never subtract runtime from a queued job as though execution has begun. State uncertainty explicitly when scheduling or runtime variance materially affects the estimate.

## Sweep rules

Use counts when they are more informative than a generic running label:

```text
α sweep ───────────────────────────────────────── [PARTIAL 18/60]
```

Then put execution detail in nearby prose, e.g. `18/60 are cached; the remaining 42 are currently running.`

## Automatic pipeline rules

Expose automatic transitions explicitly so the user does not mistake them for forgotten manual work:

```text
├── α sweep ───────────────────────────────────── [RUNNING]
├── selected-α evaluation ─────────────────────── [AUTO-NEXT]
└── final plots ───────────────────────────────── [WAITING: selected-α evaluation]
```

## Anti-patterns

Avoid:

- flat todo lists that erase workstream/dependency structure;
- chronological diaries of every command and debugging event;
- script/repository names as the conceptual project hierarchy;
- false completion inferred from missing processes;
- huge trees containing every conceivable future experiment;
- constant tree restructuring between updates;
- decorative ASCII whose branches do not encode dependency or conceptual decomposition.

If prose or a small table is clearer than a tree, use it. The execution-frontier model is mandatory; the ASCII rendering is only the default.

## References

- Read `references/status-vocabulary.md` for exact status semantics and evidence rules.
- Read `references/templates-and-examples.md` when a concrete research, software, paper, macro/active, or ETA example would help construct the update.
