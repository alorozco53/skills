# Troubleshooting — common failure modes when authoring slides

Sorted from most-common to most-obscure. Each entry: **symptom** →
**diagnosis** → **fix**. These are the issues that actually break
real decks in this template; verify against this list before declaring
a deck done.

## "Deck loads but every asset 404s"

**Symptom:** The deck URL returns HTTP 200, but the page looks like
flat unstyled HTML. Browser console shows 404s for `/css/...`, `/js/...`,
images, or plugin files. The chrome (back-to-home, menu) is missing.

**Diagnosis:** Jekyll build succeeded but assets aren't where the deck
expects them. This is the single most common failure mode and the
reason `bundle exec jekyll build` success is **not** sufficient as a
verification step.

**Fix:** `curl -s http://localhost:4001/presentations/<slug>/ | grep -E 'reveal-chrome|/css/reveal.css|/js/reveal.js'`. All three should
appear. If any are missing, the layout isn't being applied — verify
`layout: reveal` is set in front matter.

## "Relative `../` paths break after Jekyll renders"

**Symptom:** Deck at `_presentations/foo.html` references images with
`<img src="../img/bar.png">` and they 404.

**Diagnosis:** Jekyll renders `_presentations/foo.html` at
`/presentations/foo/`. From that URL, `../img/bar.png` resolves to
`/presentations/img/bar.png` — which doesn't exist. The image actually
lives at `/img/bar.png`.

**Fix:** Use absolute, site-root-relative paths everywhere inside
deck HTML:

- `/img/bar.png` ✓
- `../img/bar.png` ✗
- `img/bar.png` ✗ (relative — same problem)
- `{{ '/img/bar.png' | relative_url }}` ✓ (works through Jekyll Liquid)

The rule applies to `<img src>`, `<a href>`, `<link href>`,
`<script src>`, `<iframe src>`, `data-background-image=`,
`<source src>`, and any `url(...)` inside `<style>` blocks.

## "Folder-index URL vs `.html` URL"

**Symptom:** Cross-deck link `<a href="/talks/foo.html">` returns 404.

**Diagnosis:** Jekyll folder-indexes any HTML file that has front
matter. `_presentations/foo.html` → `/presentations/foo/`, NOT
`/presentations/foo.html`. The same happens for files at
`talks/foo.html` if they have front matter — they render at `/talks/foo/`.

**Fix:** Always link to the trailing-slash folder form:

- `/presentations/foo/` ✓
- `/presentations/foo.html` ✗
- `/talks/foo/` ✓
- `/talks/foo.html` ✗ (except for files without front matter)

Files **without** front matter are served as-is at their original path.

## "Math equations show as raw `$$ ... $$`"

**Symptom:** LaTeX appears literally on the slide, not rendered.

**Diagnosis:** `reveal.math` is **off by default**. The plugin must be
opted in explicitly.

**Fix:** In front matter:

```yaml
reveal:
  math: true
  math_config:
    mathjax: 'https://cdn.mathjax.org/mathjax/latest/MathJax.js'
    config: 'TeX-AMS_HTML-full'
```

If math is enabled but a *specific* equation still appears raw, check
that:

- It's not inside a `<code>` block (HTML-escaped, won't be parsed).
- Backslashes in inline math are not escaped — `\(`/`\)` work; HTML
  entities like `&#92;(` do not.

## "Code blocks show as plain text"

**Symptom:** `<pre><code>` blocks render without syntax highlighting.

**Diagnosis:** Either (a) `reveal.highlight` is disabled, or (b) the
`class="language-X"` attribute is missing or wrong.

**Fix:**

- Confirm `reveal.highlight` is not set to `false`.
- Add `class="language-<lang>"` to the `<code>` tag — use the
  highlight.js language name (`python`, `js`, `bash`, `yaml`, `cpp`,
  etc.).
- For trimmed leading whitespace, add `data-trim` to `<code>`.

## "Side menu doesn't open"

**Symptom:** No hamburger icon visible in the top-left, `M` key does
nothing.

**Diagnosis:** Either `reveal.menu` is disabled or the menu CSS isn't
loaded.

**Fix:**

```yaml
reveal:
  menu: true
  menu_config:
    openButton: true
```

If still missing, verify `/plugin/menu/menu.css` returns 200 in the
browser network panel.

## "Side menu labels are wrong / missing"

**Symptom:** Menu shows generic labels like "Slide 3" or nothing for
image-only slides.

**Diagnosis:** The menu plugin scans `<h1>/<h2>` for labels. Image
slides without headings show as unlabeled.

**Fix:** Add `data-menu-title="Short label"` to the `<section>`:

```html
<section data-menu-title="Architecture" data-background-color="#000">
  <img src="/img/arch.png" alt="...">
</section>
```

## "Iframe content shows `Not Found`"

**Symptom:** An `<iframe src="material/conv-demo.html">` shows 404.

**Diagnosis:** The iframe target is referenced relative to the deck's
URL, not its source path. If the deck lives at
`/presentations/foo/`, the iframe expects
`/presentations/foo/material/conv-demo.html`.

**Fix:** Either move the iframe target to `/talks/material/conv-demo.html`
(or similar absolute path) and rewrite the `src` attribute, or use
absolute paths throughout. **Always test iframe content by clicking
through to the slide that embeds it.**

