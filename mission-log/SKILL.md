---
name: mission-log
description: Bootstrap or update a date-stamped mission-log doc that captures a multi-day, often cross-repo push. Use when the user wants to write down what's being done, what's decided, what's stuck, and what's next — especially mid-stream after work has already started. Default behavior is to introspect the current conversation and pre-populate goal, decisions on file, repos touched, status board, and bug/fix entries; falls back to a blank skeleton with --blank.
---

# Mission Log

## Overview

A mission log is a single markdown file that tracks one cohesive push of work — usually multi-step, often touching more than one repo, almost always longer-lived than a single conversation. It is *not* a code reference, *not* a PR description, and *not* a tutorial. It is the document a future-you (or a teammate agent) reads to understand what we're doing, what we already decided, and what's left.

This skill creates or updates that file.

## When to use

- Mid-stream: "we've been at this a while, time to write it down."
- At the start of a multi-day push, to anchor the goal and decisions.
- Right after a refactor or methodology change, to capture *why* before the reasoning rots.
- When handing off to a teammate agent.

## When NOT to use

- Single-shot edits or one-conversation tasks. The diff and commit message are enough.
- Code-anchored references (an entrypoint description, a CLI guide, a gotcha doc tied to one file). Those go in `<repo>/docs/`, not in a mission log.
- General project documentation. That's a different artifact.

## Location decision rule

Count the repos touched by the work being logged:

- **More than one repo** → `<workspace>/.workspace/notes/<TOPIC>_<YYYY-MM-DD>.md`
- **Exactly one repo** → `<repo>/docs/<TOPIC>_<YYYY-MM-DD>.md`

`<workspace>` is the directory that contains both `.workspace/notes/` and the per-repo subdirectories (typically the cwd). `<TOPIC>` is `UPPER_SNAKE_CASE` and content-bearing — `QWEN_BASELINES_AND_TA`, not `WORK_LOG`.

State the chosen location in the report. If `.workspace/notes/` does not exist for a multi-repo workspace, ask the user before creating it.

## Bootstrap behavior (default)

When invoked with `/mission-log <topic>`, introspect the current conversation and pre-populate as much as can be inferred. Do not invent. If a field is genuinely empty, write `(none yet)` or `TBD` rather than leave it blank or fabricate.

Sources to mine, in priority order:

1. **The plan file**, if one exists (`~/.claude/plans/*.md` referenced this session). Goal, scope, decisions on file usually live here verbatim.
2. **Edits made this session** — gives the cross-repo touch map and the artifacts list.
3. **User decisions stated explicitly** — "let's do the sweep", "put it in task_vectors", etc. These belong in *Decisions on file*.
4. **Bugs the user and you hit and fixed**, with file:line links to the fix and a one-line *why*.
5. **Existing related docs** in the touched repos — link them under *Pointers*.

## Update behavior

When the file already exists for the same `<TOPIC>_<YYYY-MM-DD>.md`, do not rewrite it. Read it, then surgically:

- Flip checkboxes in the status board based on conversation evidence (`[ ]` → `[x]` only when actually done).
- Append rows to the live progress table if one exists and new events have happened.
- Add new entries to *Bugs hit and fixes* — never rewrite existing ones.
- Update the front-matter `status` field if it changed (`planned` → `in_progress` → `complete`).
- Move stale items from *In progress* to *Done* or *Pending* as appropriate.

When the user says `/mission-log update` (no topic), find the most recent matching log in `.workspace/notes/` or any touched-repo's `docs/` and update it. If multiple candidates exist, ask.

## Skeleton template

```markdown
---
title: <human title>
date: <YYYY-MM-DD>
repos: [<repo>, ...]
status: <planned | in_progress | complete | abandoned>
related_plan: <path or null>
---

# <human title> — <YYYY-MM-DD>

## Goal

<one paragraph: what we're trying to achieve and why these specific deliverables>

## Status board

### Done
- [x] <item — one verb, one line, file path if relevant>

### In progress
- [ ] <item — same shape>

### Pending
- [ ] <item — same shape>

## Cross-repo touch map

| Repo | Why involved |
|---|---|
| <repo> | <what role this repo plays in the push> |

## Decisions on file

- <decision> — *why*: <one-line rationale>

## Live progress (optional)

<only include this section when there's a long-running multi-step run worth tracking
in real time, e.g., a SLURM allocation with many parallel jobs. Use a table.>

| label | <axis like gpu> | status | elapsed |
|---|---|---|---|

## Bugs hit and fixes (optional)

### <one-line bug title>

<two- or three-sentence description of the bug, the symptom, and what made it
non-obvious. Then a Fix line with a file:line link.>

**Fix:** [`<repo>/<path>`](<relative path>#L<line>) — <what the fix does>.

## Pointers

- <related doc, code path, or external resource> — <one-line role>
```

## Quality bars

- The status board is the **load-bearing** section. If a reader skims nothing else, that table tells them what's done, what's running, what's left.
- Every artifact mentioned has a path, ideally a clickable relative link.
- Decisions include *why*, not just *what*. The why is what survives time.
- Bug entries lead with the **non-obvious** part. "vLLM IPC socket > 107 chars" beats "fixed bug in runner."
- The progress table appears only when something is actually running. Don't include it for retrospective logs.
- Never restate code that's in the diff. Say "added run_qwen_merge.py — TA / AVG merger for HF refs," not the function signatures.

## What this skill does not produce

- Implementation walkthroughs.
- Full diff dumps.
- Code-anchored references (those go in `<repo>/docs/`, not the mission log).
- Anything ephemeral that won't matter in a week.

## Failure modes to avoid

- Hallucinating decisions the user did not make. If unsure, omit or write `TBD`.
- Putting a cross-repo log inside a single repo's `docs/`, or vice versa. Apply the location rule.
- Rewriting an existing log on update — surgically modify only the parts that changed.
- Creating the file before any real work has been done. If the conversation has only a goal and no decisions or edits, the user probably wants a plan file (`/plan`), not a mission log.
- Writing a wall of prose. Tables and tight bullets carry the weight.
- Forgetting the date stamp. Every mission-log filename ends in `_YYYY-MM-DD.md`.

## Default behavior

- Default to bootstrap-from-context. Use `--blank` only when the user explicitly asks for an empty skeleton or when the conversation has no relevant context to mine.
- Default `status: in_progress` when the conversation shows ongoing work; `planned` only when bootstrapping at session start before any edits.
- Default the *Live progress* and *Bugs hit and fixes* sections to **omitted** unless real content exists.
- Always print the final path the file was written to, and a one-line summary of what was added or updated.
