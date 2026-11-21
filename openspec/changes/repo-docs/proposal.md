# Proposal

## Why

The repository has a README but no contributor documentation, no single entry point
for the local commands and no issue templates
([#12](https://github.com/gjed/roadsurfer-rally-map/issues/12)). Contributors and
coding agents have to read the workflows to learn how to scan, render, lint and
test, and nothing written down tells them the rate-limit, commit, OpenSpec and
`vendor/` rules.

## What Changes

- Add a `Makefile` with `help` (default), `scan`, `map`, `serve`, `lint` and `test`.
  `scan` writes `offers.json` with `--json-out`; `map` renders `index.html` from it
  with `--from-json` and no network, and falls back to
  `tests/fixtures/offers.json` with a printed note when there is no `offers.json`.
- Git-ignore the root `offers.json`.
- Add `AGENTS.md`: what the repo is, API notes, rate-limit rules, the scan/render
  split and the JSON format, local build/lint/test, the OpenSpec workflow, commit
  conventions, `vendor/` rules and PR rules.
- Add `CONTRIBUTING.md`: setup, pre-commit, tests, PR flow, pointing to `AGENTS.md`.
- Add `.github/ISSUE_TEMPLATE/` issue forms: bug report, feature request and a
  `config.yml` with blank issues disabled and a link to the live map.
- README: link to the live map and both workflows, list the `make` targets, keep
  the unofficial-API disclaimer.

Out of scope: CI changes, scanner changes, scan metadata in the JSON
([#4](https://github.com/gjed/roadsurfer-rally-map/issues/4)) and Renovate
([#11](https://github.com/gjed/roadsurfer-rally-map/issues/11)).

## Capabilities

### New Capabilities

- `developer-tooling`: local `make` targets for scanning, rendering, serving,
  linting and testing.

### Modified Capabilities

None. The documentation and issue templates need no spec.

## Impact

- New files: `Makefile`, `AGENTS.md`, `CONTRIBUTING.md` and the issue templates.
- `.gitignore` and `README.md` change. `roadsurfer-rally.py`, the template, the
  tests and the workflows are unchanged.
