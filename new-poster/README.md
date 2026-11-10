# new-poster adapter

A small independently authored Codex skill that orchestrates the external [aumona/poster-harness](https://github.com/aumona/poster-harness) LaTeX template. The template, logos, and upstream `SKILL.md` are **not vendored** here.

The pinned upstream SHA and default local directories are in [`references/upstream.json`](references/upstream.json). You may override the template checkout via `POSTER_HARNESS_TEMPLATE` or `--template`; a stale or dirty checkout is rejected rather than updated.

## Quick start

```bash
# Explicit one-time download of the reviewed revision, when you have permission
python3 new-poster/scripts/new_poster.py --bootstrap --verify

# Create independent output outside the template checkout
python3 new-poster/scripts/new_poster.py ~/Projects/presentations/posters/2026-12-01-venue-topic

# In the generated project after replacing sample content and building
make check
python3 /path/to/skills/new-poster/scripts/verify_poster.py .
```

From within `~/.codex/skills`, omit `new-poster/` duplication in the script path; these commands assume running from the repository root. The skills repo itself may be anywhere; the `SKILL.md` examples use its commonly configured `~/.codex/skills` path.

**Runtime requirements:** Python 3 standard library, Git; for building, `pdflatex` and upstream TeX packages, Make, and Poppler `pdfinfo` for the extra release gate. `--bootstrap` needs GitHub network access; existing checkout verification works offline.

**Non-goals:** owning the external template, automatically updating it, verifying the truth of scientific claims, scanning QR codes automatically, generating posters without source material, or deploying privately/publicly. Manually review the PDF, evidence and QR targets before printing.

## Unit tests (offline)

```bash
python3 -m unittest discover -s new-poster/tests -v
```

Tests construct a synthetic local Git repository, so no upstream files are copied and network access is unnecessary. They do **not** replace an end-to-end poster build against the real pinned template.

## Updating the pin

Review the new upstream commit and its history, revise `references/upstream.json`, and test a fresh checkout; an existing checkout is deliberately never changed by the wrapper. If the upstream clone disappears or rewrites history, the pin may become unavailable, so keep an authorized archived release if archival guarantees are necessary.

## Licensing and provenance

This adapter is original orchestration code. At integration time, the external upstream repository has no declared root license. A public GitHub repository does not imply unrestricted copying or redistribution; ask its author about permissions for template use/derivative work. Bundled institutional logos and bundled QR implementation have their own sources/rights. No upstream source files are included in this PR.
