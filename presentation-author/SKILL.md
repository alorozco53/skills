---
name: presentation-author
description: This skill should be used when the user asks to "create a presentation", "make a slide deck", "start a new deck", "build a reveal.js deck", "write slides for my paper", "convert a paper to slides", "make a talk", or mentions one of the three structural starter templates from the alorozco53/slides repo (horizontal, vertical, grid). Provides format reference, authoring workflow, and starter skeletons for reveal.js + Jekyll presentations.
version: 0.1.0
---

# Presentation Author

Guide an agent through authoring a reveal.js + Jekyll presentation for the
[alorozco53/slides](https://github.com/alorozco53/slides) template (a public,
locally-launchable starter that strips the engine out of
`alorozco53.github.io`). Every deck in that repo follows a single shared
layout (`layout: reveal`) with the full plugin stack (chalkboard, menu,
math, highlight, zoom, notes, markdown) and a standard chrome (back-to-home
button + paper/code quick-links).

## When to invoke

Invoke this skill when the user asks to author, scaffold, or convert
content into a slide deck for that template, or when the user references
the three structural templates (horizontal / vertical / grid).

Do **not** invoke for:
- Generic markdown notes or documents
- PowerPoint / Keynote / Google Slides exports
- Decks that are not reveal.js / Jekyll based

## Step 1 — Confirm the deck shape

Three starter shapes ship with the template. Pick **one** based on the
content arc, never invent a fourth:

| Shape | Use when… | Pattern |
|-------|-----------|---------|
| **Horizontal** | Talk is short, single-topic, sequential. No chapters, no backup. | Flat row of top-level `<section>` blocks. Audience presses `→` to advance. |
| **Vertical** | One topic with optional drilldowns or Q&A backup. | One top-level `<section>` wraps several sub-`<section>`s; audience presses `↓` to drill, `→` to skip. |
| **Grid** | Paper-talk arc: Intro → Method → Evidence → Conclusions. Multiple chapters × multiple subslides per chapter. | Several top-level `<section>` wrappers, each containing several sub-`<section>`s. Each chapter opens with a color-scaled section-title slide. |

If the user is ambiguous, ask a single clarifying question or default to
**grid** for paper-style talks and **horizontal** for short lightning talks.

## Step 2 — Copy a starter skeleton

Two sources for starter content, in priority order:

1. **Preferred — copy from the slides repo working copy** when one is
   available locally (e.g. `~/website/slides/`):

   ```bash
   cp ~/website/slides/_presentations/template-grid.html \
      ~/website/slides/_presentations/<your-slug>.html
   ```

   This pulls in the *full* template — including the demonstration
   content and `<style>` block — which is the right starting point when
   building a real deck.

2. **Fallback — use a minimal skeleton from `assets/`** when the slides
   repo is not available, or when the user wants a leaner starting point
   without the demo content. Three skeletons live alongside this skill:

   - `assets/skeleton-horizontal.html`
   - `assets/skeleton-vertical.html`
   - `assets/skeleton-grid.html`

   Each is the bare front-matter + minimal section scaffolding for that
   shape — enough to render with chrome and serve as a blank canvas.

The filename becomes the URL slug: `<your-slug>.html` renders at
`/presentations/<your-slug>/`.

## Step 3 — Edit the front matter

Every deck starts with YAML front matter under `layout: reveal`. Set:

- `title`, `subtitle`, `presenter` — strings shown in the title slide and
  `<head>`.
- `reveal.theme` — one of `black`, `white`, `league`, `sky`, `beige`,
  `simple`, `serif`, `blood`, `night` (default), `moon`, `solarized`.
- `reveal.transition` — `slide` (default), `fade`, `convex`, `concave`,
  `zoom`, `none`.
- `reveal.links` — list of `{label, url}` shown as buttons next to
  back-to-home. Use for paper / code / arXiv / demo links.
- `reveal.home_url` — usually `/` (back to repo homepage).
- `reveal.math: true` — enable MathJax (off by default).
- `reveal.chalkboard: true` — enable draw-on-slide and whiteboard.

For the exhaustive front-matter key reference, load
`references/front-matter.md`.

## Step 4 — Fill content

Slide content lives between `<section>` (or `<section data-markdown>`)
blocks. The most useful authoring patterns:

- **Title slide** — `data-background-image` + `data-background-opacity`
  with a translucent `.title-card` container.
- **Two-column body** — `<div class="two-col">` wrapping two `<div
  class="card">` blocks.
- **Fragments** — append `class="fragment"` to a `<li>` or `<p>` for
  step-by-step reveal.
