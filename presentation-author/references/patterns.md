# Slide Design Patterns

Reusable HTML/CSS patterns for the `layout: reveal` decks in
`alorozco53/slides`. Copy-paste-ready snippets. Each pattern lists the
markup, the CSS classes it expects, and where to put the CSS (per-deck
`<style>` block at the bottom of the deck, or `css/decks/<slug>.css`).

## Title slide with image background

Used in all three structural templates.

```html
<section data-transition="fade"
         data-background-color="#03040f"
         data-background-image="/img/your-hero.gif"
         data-background-size="cover"
         data-background-opacity="0.25"
         data-menu-title="Title">
  <div class="title-card">
    <h1 data-auto-animate>Your Title</h1>
    <h3 data-auto-animate>One-sentence subtitle</h3>
    <p class="attribution">Your name — venue — date</p>
  </div>
</section>
```

Required CSS:

```css
.title-card {
  padding: 1.5rem 1.8rem;
  border-radius: 14px;
  background: rgba(8, 14, 32, 0.55);
  border: 1px solid rgba(120, 180, 255, 0.35);
  backdrop-filter: blur(4px);
  max-width: 900px;
  margin: 0 auto;
}
.title-card h1 { font-size: 2.4em; line-height: 1.08; margin-bottom: 0.3em; }
.title-card h3 { color: #b6cdf0; font-weight: 400; margin-bottom: 0.7em; }
.attribution { color: #8fa6c7; font-size: 0.85em; margin: 0; }
```

`data-background-opacity="0.25"` keeps the hero image subtle behind the
card. `backdrop-filter: blur(4px)` softens whatever is behind the card.

## Color-scaled section title

For the grid template's chapter dividers. Each chapter opens with a
section-title slide whose background and text follow a per-chapter
color scale. Inspired by the `graftllm-knowledge-grafting` and
`empirical-weight-space-learning` decks.

```html
<section>
  <section class="column-title centered intro-teal-title"
           data-background-color="#0e3a4a"
           data-transition="fade"
           data-menu-title="Intro & Motivation">
    <h1>Intro &amp; Motivation</h1>
    <h2>Why this problem, why now</h2>
  </section>

  <section class="intro-teal" data-background-color="#114455">
    <h2>The pressure</h2>
    ...
  </section>
</section>
```

Pair each color scale with a matching CSS modifier:

```css
.column-title h1,
.column-title h2 {
  margin-left: auto;
  margin-right: auto;
  max-width: 980px;
}

/* Intro (teal) */
.intro-teal-title h1,
.intro-teal-title h2 { color: #d6f4ff !important; }
.intro-teal h2,
.intro-teal h3,
.intro-teal p,
.intro-teal li { color: #e7fbff !important; }
.intro-teal .card {
  background: rgba(6, 30, 40, 0.55);
  border-color: rgba(120, 215, 240, 0.4);
}
```

Standard four-chapter palette used in the grid template:

| Chapter | bg-color (title) | bg-color (body) | text |
|---|---|---|---|
| Intro (teal) | `#0e3a4a` | `#114455`–`#13525f` | `#d6f4ff` |
| Method (blue) | `#14274a` | `#1a3565`–`#1f3e75` | `#e2ecff` |
| Evidence (gold) | `#f0c847` | `#f6d86d`–`#fae59f` | `#261a02` (dark text on light bg) |
| Conclusions (purple) | `#4e2f82` | `#5a3695`–`#6742a4` | `#f3e8ff` |

The gold scale flips text color to dark because the background is
light — important for contrast.

## Two-column body

```html
<section data-background-color="#1a3565">
  <h2>The pressure</h2>
  <div class="two-col">
    <div class="card">
      <h3>Current state</h3>
      <ul>
        <li>What people do today.</li>
        <li>Where it breaks down.</li>
      </ul>
    </div>
    <div class="card">
      <h3>What we want</h3>
      <ul>
        <li>Property A under constraint B.</li>
        <li>Without losing C.</li>
      </ul>
    </div>
  </div>
</section>
```

CSS:

```css
.two-col {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}
.card {
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(0, 0, 0, 0.18);
  padding: 0.75rem 0.9rem;
}
@media (max-width: 1000px) {
  .two-col { grid-template-columns: 1fr; }
}
```

## Fragments (step-by-step reveal)

Append `class="fragment"` to elements that should appear on successive
key presses within the same slide:

