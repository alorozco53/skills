---
name: research-kb-curator
description: Curate an Obsidian research knowledge base from academic-paper links, local papers, and existing notes. Use when asked to process, extract, integrate, compare, synthesize, normalize, or audit research knowledge as traceable claims, evidence, mechanisms, assumptions, limitations, connections, and project implications. Do not use for generic paper summaries, bibliography formatting, or indiscriminate paper archiving.
---

# Research KB Curator

## Goal

Turn sources into a small amount of reusable, precisely sourced research
knowledge, and integrate that knowledge into the existing Obsidian vault.

The source is evidence. The knowledge base stores what is useful from it.

## Mandatory startup

1. Read the repository-root `AGENTS.md`.
2. Read `KB_SCHEMA.md`.
3. Read `references/evidence-policy.md`.
4. Inspect the current working tree with `git status --short` when Git is
   available.
5. Identify the requested workflow:
   - process a source;
   - integrate an already-written source note;
   - synthesize or compare;
   - audit or repair the vault;
   - scaffold or normalize notes.
6. Search the vault before creating files.

## Workflow A — Process a paper or source

### 1. Resolve and inspect the source

- Prefer the exact URL supplied by the user.
- Retrieve the full paper when available.
- For local files, inspect the supplied file directly.
- Record whether access was `full-text`, `abstract-only`, `secondary`, or
  `unavailable`.
- Do not infer exact tables, equations, datasets, or results from a title,
  abstract, alphaXiv discussion, or search snippet.
- If the source cannot be accessed, do not fabricate a processed note. Create
  or update an inbox entry, or create an explicitly partial source note only
  when the user requests it.

### 2. Check for an existing record

Search by:

- exact title and distinctive title fragments;
- first author and year;
- DOI;
- arXiv identifier;
- OpenReview forum URL;
- canonical and alternate URLs.

If a source note exists, update it instead of creating a duplicate.

### 3. Read relevant context

Search `20 Concepts/`, `30 Projects/`, and `40 Syntheses/` for the source's core
ideas and the user's active project terms.

Read only the most relevant notes first. Expand the search when needed.

### 4. Extract selectively

Extract only durable material:

- claims that may support an argument;
- concrete evidence;
- mechanisms;
- assumptions;
- limitations or confounders;
- connections to existing sources and concepts;
- implications for active projects or experiments.

Do not create a section-by-section summary.

For each source-dependent block:

1. identify what the authors explicitly state;
2. identify what the evidence actually establishes;
3. record an exact locator;
4. state scope and boundary conditions;
5. label the agent's assessment separately;
6. label speculation explicitly.

### 5. Write the source note

- Use `assets/source-note.md` as the structural starting point.
- Follow `KB_SCHEMA.md`.
- Omit empty boilerplate sections.
- Use a stable, human-readable filename.
- Assign stable block IDs only to reusable blocks.
- Preserve the source URL and access level.
- Do not store the PDF unless explicitly asked.

### 6. Integrate

Update the smallest relevant set of concept or project notes.

- Prefer embedding or linking the new source block.
- Do not duplicate its wording into multiple notes.
- Add qualifications or counterevidence where needed.
- Do not create a concept page for a one-off keyword.
- If the new source changes an existing position, revise the position and
  explain the changed boundary conditions.

## Workflow B — Integrate an existing source note

1. Validate its source and access metadata.
2. Identify its genuinely reusable blocks.
3. Search for related concept, project, and synthesis notes.
4. Add links or embeds where they improve the knowledge graph.
5. Avoid copying prose.
6. Flag unsupported claims, missing locators, and blurred epistemic roles.
7. Do not rewrite the entire source note merely for stylistic uniformity.

## Workflow C — Synthesize or compare

1. Restate the exact research question.
2. Search source blocks and concept notes.
3. Build an evidence map before writing the synthesis.
4. Separate:
   - agreement under shared conditions;
   - apparent disagreement caused by different setups;
   - genuine contradiction;
   - absent evidence;
   - mechanistic explanation;
   - speculative bridge.
5. Cite source notes and stable block IDs.
6. Use `assets/synthesis-note.md` when creating a persistent synthesis.
7. Do not use outside knowledge silently. Add external sources only when the
   user requested research beyond the vault, and process them with the same
   evidence policy.

## Workflow D — Audit the vault

Check for:

- duplicate source records or canonical URLs;
- duplicate block IDs;
- missing frontmatter fields;
- source-dependent claims without locators;
- abstract-only notes that imply full-text verification;
- generic summaries with no reusable knowledge;
- duplicated text that should be embedded;
- concept notes that merely list papers;
- near-duplicate concept pages;
- broken or unstable block references;
- author claims presented as facts;
- interpretations presented as evidence;
- obsolete inbox entries;
- inconsistent terminology affecting retrieval.

Run:

```bash
python .codex/skills/research-kb-curator/scripts/validate_kb.py .
```

For broad audits, report findings before making large-scale changes. Apply safe,
local fixes directly; propose structural migrations separately.

## Workflow E — Scaffold or normalize

- Use the templates in `assets/`.
- Preserve existing user content.
- Normalize only the files in scope.
- Do not rename files or block IDs without updating all references.
- Do not add a large taxonomy, plugin dependency, or automation without a
  demonstrated need.

## Quality gate

Before finishing:

1. Run the validator.
2. Run `git diff --check` when Git is available.
3. Inspect the complete diff.
4. Verify every newly asserted paper fact against the retrieved source.
5. Confirm exact locators.
6. Confirm no PDF or attachment was added accidentally.
7. Confirm no existing user judgment was silently overwritten.
8. Confirm the new material connects to the vault rather than merely occupying
   a new file.

## Final response

Report:

- changed files;
- the durable knowledge added or repaired;
- validation results;
- verification limits;
- any unresolved decision.

Do not claim completion when the source was inaccessible or only partially
verified.
