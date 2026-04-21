---
name: interactive-tester
description: Turn vague testing requests into explicit, layered testing scopes and execution plans. Use when Codex needs to choose, negotiate, run, or review the right level of testing for code changes, ML pipelines, SLURM jobs, checkpoints, evaluation outputs, or research workflows. Trigger for requests about test strategy, what to run, how much to run, safety before merge, unit vs integration vs end-to-end decisions, artifact validation, reproducibility, or Mila-cluster-aware GPU testing.
---

# Interactive Tester

## Overview

Separate software correctness from research validation. Negotiate scope before expensive runs, choose the cheapest informative layer first, then report exactly what was and was not validated.

## Start the Interaction

- Classify the user request before running anything:
  - logic regression
  - codepath wiring
  - artifact or workflow integrity
  - benchmark or research claim
  - reproducibility or seed stability
- Ask a concise scope question when cost or risk materially changes with the chosen layer.
- Prefer one compact question over a long questionnaire.
- If the user is vague, propose a default scope instead of asking open-ended questions.

Use a compact framing like:

```text
I can keep this to unit plus component checks, or include a short GPU contract check as well. My default is unit plus component, and I add contract checks only if the change touches checkpoints, resume logic, evaluation outputs, or job wrappers.
```

## Use the Layer Model

- `unit`
  - Protect semantics, parser behavior, naming, loss math, aggregation rules, and helper invariants.
  - Use synthetic inputs, mocks, and tiny tensors.
  - Keep CPU-first and fast.
- `component`
  - Exercise a real codepath with tiny scale.
  - Use tiny models, tiny graphs, or minimal fixtures.
  - Check forward paths, reconstruction paths, merge paths, and adapter wiring.
- `contract`
  - Validate workflow and artifact integrity on short real runs.
  - Inspect checkpoint contents, metadata, run IDs, resume behavior, output schemas, and directory layout.
  - Treat artifact contracts as correctness, not as optional bookkeeping.
- `validation`
  - Run research-facing evaluation, benchmark, ablation, or paper-style workflows.
  - Use canonical repo entrypoints when they exist.
  - Keep this separate from ordinary software tests.
- `reproducibility`
  - Repeat seeded runs and compare within tolerances.
  - Record environment, hardware, seeds, and any nondeterministic caveats.

## Pick the Right Layer

- Choose `unit` for parser changes, save-path naming, loss functions, namespace parsing, or narrowly scoped logic fixes.
- Choose `component` for real forward paths, graph construction, model-family adapters, or light end-to-end codepath checks.
- Choose `contract` for checkpointing, automatic resume, evaluation result serialization, run metadata, job scripts, or workflow wrappers.
- Choose `validation` for benchmark numbers, figure reproduction, baseline generation, ablations, lambda search, or cross-method comparison.
- Choose `reproducibility` when the user cares about seed sensitivity, variance, or repeatability claims.
- Combine layers from cheapest to most informative.
- Stop upgrading scope automatically once the current layer answers the user request with acceptable confidence.

## Prefer Canonical Entrypoints

- Look for repo-published front doors before inventing ad hoc commands.
- Respect explicit workflow indexes, validation scripts, and job wrappers.
- Distinguish `canonical`, `advanced`, and `legacy` paths when the repo does.
- Avoid calling a paper reproduction flow a “test” unless the repo explicitly treats it as validation.

## Mila Cluster Policy

- Treat login nodes as control planes, not execution targets for heavy work.
- Use the project’s canonical Python environment and module stack when the repo defines one.
- Prefer `short-unkillable` for short GPU smoke tests, contract checks, and debugging runs on Mila.
- Escalate to longer partitions only when runtime or scale actually requires it.
- Request the smallest realistic walltime and resource set.
- Keep scheduler-friendly durations rather than vague oversized requests.
- Use `$SLURM_TMPDIR` for per-job scratch when available.
- Use `$SCRATCH` for persistent outputs, logs, checkpoints, and artifacts.
- Surface partition choice, walltime, GPU count, and output paths in the report for any SLURM-backed run.

## Execute in the Right Order

- Read existing tests and validation docs first.
- Run the narrowest cheap checks that can falsify the change.
- Reuse existing contract or validation entrypoints when available.
- Inspect produced artifacts, not just process exit codes.
- Capture exact commands, seeds, checkpoint sources, output locations, and any skips.
- Re-negotiate with the user if the required scope expands beyond the original budget.

## Report with Explicit Boundaries

- State the requested objective.
- State the chosen layer or layers and why.
- State what was run.
- State what was not run.
- Distinguish:
  - `passed`
  - `failed`
  - `not run`
  - `blocked by prerequisites`
- Call out residual risk when only lower layers ran.
- Recommend the next higher layer only when it would materially reduce uncertainty.

## Avoid These Failure Modes

- Avoid conflating unit tests with research validation.
- Avoid reporting success when a job only launched but artifacts were not inspected.
- Avoid expensive GPU validation without aligning on scope.
- Avoid hiding missing checkpoints, missing datasets, skipped tasks, or nondeterminism.
- Avoid assuming bitwise reproducibility unless the stack actually enforces it.
- Avoid writing a “global test strategy” that ignores repo-specific canonical workflows.

## Default Behavior

- Default to `unit` plus `component` for ordinary code changes.
- Add `contract` when the change touches checkpoints, resume logic, eval outputs, CLI runners, or SLURM wrappers.
- Add `validation` only when the user asks for metric confidence, research confirmation, figure reproduction, or benchmark-level assurance.
- Add `reproducibility` only when repeatability is part of the claim.
