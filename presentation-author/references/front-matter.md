# Front-Matter Reference — `layout: reveal`

Every key under `reveal:` in deck front matter is passed through to the
Reveal.js `Reveal.initialize()` call by the shared `_layouts/reveal.html`
layout. Defaults live in `_config.yml` under
`defaults > scope.type: presentations`; per-deck front matter overrides.

## Page-level keys

| Key | Type | Effect |
|---|---|---|
| `layout` | string | **Required**. Always `reveal` for a slide deck. |
| `title` | string | Shown in `<title>` and used by the title-card pattern. |
| `subtitle` | string | Shown in the title-card and `<meta>`. |
| `presenter` | string | Free-form attribution shown on the title slide. |

## Core Reveal.js settings

| Key | Default | Notes |
|---|---|---|
| `reveal.theme` | `night` | One of `black`, `white`, `league`, `sky`, `beige`, `simple`, `serif`, `blood`, `night`, `moon`, `solarized`. CSS lives in `/css/theme/<name>.css`. |
| `reveal.transition` | `slide` | One of `slide`, `fade`, `convex`, `concave`, `zoom`, `none`. Per-slide override via `data-transition="X"`. |
| `reveal.backgroundTransition` | `fade` | Same enum as `transition`. Controls background-color/image animation. |
| `reveal.controls` | `true` | Show navigation arrows. |
| `reveal.progress` | `true` | Show progress bar. |
| `reveal.history` | `true` | Push slide index to URL hash. |
| `reveal.center` | `true` | Vertically center slide content. Set `false` for top-aligned (used in the grid template). |

## Navigation chrome (`_includes/presentation/navbar.html`)

| Key | Default | Effect |
|---|---|---|
| `reveal.home_link` | `true` | Show the "Back to Home" link. |
| `reveal.home_url` | `/` | URL the back-link points to. |
| `reveal.home_label` | `Back to home` | Visible label. |
| `reveal.links` | empty list | List of `{label, url, newtab?}` rendered as quick-link buttons next to back-home. Use for paper / code / arXiv / demo. |
| `reveal.logo` | unset | Optional `/img/...` logo path shown in the top-right of the chrome. |
| `reveal.logo_alt` | site title | Alt text for the logo. |

Example:

```yaml
reveal:
  home_link: true
  home_url: '/'
  home_label: 'Back to Home'
  links:
    - label: 'arXiv'
      url: 'https://arxiv.org/abs/0000.00000'
    - label: 'Code'
      url: 'https://github.com/example/repo'
    - label: 'Demo'
      url: 'https://example.org/demo'
      newtab: false
```

## Plugins

All plugins ship bundled (no CDN). Each is opt-out except `math` which
is opt-in.

| Key | Default | What it does |
|---|---|---|
| `reveal.menu` | `true` | Top-left side menu listing slides. |
| `reveal.markdown` | `true` | Enables `<section data-markdown>` blocks. |
| `reveal.highlight` | `true` | Syntax highlighting via `highlight.js` (zenburn theme). |
| `reveal.zoom` | `true` | Hold `Alt` and click to zoom into a region. |
| `reveal.notes` | `true` | Speaker notes view (press `S`). |
| `reveal.chalkboard` | `true` | Draw-on-slide (`c`) + whiteboard (`b`). |
| `reveal.math` | `false` | MathJax. **Opt in** — set `true` to render `$$ ... $$`. |
| `reveal.title_footer` | `false` | Optional bottom footer plugin. |

Set any to `false` to disable. Example:

```yaml
reveal:
  menu: true
  chalkboard: true
  math: true       # opt-in
  highlight: true
  notes: true
  zoom: false      # turned off for a content-heavy talk
```

## Menu plugin config

```yaml
reveal:
  menu: true
  menu_config:
    side: left              # 'left' | 'right'
    titleSelector: 'h1, h2' # tags scanned for menu labels
    hideMissingTitles: false
    markers: false
    transitions: true       # animated menu
    openButton: true        # show the hamburger
    openSlideNumber: false
    keyboard: true
```

