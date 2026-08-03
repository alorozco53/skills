---
name: study
description: Run one FSRS-scheduled study step for the local ASRS vault at /home/alorozco53/asrs. Use when the user invokes /study, asks to study cards, provides a deck filter for study, or answers a study prompt that should be graded.
---

# Study

This skill is bound to the local repo at `/home/alorozco53/asrs`.

Use the FSRS-backed study flow. One invocation either presents one question or,
if the user is replying to the question just presented, grades that answer and
advances the session. Do not reveal the reference answer before grading.

## Load Or Refill

Work from `/home/alorozco53/asrs`.

Determine the deck filter from the user's request:

- Accept path-like tokens such as `@notes/code/algos/`, `notes/code/algos`,
  `code/algos`, or `algos`.
- Strip a leading `@` and trailing `/`.
- If no filter is present, omit `--deck`.

Run:

```bash
python3 .claude/fsrs_session.py next [--deck <DECK>]
```

Parse the JSON. Important fields:

- `current`: relative path of the card to quiz
- `index`, `total`, `remaining`: batch progress
- `refilled`: true when a new batch was started
- `cards`: full batch list

If `refilled` is true, print a compact session summary first, listing every
card in `cards`. If false, optionally print one short progress line.

The scheduler state lives in `state.db`; the active batch lives in
`.claude/fsrs_session.json`.

## Present The Question

For `current`:

1. Read the card's deck `index.md`, meaning the `index.md` in the same
   directory as the card.
2. Parse its `question:` and `answer:` heading names.
3. Read the card.
4. Extract the section under the question heading, stopping at the next heading
   of equal or higher level.

Print, in order:

1. The card's relative path on its own line.
2. The card's `### Name` or `## Name` section value if present.
3. A separator line.
4. The question section exactly as card content, preserving code blocks.
5. `Type your answer; I'll grade against the reference.`

Then stop and wait for the user's answer.

## Grade The Reply

When the user replies with an answer to the currently presented card, compare
it to the answer section from that same card.

Return:

1. A grade label on its own line: `again`, `hard`, `good`, or `easy`.
2. One to three specific sentences of feedback.
3. A `--- Reference ---` separator, then the full answer section verbatim.

Grade meanings:

- `again`: fundamentally wrong or blank
- `hard`: partial; missed the core idea or made a meaningful error
- `good`: captured the core idea with minor gaps
- `easy`: complete and clean

## Persist The Review

Append a block to `/home/alorozco53/asrs/history.md`. If the file does not
exist, create it with `# Review history`.

Use a real local ISO-8601 timestamp with minute precision and this exact header
shape, including the em dash separators:

```markdown
## <YYYY-MM-DDTHH:MM> — <relative card path> — <grade>
<one-to-three-sentence note summarizing what was right and wrong>
```

Keep the note terse and useful for future grading.

## Apply FSRS And Advance

After updating `history.md`, run:

```bash
python3 .claude/fsrs_session.py grade --card <current> --grade <grade>
```

Parse the JSON output. If `remaining` is `0`, print a single closing line:

```text
FSRS session complete (N/N). Next /study will start a fresh batch.
```

Otherwise print:

```text
N left in this session. /study for the next card.
```

Stop after one card.