```html
<section>
  <h2>Three reasons</h2>
  <ul>
    <li class="fragment">First reason.</li>
    <li class="fragment">Second reason.</li>
    <li class="fragment">Third reason.</li>
  </ul>
</section>
```

Variants (set as the value of `class="fragment X"`):

- `fade-in` (default) — appear
- `fade-out` — disappear
- `highlight-red`, `highlight-green`, `highlight-blue` — color change
- `grow`, `shrink` — scale
- `fade-up`, `fade-down`, `fade-left`, `fade-right` — directional

Order fragments with `data-fragment-index="N"`.

## Auto-animate — morph elements across slides

Add `data-auto-animate` to consecutive sections and give the elements
matching `data-id="X"` to morph them across slides.

```html
<section data-auto-animate>
  <h2>Build up an idea</h2>
  <p data-id="thought">A model is a <strong>point</strong> in parameter space.</p>
</section>

<section data-auto-animate>
  <h2>Build up an idea</h2>
  <p data-id="thought">A model is a <strong>point</strong> in parameter space — training traces a <strong>path</strong>.</p>
</section>
```

The `<p>` with `data-id="thought"` morphs in place rather than
re-rendering. Works for any element type — useful for code blocks,
SVGs, and figures that grow over consecutive slides.

## Code blocks

```html
<section>
  <h2>Algorithm</h2>
  <pre><code class="language-python" data-trim>
def step(theta, batch, lr=1e-3):
    grad = compute_grad(theta, batch)
    return theta - lr * grad
  </code></pre>
</section>
```

- `data-trim` strips leading/trailing whitespace.
- Languages: `python`, `js`, `ts`, `bash`, `yaml`, `json`, `cpp`, `rust`,
  `go`, `latex`, `julia`, etc. (full highlight.js list).
- Line numbers: add `data-line-numbers` (or `data-line-numbers="3-5"`
  to focus specific lines).
- For step-by-step code reveals across slides, use `data-line-numbers`
  with comma-separated highlight specs and Reveal will animate them as
  fragments.

## Math equations

Requires `reveal.math: true` in front matter. Then:

- Inline: `\( \nabla_\theta \mathcal{L} \)`
- Display:

```html
<p class="equation">$$\mathcal{L}(\theta) = \mathbb{E}_{(x,y)\sim\mathcal{D}}\big[\ell(f_\theta(x), y)\big] + \lambda \|\theta\|^2_2$$</p>
```

Standard `.equation` styling:

```css
.equation {
  background: rgba(160, 210, 255, 0.1);
  border-radius: 8px;
  padding: 0.5rem 0.8rem;
  margin: 0.6rem auto;
  max-width: 980px;
  overflow-wrap: anywhere;
}
```

## Image slide — figure-large pattern

```html
<section class="image-slide" data-background-color="#000000">
  <h2 class="image-caption-light">Architecture</h2>
  <img class="figure-large" src="/img/your-figure.png"
       alt="Descriptive alt text for accessibility">
</section>
```

```css
.image-slide { text-align: center !important; }
.image-caption-light { color: #ffffff !important; text-align: left; margin: 0.1rem 0 0.5rem; }
.figure-large {
  width: auto;
  max-width: 96%;
  max-height: 76vh;
  object-fit: contain;
  display: block;
  margin: 0.4rem auto;
}
```

## Image with side caption

For the "figure on the left, takeaway panel on the right" layout used
in evidence-heavy slides.

```html
<section class="image-side-caption" data-background-color="#ffffff" data-transition="convex">
  <h2>Headline result</h2>
  <div class="side-caption-layout">
    <img class="figure-medium" src="/img/result.png" alt="...">
    <div class="side-caption-panel">
      <p><strong>Takeaway</strong></p>
      <p>One-sentence interpretation of the figure.</p>
    </div>
  </div>
</section>
```

```css
.side-caption-layout {
  display: grid !important;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr) !important;
  gap: 0.9rem !important;
  align-items: center !important;
}
.side-caption-panel {
  border: 1px solid rgba(35, 88, 62, 0.25) !important;
  border-radius: 10px !important;
  background: rgba(248, 253, 250, 0.95) !important;
  padding: 0.7rem 0.8rem !important;
}
@media (max-width: 1000px) {
  .side-caption-layout { grid-template-columns: 1fr !important; }
}
```

