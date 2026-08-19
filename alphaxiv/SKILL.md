---
name: alphaxiv
description: Use AlphaXiv for paper discovery, paper reading, PDF question answering, paper codebase inspection, researcher lookup, and AlphaXiv library actions. Fall back to the legacy public overview API only when the MCP tools are unavailable and the task is a single-paper summary.
---

# AlphaXiv

Use AlphaXiv's MCP tools when they are available. Prefer them over raw arXiv PDFs, ad hoc web scraping, or the old public overview endpoints.

## When to Use

- User asks for related papers, literature discovery, or the latest work in an area
- User shares a paper URL, title, or arXiv ID and wants a summary or explanation
- User wants targeted questions answered from a paper with page-grounded evidence
- User wants to inspect a paper's GitHub repository
- User wants to find researchers or manage their AlphaXiv library

## Preferred Routing

- Use `discover_papers` for topic-level discovery and related-work searches.
- Use `get_paper_content` for a single paper when you want AlphaXiv's structured report or the full extracted text.
- Use `answer_pdf_queries` when the user asks specific questions about one paper and page-level evidence matters.
- Use `read_files_from_github_repository` for codebase inspection tied to a paper repo.
- Use the researcher tools for "who works on X?" or person/profile questions.
- Use the library tools only for explicit library or folder actions.

## Setup On Another Machine

This skill alone is not enough. AlphaXiv MCP usage depends on both:

- this skill folder under `~/.codex/skills`
- a local Codex plugin named `alphaxiv` that points to AlphaXiv's MCP server

For a desktop or laptop with interactive sign-in:

1. Sync or copy this skill to the new machine.
2. Copy or recreate the local plugin source at `~/plugins/alphaxiv`.
3. Ensure your personal marketplace file `~/.agents/plugins/marketplace.json` contains an entry for `alphaxiv` whose source path is `./plugins/alphaxiv`.
4. Install the plugin with `codex plugin add alphaxiv@personal`.
5. Start a fresh task before testing. Do not rely on a task that was already open before installation.
6. On first real AlphaXiv use, expect an OAuth/browser sign-in flow.

For a headless server or remote machine without convenient browser auth:

- Do not assume the OAuth-based plugin is the best fit.
- AlphaXiv's MCP docs say non-interactive usage should use an API key with `Authorization: Bearer <key>` instead of OAuth.
- Prefer a separate headless variant of the plugin or a machine-local edit of the plugin's MCP config for API-key auth.
- After changing the plugin config, reinstall the plugin and start a fresh task before use.

## Portability Notes

- If the AlphaXiv MCP tools are missing in the current task, the most likely causes are: the plugin is not installed on this machine yet, the task started before the plugin was installed, or authentication has not been completed yet.
- The skill can be tracked in a dotfiles or shared-skills repo, but the plugin source and personal marketplace entry must also exist on each machine that should use AlphaXiv through MCP.
- Keeping the skill folder name aligned with the skill name is recommended for clarity.

## Fallback Behavior

If the AlphaXiv MCP tools are missing in the current task, assume the plugin is not installed yet or this task started before the plugin was loaded.

- For a single-paper summary only, fall back to the public REST flow below.
- Do not use the fallback for researcher lookup, library actions, repo reads, or topic discovery. Those should wait for the MCP plugin.

### Legacy summary fallback

1. Extract the paper ID from an arXiv or AlphaXiv URL, title context, or raw ID when obvious.
2. Resolve the paper:

```bash
curl -s "https://api.alphaxiv.org/papers/v3/{PAPER_ID}"
```

3. Extract `versionId` from the JSON response.
4. Fetch the overview:

```bash
curl -s "https://api.alphaxiv.org/papers/v3/{VERSION_ID}/overview/en"
```

- Prefer `intermediateReport` when present.
- Otherwise use the structured `summary` fields and `overview`.
- If the resolve step returns 404, the paper is not indexed on AlphaXiv.
- If the overview step returns 404, the overview has not been generated yet.
