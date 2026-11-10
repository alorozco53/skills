---
name: new-poster
description: Create an evidence-backed LaTeX research poster from a paper, results, and figures using a separately maintained, commit-pinned aumona/poster-harness checkout. Use for new academic/conference posters; not for Reveal.js slide decks or generic PDFs.
version: 0.1.0
---

# New Research Poster (external Poster Harness)

Use upstream [Poster Harness](https://github.com/aumona/poster-harness) as a **separate** LaTeX template, not as code copied into this skills repository. The exact reviewed upstream revision and default paths live in [references/upstream.json](references/upstream.json). This skill is independently authored; the upstream project has no declared general code license at the time of integration. Before distribution or derivative use of its template files, clarify permissions with its authors. Third-party logos retain separate rights.

## Scope and relationship to other skills

- Use this skill for a **new printed or PDF conference poster**. For a Reveal.js talk, use `presentation-author`, and for remotely hosting a deck use `deploy-reveal-presentation`.
- Do not create a GitHub fork, copy template sources into `alorozco53/skills`, initialize a poster Git repo, push, or publish unless requested.
- Do not silently update an existing checkout: reproducibility takes priority over upstream freshness.

## 1. Resolve and verify the pinned engine

The default template path is `~/Projects/poster-harness`; override with `POSTER_HARNESS_TEMPLATE` or `--template`. The collection default is `~/Projects/presentations/posters/`; these are defaults, not assumptions about the user's workstation.

```bash
python3 ~/.codex/skills/new-poster/scripts/new_poster.py --verify
```

If it is absent and the user authorized obtaining the upstream template, explicitly bootstrap the pinned commit (network required):

```bash
python3 ~/.codex/skills/new-poster/scripts/new_poster.py --bootstrap --verify
```

This checks the Git origin, exact HEAD SHA, clean working tree, and required template files. A mismatched, modified, or incomplete existing directory is a **hard error**; do not reset, stash, pull, overwrite, or silently choose the latest `main`. Keep any needed user changes separate. The external template is not stored in this skills repo.

## 2. Create a separate poster project

Get the source paper and/or original LaTeX, figures/results, event/date, intended audience, main message, poster size requirements, affiliations, and valid paper/code links from the user's request or referenced material. If date or venue is missing and cannot be inferred, request the minimal missing detail instead of fabricating it. Prefer original figures with their experimental conditions over recreating uncertain results. Respect the venue's dimensions, otherwise use upstream's 48 × 36 inch landscape default.

Choose a new destination, usually `~/Projects/presentations/posters/YYYY-MM-DD-venue-slug`, and run:

```bash
python3 ~/.codex/skills/new-poster/scripts/new_poster.py \
  ~/Projects/presentations/posters/YYYY-MM-DD-venue-slug
```

The wrapper verifies the pin, refuses existing destinations, and delegates scaffolding to the *upstream* `scripts/new-poster.py`. It never writes into the reusable checkout. Do not create a poster by copying an older poster's layout.

## 3. Evidence-first content workflow

Read the generated project's `README.md`, `AGENTS.md`, and `brief.md`. These project-local instructions govern the content and layout, rather than assuming they match this skill forever.

1. Fill `brief.md` with the supplied paper, underlying TeX, source results, figure assets, conference restrictions, audiences, verified authors and affiliations, and QR destinations.
2. Collect **selected**, relevant materials inside the project: `sources/` for original papers/TeX/results and `sources/citations.json` for a keyed source register; `figures/` for reproducible scripts; `assets/` for portable display figures and QR images. Preserve provenance, source paths/URLs, figure/table/section locators, captions, units, experimental conditions, and uncertainty. Do not introduce external build dependencies or symlink personal research files.
3. Fill `outline.md` **before** editing `content.tex`; show the proposed central takeaway, left overview, right evidence, footer, and the source of each factual assertion. In particular, avoid treating unsupported model-generated numbers as experimental results. Mark missing evidence explicitly rather than inventing it.
4. After the outline is accepted or the user has authorized direct completion, implement it in `content.tex`. Follow the upstream three-pane hierarchy (strong central finding, standalone overview, discussion evidence), adapting dimensions when required. Keep institutional logo provenance and publication restrictions intact.
5. Replace all starter content, both example QR destinations, and default affiliations not supported by the paper. Verify paper/code URLs and actual QR targets. The poster must be independently buildable from its own folder.

## 4. Build and release gate

In the **generated poster project**, not the reusable template:

```bash
make check
python3 ~/.codex/skills/new-poster/scripts/verify_poster.py .
```

The first command invokes upstream's LaTeX build and diagnostic checks. The second verifies essential files, a nonempty JSON source register, obvious unresolved placeholders/example links, and a single-page PDF using `pdfinfo` (Poppler). Neither command proves scientific correctness. If the source register format changes upstream, update the adapter validator explicitly and test it; do not mask parsing failures.

**Mandatory manual verification:** render `output/pdf/main.pdf` and inspect the entire poster plus close crops for panel overlap/clipping, text legibility at intended print size, true vector/raster figure quality, accurate figures/labels/captions/uncertainty, correct and appropriately attributed logos, and QR scannability with the intended destination. Compare every substantive claim with the listed primary source; the source register is not automatically cross-checked against each outline entry. Rebuild after each correction. Report checks that were unavailable, not as passed.

Do not declare the poster ready merely because `pdflatex` succeeded. Do not commit/push/publish poster contents without authorization.

## 5. Updating the upstream pin

Review upstream changes, license/permissions, and any updated `AGENTS.md`, `Makefile`, and `scripts/new-poster.py` first. Change the full 40-character commit in `references/upstream.json` through a reviewed PR, test against a **separate clean checkout** at the new SHA, run adapter unit tests, then smoke-test creation/build/render. No automatic pull or branch tracking. Existing posters remain standalone and do not update retroactively.