- **Auto-animate** — add `data-auto-animate` to consecutive sections
  with matching `data-id="X"` on elements to morph them across slides.
- **Math** — wrap LaTeX in `$$ … $$` (display) or `\( … \)` (inline);
  requires `reveal.math: true` in front matter.
- **Code** — `<pre><code class="language-python" data-trim> … </code></pre>`.
- **Image-as-background** — `data-background-image="/img/foo.png"` plus
  `data-background-size="cover"` on the `<section>`. Overlay readable
  text with a `.hero-overlay` card.
- **Speaker notes** — `<aside class="notes"> … </aside>` shows in the
  speaker view (press `S`).
- **Menu titles** — `data-menu-title="Short label"` on each section so
  the side menu shows readable labels.

For deeper slide-design patterns (color-scaled section titles, image
side-caption layouts, results tables, the title-card class structure),
load `references/patterns.md`.

## Step 5 — Reference assets correctly

**Always use absolute, site-root-relative paths**: `/img/foo.png`,
`/css/decks/your-deck.css`, `/talks/material/conv-demo.html`.

**Never use `../foo`** (depth-relative) paths inside `_presentations/`
files. Jekyll renders them at `/presentations/<slug>/` so any `../`
references break.

Per-deck CSS goes in `css/decks/<slug>.css` and is loaded via the
`reveal.additional_css` front-matter key.

## Step 6 — Run and verify locally

```bash
cd ~/website/slides   # or wherever the slides repo lives
make install          # one-time
make run              # serves on http://localhost:4001
```

Open `http://localhost:4001/presentations/<your-slug>/` and verify:

- The deck loads (status 200, not 404).
- The back-to-home button and quick-links are present (the chrome).
- The side menu opens (top-left icon) and lists slide titles.
- Each image / asset resolves (no broken images in the browser console).
- Math renders (if enabled): no raw `$$ ... $$` text on screen.
- Code blocks are syntax-highlighted (if enabled): colored, not plain.

A `bundle exec jekyll build` success is necessary but **not sufficient**
— Jekyll will happily serve a deck whose CSS/JS/images all 404. Always
open the deck in a browser before declaring done. For common failure
modes (asset 404s, relative-path breakage, missing iframe targets, raw
LaTeX on screen), load `references/troubleshooting.md`.

## Step 7 — Surface the deck

After authoring a deck that should be discoverable, link it from one of:

- The repo homepage [`index.html`](https://github.com/alorozco53/slides/blob/main/index.html)
  if it's a template/example deck.
- [`catalog.md`](https://github.com/alorozco53/slides/blob/main/catalog.md)
  if it's a real-world deck migrated from elsewhere.

Otherwise the deck renders at its URL but no on-site link will lead a
user to it.

## Workflow summary

```
1. Confirm shape         →  horizontal / vertical / grid
2. Copy skeleton         →  from slides repo or assets/
3. Edit front matter     →  title, subtitle, theme, links, plugins
4. Fill <section> blocks →  use the authoring patterns
5. Use absolute paths    →  /img/..., /css/decks/...
6. make run + verify     →  open in browser, click through chrome
7. Surface the deck      →  link from index.html or catalog.md
```

## Hard rules

- **Always** use `layout: reveal` in deck front matter.
- **Always** use absolute paths (`/img/...`, `/css/...`) — never `../`.
- **Always** verify in a browser before declaring the deck done.
- **Never** push the slides repo without explicit user authorization.
- **Never** invent a fourth deck shape — one of the three covers every
  real use case in this template.

## Resources

### Reference files (load on demand)

- **`references/front-matter.md`** — exhaustive `reveal:` key reference,
  including plugin configuration, math/chalkboard options, and
  `extend:` passthrough.
- **`references/patterns.md`** — slide-design patterns: title cards,
  color-scaled section titles, two-column layouts, image-side-caption,
  results tables, fragments, auto-animate.
- **`references/troubleshooting.md`** — common failure modes and fixes:
  asset 404s, relative-path breakage, missing iframes, raw LaTeX,
  Jekyll URL rewriting quirks.

### Asset files (copy as starting points)

- **`assets/skeleton-horizontal.html`** — minimal flat-row skeleton.
- **`assets/skeleton-vertical.html`** — minimal vertical-stack skeleton.
- **`assets/skeleton-grid.html`** — minimal chapters-grid skeleton.

### Upstream

- Repo: <https://github.com/alorozco53/slides>
- Working copy on this machine: `~/website/slides/`
- reveal.js docs: <https://revealjs.com/>
- Beautiful Jekyll (the Jekyll theme it derives from):
  <https://github.com/daattali/beautiful-jekyll>
