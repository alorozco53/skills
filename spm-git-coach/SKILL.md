---
name: spm-git-coach
description: Scientific project manager workflow for safe, collaborative Git change review and commit preparation. Use when the user wants to assess repo state, split work into small thematic commits, discuss tradeoffs before committing, enforce portability/hygiene conventions, and produce push-ready instructions without performing remote pushes.
---

# SPM Git Coach

Follow this workflow for every request.

## 1) Frame The Work

- Confirm objective, scope, and constraints before changing code.
- Distinguish exploration, implementation, validation, and commit phases.
- Keep batches minimal and thematic; avoid unrelated edits.
- State explicitly that remote push is user-owned unless asked otherwise.

## 2) Repo Safety And Discovery

- Inspect current branch, changed files, remotes, and submodule state.
- Detect risky artifacts before staging:
  - machine-specific absolute paths (for example `/home/...`, `/network/...`)
  - generated files (`*.out`, `*.err`, caches, `__pycache__`, notebook checkpoints, SLURM outputs)
  - logs directories (for example `logs/`)
- Prefer env variables and portable paths (`$SCRATCH`, `$HOME`) in scripts/docs.
- Never use destructive Git commands unless explicitly requested.

## 3) Collaborative Commit Planning

- Propose a short commit plan before committing:
  - one intent per commit
  - clear include/exclude file list
  - validation checks to run
- Ask for confirmation when commit boundaries are ambiguous.
- Preserve user work already present in the tree; do not revert unrelated changes.

## 4) Commit Message Conventions

- Use the agreed style with bracketed tags in present tense:
  - `[ADDED]` new functionality or files
  - `[FIXED]` bug/hygiene/portability corrections
  - `[UPDATED]` refinements, wiring, or behavior adjustments
- Keep messages concise and purpose-first.
- Prefer mixed tags in one message only when a commit truly contains multiple intents.

## 5) Validation Standard Before Commit

- Run targeted checks relevant to touched files (for example `bash -n` for shell scripts).
- Re-scan docs/scripts for non-portable absolute paths.
- Confirm deleted files are not still referenced.
- Summarize what was validated and any remaining risk.

## 6) Final Handoff

- Provide:
  - branch status
  - commit list (`sha` + message + intent)
  - any caveats (submodules, local-only commits, env assumptions)
  - suggested push commands only (no push execution)
- End with explicit next step for the user.
