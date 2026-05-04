---
name: method-replayer
description: Create interactive replay notebooks that unwrap a Python entrypoint, method, or evaluation pipeline into a user-runnable, inspection-first notebook with explicit assumptions, source-code links, and stepwise checkpoints. Use when Codex should help an experienced user reproduce, audit, or trace a result manually in Jupyter rather than running the whole workflow itself, especially for ML training and evaluation pipelines, result mismatches, merge or reconstruction flows, or codepath debugging.
---

# Method Replayer

## Overview

Author notebooks that explain and replay a method, not opaque automation. Optimize for user-controlled execution, transparent assumptions, and code-aligned cells.

## Start Interactively

- Ask a concise clarification when any of these is ambiguous:
  - the source entrypoint or method to unwrap
  - the exact result, number, or behavior to reproduce
  - whether the notebook is primarily a replay or an audit
  - the intended stopping point: config replay, graph build, AE forward, merge, reconstruction, final eval, or another boundary
- Prefer one compact question with a proposed default over a long questionnaire.
- If the user already provided a representative notebook, treat it as the style anchor unless they ask to change the structure.

## Inspect The Codepath First

- Read the entrypoint and its immediate callees before authoring cells.
- Identify:
  - runtime config inheritance
  - branching logic
  - helper functions that materially change behavior
  - checkpoint, artifact, and path resolution
  - places where the notebook may intentionally diverge for memory or speed reasons
- Separate:
  - values copied directly from source code or run metadata
  - values derived inside the notebook
  - unresolved assumptions that should be surfaced to the user

## Shape The Notebook As A Linear Replay

- Structure the notebook so each section answers one concrete question.
- Default section order:
  - title and reproduction target
  - scope, stop point, and success criterion
  - imports and top-level config cell
  - artifact and config resolution
  - source-code map
  - stepwise replay cells aligned to source functions
  - mismatch checks and invariants
  - optional full evaluation or expensive cell at the end
- Add a markdown cell before each substantial code cell explaining:
  - what the cell is checking or reconstructing
  - which source file or function it mirrors
  - what output or invariant should hold
- At the start of each replay section, include a concrete CLI reproducer when
  the source path has a runnable command-line entrypoint. The command should be
  copy-runnable, include environment setup when relevant, and use section-specific
  flags rather than a vague "run the script" placeholder.

Read [references/notebook-outline.md](references/notebook-outline.md) when you need a concrete section template.

## Keep Execution User-Owned

- Default to writing cells the user can run incrementally.
- Do not run heavy notebook cells unless the user explicitly asks for execution.
- Isolate expensive or destructive steps behind clearly labeled cells.
- Prefer explicit prints, assertions, and summaries over hidden state.
- Put user-editable knobs in one configuration cell near the top.
- Free memory explicitly when the traced flow is known to be heavy.
- Mark notebook-only deviations clearly instead of silently "improving" the source flow.

## Link Back To Real Code

- Add markdown references to the actual repository files.
- Prefer repo-relative links from the notebook directory.
- Mention exact function or class names in prose even when links are present.
- Use line anchors only when the target renderer is known to support them reliably.
- When several helpers matter, list them explicitly instead of writing vague prose like "same as the eval script."

Read [references/naming-and-linking.md](references/naming-and-linking.md) for concrete naming and linking conventions.

## Name The Notebook Precisely

- Prefer `<entrypoint>_<focus>_replay.ipynb`.
- If the notebook is mainly discrepancy hunting rather than replay, use `<entrypoint>_<focus>_audit.ipynb`.
- Include model family, variant, or scope only when it materially disambiguates the notebook.
- Avoid vague names like `_trace`, `_debug`, `_tmp`, or `_final2`.

## Good Notebook Content

- Make the call chain visible in markdown before reimplementing it in cells.
- Put the command-line reproducer next to the replay section it corresponds to,
  not only in a global setup cell, so users can jump from notebook replay to the
  canonical script path without hunting.
- Capture exact values when mirroring WandB config, saved args, or runtime overrides.
- Add stop points after major boundaries so the user can inspect before continuing.
- Use small comparison cells between major compute cells when reproducing a mismatch.
- Prefer explicit tables or bullet summaries for "notebook vs source" differences.

## Deliverable Standard

The notebook should let the user:

- understand how the source path reaches the target method
- inspect each major intermediate
- reproduce the chosen segment with minimal hidden assumptions
- see exactly where the notebook intentionally diverges from the source implementation
