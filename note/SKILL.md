---
name: note
description: Create one study card in the local ASRS vault at /home/alorozco53/asrs/notes from the current conversation. Use when the user asks to make a note/card, invokes /note for this repo, or wants to turn discussion into a study card for code/algos, code/ml, code/basics, or math.
---

# Note

This skill is bound to the local repo at `/home/alorozco53/asrs`.

Create exactly one new card from the current conversation. Work from the repo
root and write under `notes/`. Do not update `index.md` unless the user asks.

## Deck Choice

Infer the deck from the conversation:

- LeetCode, data structures, coding-interview problems, concurrency primitives:
  `notes/code/algos/`
- NumPy, ML algorithms, training tricks, broadcasting, modeling patterns:
  `notes/code/ml/`
- Basic Python or recursion:
  `notes/code/basics/`
- Proofs, derivatives, optimization theory, linear algebra identities:
  `notes/math/`

Prefer decks that already have `index.md`, because the study picker discovers
decks through that file. If the best semantic deck lacks `index.md`, say so in
one short line and still follow the closest existing card style in that deck.

## Slug

Choose a short kebab-case filename with `.md`.

- `notes/code/algos/` LeetCode cards start with the problem number, for example
  `146-lru-cache.md`; unnumbered cards use a descriptive slug.
- Other decks use descriptive slugs.

Check the target deck for collisions before writing. If a filename exists,
append a short qualifier. Never overwrite an existing card.

## Structure

Read the deck's `index.md` when present to confirm the question and answer
heading names. Also read one or two neighboring cards and mirror the local
structure, heading levels, field order, prose tone, and code-block conventions.

Common structures in this repo:

- `notes/code/algos/`: `## Number`, `## Tags`, `### Name`, `### Problem`,
  `### Solution`, `### Source`
- `notes/code/ml/`: `## Tags`, `### Name`, `### Problem`, `### Solution`,
  `### Source`
- `notes/code/basics/`: mirror neighboring cards
- `notes/math/`: `## Topic`, `## Tags`, `### Name`, `### Question`,
  `### Answer`

The question and answer headings are mandatory for decks with `index.md`.

## Content

Synthesize from the current conversation. The card should read standalone weeks
later.

- Problem or Question: state the task tightly. Include shapes, constraints, or
  assumptions when relevant.
- Solution or Answer: lead with the key idea, then include code if useful, then
  concise gotchas, tradeoffs, or alternatives.
- Source: cite the origin when possible. Use `N/A` only if no source fits.

Do not include conversation artifacts such as "as discussed" or tool output.

## Confirmation

After writing the file, print only:

1. The relative path of the new card.
2. One short line describing the card.
