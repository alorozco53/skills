# Status Vocabulary and Evidence Rules

Use status labels as execution semantics, not decoration.

## Canonical labels

| Label | Meaning | Evidence expectation |
|---|---|---|
| `[DONE]` | Planned work completed; expected artifact exists | Exit state and/or terminal artifact/result verified |
| `[PASSED]` | Validation/test completed successfully | Explicit test/validation success |
| `[PARTIAL n/N]` | Independently valid subset exists; unit incomplete | Count derived from artifacts/results, not expectation |
| `[RUNNING]` | Work is actively executing | Scheduler/process/log confirms current execution |
| `[QUEUED]` | Accepted but not executing | Scheduler/execution system shows pending/queued state |
| `[AUTO-NEXT]` | Existing workflow will launch it automatically | Pipeline/parent job dependency is already configured |
| `[NEXT]` | Planned and ready but not started/submitted | No unmet dependency; manual start remains |
| `[WAITING: X]` | Cannot start until X completes | Real dependency, not merely preferred chronology |
| `[BLOCKED: reason]` | Requires intervention/decision/information/resource | Agent/user action is necessary before progress |
| `[FAILED: cause]` | Terminal unsuccessful execution | Failure state verified; concise cause known |
| `[STALE]` | Artifact exists but violates current contract | Contract/config changed or artifact invalidated |
| `[DROPPED]` | Deliberately removed from scope | Explicit replanning decision |
| `[OPTIONAL]` | Not necessary for principal conclusion/deliverable | Scope semantics make it non-gating |

## Distinctions that matter

- `[DONE]` is completion; `[PASSED]` is successful validation.
- `[QUEUED]` is scheduler state; `[WAITING]` is dependency state.
- `[BLOCKED]` means something must intervene; `[WAITING]` can resolve without intervention.
- `[AUTO-NEXT]` means the launch path already exists; `[NEXT]` means a manual action remains.
- `[PARTIAL n/N]` describes valid output coverage and may be more informative than `[RUNNING]` for sweeps.

## Scheduler-backed work

Never call a job `[DONE]` because it disappeared from a live queue. Verify with the strongest available source, such as:

1. scheduler terminal state (`COMPLETED`, exit code, etc.);
2. terminal log line expected from successful execution;
3. expected output artifact(s);
4. expected result count/aggregation;
5. downstream validation that consumes the artifact successfully.

Likewise, submission alone does not justify `[RUNNING]`; use `[QUEUED]` until active execution is confirmed.

## Evidence uncertainty

When evidence conflicts or is incomplete:

- report the weaker accurate state;
- mention the uncertainty outside the tree if it affects interpretation;
- do not invent a hybrid status merely to sound precise.

Example:

```text
full evaluation ───────────────────────────────── [QUEUED]
```

with prose: `Submitted successfully, but the scheduler has not started it yet.`

## Dependency wording

Prefer a concrete dependency:

```text
plots ─────────────────────────────────────────── [WAITING: full evaluation]
```

over a vague label:

```text
plots ─────────────────────────────────────────── [WAITING]
```

when the dependency is known and remains readable.