## Image as full-slide background

Use this for hero or transition slides where text floats over imagery.

```html
<section data-background-image="/img/landscape.jpg"
         data-background-size="cover"
         data-background-position="center"
         data-background-opacity="0.55"
         data-transition="zoom"
         data-menu-title="Visual interlude">
  <div class="hero-overlay">
    <h2>The moment matters</h2>
    <p>Brief explanatory text over the imagery.</p>
  </div>
</section>
```

```css
.hero-overlay {
  background: rgba(5, 9, 22, 0.7);
  border: 1px solid rgba(180, 200, 240, 0.25);
  border-radius: 12px;
  padding: 1.4rem 1.6rem;
  max-width: 760px;
  margin: 0 auto;
}
```

## Results table

```html
<section>
  <h2>Headline numbers</h2>
  <table class="results-table">
    <thead>
      <tr><th>Setting</th><th>Baseline</th><th>Ours</th><th>Δ</th></tr>
    </thead>
    <tbody>
      <tr><td>X — metric M</td><td>0.62</td><td><strong>0.71</strong></td><td>+0.09</td></tr>
      <tr><td>Y — metric M</td><td>0.55</td><td><strong>0.68</strong></td><td>+0.13</td></tr>
    </tbody>
  </table>
</section>
```

```css
.results-table {
  width: 100%;
  max-width: 980px;
  margin: 0.5rem auto;
  border-collapse: collapse;
}
.results-table th,
.results-table td {
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.45rem 0.6rem;
  text-align: left;
}
.results-table th { background: rgba(255, 255, 255, 0.1); }
```

## Callout / blockquote

For a contribution-sentence callout on the title-page or summary slide:

```html
<blockquote class="callout">
  We show that <em>&lt;mechanism&gt;</em> achieves <em>&lt;property&gt;</em>
  on <em>&lt;setting&gt;</em>, at <em>&lt;cost&gt;</em>.
</blockquote>
```

```css
.callout {
  border-left: 4px solid #5ad1c8;
  background: rgba(90, 209, 200, 0.08);
  padding: 0.9rem 1.1rem;
  margin: 0.6rem auto;
  max-width: 820px;
  text-align: left;
  font-style: italic;
}
```

## Speaker notes

Notes are not rendered on the deck; press `S` to open the speaker view.

```html
<section>
  <h2>Main slide content</h2>
  <p>What the audience sees.</p>
  <aside class="notes">
    What you want to say but not show.
    Markdown-light: use line breaks for paragraphs; <strong>bold</strong> works.
  </aside>
</section>
```

## Per-slide menu labels

The menu plugin auto-extracts `<h1>/<h2>` text for menu labels. For
image-only slides or slides where the heading is misleading, set an
explicit label:

```html
<section data-menu-title="Architecture sketch" data-background-color="#000">
  <img src="/img/arch.png" alt="...">
</section>
```

## Manual asset slot (during draft)

When drafting a deck before all figures are ready, leave a visible
placeholder slot so the missing asset isn't silently forgotten:

```html
<p class="manual-slot"><strong>Manual asset slot:</strong> add Figure 5 here</p>
```

```css
.manual-slot {
  margin-top: 0.55rem;
  padding: 0.34rem 0.48rem;
  border-radius: 6px;
  font-size: 0.74em;
  background: rgba(214, 255, 230, 0.18);
  border: 1px dashed rgba(168, 235, 197, 0.55);
}
```

## Quick reference — `<section>` attributes

| Attribute | Effect |
|---|---|
| `data-background-color="#hex"` | Solid background color. |
| `data-background-image="/img/..."` | Background image (use absolute paths). |
| `data-background-size` | `cover`, `contain`, or `<w> <h>`. |
| `data-background-position` | `center`, `top`, `bottom left`, etc. |
| `data-background-opacity="0.X"` | Dim a background image. |
| `data-transition="X"` | Per-slide override of `reveal.transition`. |
| `data-transition-speed="fast"` | `default`, `fast`, `slow`. |
| `data-auto-animate` | Morph elements with matching `data-id` to/from previous slide. |
| `data-menu-title="X"` | Override the side-menu label. |
| `data-state="X"` | Add CSS class `X` to `<body>` while this slide is active. |
| `data-visibility="hidden"` | Skip this slide. |
| `data-visibility="uncounted"` | Keep but exclude from progress / numbering. |