## "Chalkboard or notes button missing"

**Symptom:** Top-right chalkboard / notes buttons not visible despite
`chalkboard: true`.

**Diagnosis:** The plugin needs both `chalkboard: true` and the toggle
buttons enabled:

**Fix:**

```yaml
reveal:
  chalkboard: true
  chalkboard_config:
    theme: chalkboard
    toggleChalkboardButton: true
    toggleNotesButton: true
```

Keyboard shortcuts (`b` for chalkboard, `c` for notes-on-slide) work
even without buttons.

## "Theme didn't change after I set `reveal.theme`"

**Symptom:** Set `reveal.theme: white` but the deck still renders dark.

**Diagnosis:** Jekyll caches `_site/` — most changes hot-reload, but
sometimes the cached theme CSS persists.

**Fix:** `make clean && make run`, or restart the Jekyll server.

## "Per-deck CSS isn't loaded"

**Symptom:** Wrote `css/decks/foo.css` but the deck doesn't pick it up.

**Diagnosis:** Per-deck CSS isn't auto-discovered. It must be wired
through the `reveal.additional_css` front-matter key.

**Fix:**

```yaml
reveal:
  additional_css:
    - /css/decks/foo.css
```

Or inline the CSS in a `<style>` block at the bottom of the deck for
self-contained portability.

## "Slide layout shifts after editing `_config.yml`"

**Symptom:** Navbar links change but you don't see them; or theme
default changes don't appear.

**Diagnosis:** Jekyll **does not hot-reload `_config.yml`**. It's read
once at server start.

**Fix:** Restart the Jekyll server (`Ctrl+C`, then `make run`).

## "Background image is too bright behind text"

**Symptom:** Text on a hero/title slide is illegible against the
background image.

**Diagnosis:** `data-background-image` is rendered at full opacity by
default.

**Fix:** Add `data-background-opacity="0.25"` (or 0.3, 0.4 — tune to
taste) to the `<section>`. For full readability, pair with a
`.title-card` or `.hero-overlay` translucent container around the
text:

```html
<section data-background-image="/img/hero.gif"
         data-background-size="cover"
         data-background-opacity="0.25">
  <div class="title-card">...</div>
</section>
```

## "Fragments appear all at once / not in order"

**Symptom:** `class="fragment"` items all reveal together, or in the
wrong order.

**Diagnosis:** Default fragment order is document order. If items must
appear in a specific order, set `data-fragment-index`.

**Fix:**

```html
<ul>
  <li class="fragment" data-fragment-index="2">Second.</li>
  <li class="fragment" data-fragment-index="1">First.</li>
  <li class="fragment" data-fragment-index="3">Third.</li>
</ul>
```

If fragments **don't appear at all**, the slide may have been wrapped
in a `data-markdown` block where the `class` attribute didn't survive
parsing — switch to plain HTML for that slide.

## "Auto-animate doesn't morph between slides"

**Symptom:** `data-auto-animate` set on consecutive slides, but
elements re-render rather than morphing.

**Diagnosis:** Auto-animate matches elements across slides by tag,
text, and (if set) `data-id`. If an element's tag or attributes change
between slides, the match fails.

**Fix:** Add explicit `data-id="X"` to the elements that should morph:

```html
<section data-auto-animate>
  <p data-id="thought">Version 1</p>
</section>
<section data-auto-animate>
  <p data-id="thought">Version 2 — extended</p>
</section>
```

## "Deck looks fine locally but the homepage doesn't link to it"

**Symptom:** Deck renders at its URL but no on-site link reaches it.

**Diagnosis:** Adding a deck file doesn't auto-list it on the
homepage. The homepage and catalog are hand-curated.

**Fix:** Edit
[`index.html`](https://github.com/alorozco53/slides/blob/main/index.html)
(template-grade decks) or
[`catalog.md`](https://github.com/alorozco53/slides/blob/main/catalog.md)
(migrated real-world decks) to add a link.

## "I keep getting `Alberto` instead of `Albert`"

**Symptom:** A draft accidentally uses "Alberto" in place of "Albert".

**Diagnosis:** The user's name is **Albert**, not Alberto. The Spanish
form is wrong even though the cultural context might make it seem
natural.

**Fix:** Sweep with `grep -rn "Alberto" .` and fix any hits before
committing. This includes `LICENSE`, `README.md`, `_config.yml`
`author.name`, deck `presenter` fields, and any prose mentioning him
by name.

## Verification checklist before declaring a deck done

Run these checks in order; stop at the first failure:

1. `curl -s -o /dev/null -w '%{http_code}\n' http://localhost:4001/presentations/<slug>/` → expect **200**
2. `curl -s URL | grep -c 'reveal-chrome'` → expect **≥1**
3. `curl -s URL | grep -c '/css/reveal.css'` → expect **≥1**
4. `curl -s URL | grep -c '/js/reveal.js'` → expect **≥1**
5. Open the deck in a browser. Click "Back to home" — expect to land on
   `/`. Open the side menu — expect labels for each slide.
6. Spot-check every image / iframe / video asset returns 200.
7. If `reveal.math: true`, navigate to a math slide and verify no raw
   `$$` is on screen.
8. If code blocks present, verify they are syntax-highlighted (colored,
   not plain monospace).
9. If chalkboard enabled, press `b` and `c` — both should toggle their
   respective canvases.