To give a slide a custom menu label that differs from its `<h1>/<h2>`,
add `data-menu-title="Short label"` to the `<section>`.

## Chalkboard plugin config

```yaml
reveal:
  chalkboard: true
  chalkboard_config:
    theme: chalkboard        # 'chalkboard' (dark) | 'whiteboard'
    toggleChalkboardButton: true
    toggleNotesButton: true
    # readOnly: true         # uncomment to show pre-drawn notes only
    # src: '/chalk/your.json'# pre-saved drawing JSON
```

Keyboard bindings (default):

- `b` — toggle chalkboard
- `c` — toggle notes canvas on the slide
- `DEL` — clear current slide drawing
- `BACKSPACE` — reset slide drawing
- `d` — download drawing JSON

## Math plugin config

```yaml
reveal:
  math: true
  math_config:
    mathjax: 'https://cdn.mathjax.org/mathjax/latest/MathJax.js'
    config: 'TeX-AMS_HTML-full'
```

Once enabled, use:

- `$$ ... $$` — display math
- `\( ... \)` — inline math

## Reveal config passthrough — `reveal.extend`

Any arbitrary Reveal.js init key not exposed above can be set via
`reveal.extend`. It is merged into the generated `Reveal.initialize()`
config at runtime.

```yaml
reveal:
  extend:
    width: 1366
    height: 768
    margin: 0.05
    minScale: 0.2
    maxScale: 1.35
    autoSlide: 0           # 0 disables, ms otherwise
    autoSlideStoppable: true
    mouseWheel: false
    showNotes: false       # set true for inline speaker notes
```

See the [Reveal.js docs](https://revealjs.com/config/) for the full
config surface.

## Additional CSS / JS

| Key | Effect |
|---|---|
| `reveal.additional_css` | List of `/css/...` paths added to `<head>`. Use for per-deck stylesheets in `css/decks/<slug>.css`. |
| `reveal.additional_js` | List of `/js/...` paths added before `Reveal.initialize`. |
| `reveal.additional_dependencies` | List of raw Reveal.js dependency JS objects — advanced; merged into `Reveal.initialize`'s `dependencies` array. |

Example:

```yaml
reveal:
  additional_css:
    - /css/decks/your-deck.css
```

## Minimal valid front matter

```yaml
---
layout: reveal
title: "My Deck"
---
```

Everything else has a sensible default. The above renders at
`/presentations/<filename>/` with the full chrome and the night theme.

## Production-grade paper-talk front matter

```yaml
---
layout: reveal
title: "Paper Title"
subtitle: "One-sentence framing"
presenter: "Your name — venue — date"
reveal:
  theme: night
  transition: slide
  backgroundTransition: fade
  controls: true
  progress: true
  history: true
  center: false
  menu: true
  menu_config:
    side: left
    transitions: true
    openButton: true
  chalkboard: true
  chalkboard_config:
    theme: chalkboard
    toggleChalkboardButton: true
    toggleNotesButton: true
  math: true
  math_config:
    mathjax: 'https://cdn.mathjax.org/mathjax/latest/MathJax.js'
    config: 'TeX-AMS_HTML-full'
  markdown: true
  highlight: true
  zoom: true
  notes: true
  home_link: true
  home_url: '/'
  home_label: 'Back to Home'
  links:
    - label: 'arXiv'
      url: 'https://arxiv.org/abs/0000.00000'
    - label: 'PDF'
      url: 'https://arxiv.org/pdf/0000.00000'
    - label: 'Code'
      url: 'https://github.com/example/repo'
  extend:
    width: 1366
    height: 768
    margin: 0.05
    minScale: 0.2
    maxScale: 1.35
---
```

This is the canonical block from
`_presentations/template-grid.html`. Copy verbatim and edit.
