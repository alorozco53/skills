---
name: deploy-reveal-presentation
description: Build, verify, privately deploy, update, or take down an existing Reveal.js and Jekyll presentation from Albert's public slides or private presentations repositories. Use for remote presentation hosting with ChatGPT Sites while preserving the source deck, plugins, sidecar speaker notes, and styling.
---

# Deploy Reveal Presentation

## Select source and operation

Distinguish deploy, update, prepare-only, and take-down requests. Default new deployments to owner-only ChatGPT Sites. Read the current Sites skill for exact registration, packaging, preview, and publication procedures; do not duplicate its hosting helpers or credentials.

Locate the actual checkout before using a remembered path:

- Public engine: `~/website/slides`, repository `alorozco53/slides`.
- Private collection: `~/website/alorozco53-presentation` (user's local spelling); also check `~/website/alorozco53-presentations`. Repository: `alorozco53/alorozco53-presentations`.
- Skill source: `alorozco53/skills`, commonly checked out at `~/.codex/skills`.

Do not confuse a cloud home directory with the user's laptop. Use connected GitHub or a separate checkout when local paths are absent, and report that local copies still need updating. Read the selected repository's AGENTS.md. A request to privately host one deck does not authorize publishing the collection or widening access.

Identify the selected deck and exact commit; preserve uncommitted work. Read front matter, linked scripts, images, embedded pages, and the matching `.notes.md` sidecar. Resolve an existing deployment record before creating another Site.

## Build and export

Install the repository's locked gems if needed, then run:

```bash
python3 <skill-dir>/scripts/build_deck.py \
  --source <absolute-checkout> --deck <slug-or-relative-html-path> \
  --output <new-empty-absolute-static-directory>
```

The script runs the real `bundle exec jekyll build --trace` with project-local plugins enabled, then exports the selected deck at the root and its original URL with the runtime and referenced assets. It writes provenance next to the export, outside the served directory. Inspect the dependency inventory and warnings. Sidecars are optional: a deck without notes is valid. When a nonempty sidecar exists, missing injection or unmatched note entries are failures, as are missing referenced assets.

Use `--built-dir <matching-successful-jekyll-output>` only to package an existing successful build of the same source. This is not a template-rendering fallback. Use `--url-path` for custom permalinks. Do not substitute the Liquid-only adapter from the GraftLLM experiment when Ruby plugins are required.

Preserve:

- Reveal navigation, vertical stacks, fragments, transitions, menus, themes, drawing tools, and speaker view.
- `_plugins/inject_notes.rb` and injected `.notes.md` sidecars. Check actual note content in speaker view, not just the timer.
- Optional zero-indexed slide numbering, print stylesheet selection, hidden print chrome, and the Export menu.
- Existing MathJax/Google Fonts integration. Report CDN resources as external dependencies; bundle replacements only when requested.
- Deck-specific scripts, animation media, videos, and embedded HTML. Review dynamically constructed URLs because static scanning cannot prove them complete.

Export only the selected deck. Never upload the full `_site/`, private source tree, raw sidecars, Git history, other decks, credentials, or machine-local configuration. Inspect inherited analytics and metadata; disable analytics with a temporary build overlay when necessary for private hosting, preserving upstream content.

## Validate and privately deploy

Follow [references/sites.md](references/sites.md) and the current Sites skill. An installed skill does not itself provide Sites tools, authentication, or hosting access. When those are unavailable, finish a reviewable build and report publication pending.

Verify the selected deck in a browser when supported: images, backgrounds, equations, menu/themes, notes, numbering, drawing, print view, and any video/iframe. Record verification limits. Confirm the audience before updating an existing Site; stop if it is broader than requested. Never substitute a client-side password or gate-bypass token for service access controls.

Register once, persist the exact returned project ID, push matching Site source, save/deploy privately, and await terminal status. Preserve project identity on updates. Check anonymous access to both the root and a representative image/script. Verify signed-in production access when the session permits; distinguish it from local preview QA.

Keep a private deployment record in the Site source with project ID, returned URL, source repository/commit, selected path, package digest, saved version/deployment IDs, audience, and completed checks. Never put private titles, URLs, IDs, notes, or credentials in the public skills repo. GitHub changes do not automatically redeploy the Site unless separately configured.

## Update or take down

For updates, reread audience and provenance, rebuild, verify, and deploy to the same Site.

For take-down requests, resolve the exact Site and distinguish permanent deletion from replacing its live content. Use supported controls. A Site-backed Library item's delete operation deletes its Site: verify `site_metadata.project_id` and read current Library management guidance first. Follow native approval requirements; never delete an ordinary similarly named file as a substitute. Verify the former URL no longer serves the deck. Replacing a live version does not erase saved versions; deletion does not promise erasure of logs, caches, screenshots, or downloads.

Return the literal deployed URL, audience, preserved features, verification limits, and whether the result is deployed, prepared, or deleted. Do not promise expiry unless an authorized automation actually exists.
