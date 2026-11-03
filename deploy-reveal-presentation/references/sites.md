# Sites handoff and validation

Use the current Sites skill for tool schemas, supported helpers, source packaging, and publication. Do not hard-code plugin versions, opaque IDs, or credentials.

## Handoff

1. Open or create the Site checkout through Sites.
2. Build a fresh export with `scripts/build_deck.py`; inspect its adjacent provenance JSON. `--built-dir` requires a matching successful full Jekyll build.
3. Put only the reviewed export in the declared static directory. Keep `.openai/hosting.json` and private `.openai/presentation.json` outside served files.
4. Push/package the exact source with the Sites helper. Use the private publication operation only for verified owner-only access.
5. Await terminal deployment status. An expected URL alone is not deployment success.

## Checks

- Open root and original permalink; navigate horizontally, vertically, and through fragments.
- Open the menu and switch a theme; activate drawing tools.
- Check images, backgrounds, CSS, scripts, fonts, video, and iframe resources.
- Render equations; inspect resource failures.
- Open speaker view and check an actual sidecar note and its slide association.
- If enabled, verify slide numbering matches the URL fragment.
- Open `?print-pdf`; check styles and hidden chrome. Preserve notes-receiver query strings.
- Exercise dynamic animation steps and review generated media URLs the packager cannot discover.
- Check the actual access list plus anonymous access to the page and one asset. Never create a gate-bypass token for testing without the user's specific request.

Report source checks, packaging checks, local browser QA, deployment success, and authenticated production checks separately.

## Portability and parity

Local preparation needs Ruby, Bundler, locked repository gems, and Python 3. Publication additionally needs an authorized hosting connection. Missing tools are environment limitations, not permission to regenerate a deck or omit notes.

Keep reusable notes injection, zero-indexed numbering, print head/scripts integration, and Jekyll dependencies aligned between the public engine and private collection. Preserve content, privacy configuration, local ports, and repository-specific metadata. Keep private decks, sidecars, and animation media out of the public engine. Package custom animation code only as a dependency of the selected deck.
