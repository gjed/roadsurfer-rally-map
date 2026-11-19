# Proposal

## Why

The roadsurfer Rally scanner and its Leaflet map exist only as untracked files in
the private `travels` repo. This change imports them unchanged into the public repo
and adds what the repo needs to stand on its own: a README, a license, ignore rules
and linting
([#1](https://github.com/gjed/roadsurfer-rally-map/issues/1),
[#13](https://github.com/gjed/roadsurfer-rally-map/issues/13)).

## What Changes

- Add `roadsurfer-rally.py` (stdlib-only scanner) and `rally-map.template.html`
  (Leaflet map template) verbatim from the prototype, then a separate `style:`
  commit with `ruff format` output only.
- Add `.gitignore` for generated output: `index.html`, `.roadsurfer-rally-seen.json`,
  `__pycache__/`.
- Add `.pre-commit-config.yaml` with pre-commit-hooks (check-yaml, end-of-file-fixer,
  trailing-whitespace, check-added-large-files, check-merge-conflict), mdformat
  (mdformat-gfm, mdformat-tables), pymarkdown with `.pymarkdown.json`, and ruff (lint
  and format). Ruff runs with its default configuration. No rule is relaxed and no
  extra rule set is enabled.
- Add `README.md`: what the project does, how to run it, the API notes and known
  behaviour, an unofficial-API disclaimer and the license.
- Add `LICENSE` with the standard, unmodified Apache License 2.0 text.

Out of scope: removing `--notify`, `--via`, `--detour` and `--watch`
([#5](https://github.com/gjed/roadsurfer-rally-map/issues/5)), vendoring Leaflet
([#6](https://github.com/gjed/roadsurfer-rally-map/issues/6)), CI workflows, a
Makefile, and `AGENTS.md`.

## Capabilities

### New Capabilities

- `rally-scanner`: queries the unofficial roadsurfer Rally API for one-way relocation
  offers and renders them as a self-contained HTML map.

### Modified Capabilities

None.

## Impact

- New files only. There is no existing code.
- Runtime dependency: Python 3 standard library. The generated map loads Leaflet and
  Esri tiles from public CDNs in the browser.
- Developer dependency: `pre-commit`.
