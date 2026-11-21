# Design

## Context

`roadsurfer-rally.py` scans with `--json-out` and renders offline with
`--from-json` since [#5](https://github.com/gjed/roadsurfer-rally-map/issues/5). The
PR check runs the unit tests with `python3 -m unittest discover -s tests -v` and
renders `tests/fixtures/offers.json`. The page loads Leaflet from `vendor/` by
relative path, so it has to be served from the repository root.

## Goals / Non-Goals

**Goals:**

- One command per local task, matching what CI runs.
- `make map` and `make test` work from a clean clone, offline.

**Non-Goals:**

- Wrapping every scanner option, installing dependencies, or changing CI to call
  `make`.

## Decisions

- **`make map` falls back to the fixture.** Without `offers.json`, `map` renders
  `tests/fixtures/offers.json` and prints a note saying so and how to get real data.
  Depending on `scan` instead would turn a clean-clone `make map` into a full scan of
  about 850 requests against the unofficial API, and would fail offline. Failing with
  an error would break the acceptance criterion.
- **Phony targets, no file dependencies.** `map` always re-renders; rendering takes
  well under a second, and a file rule `index.html: offers.json` could not express
  the fixture fallback cleanly.
- **`help` is the default goal.** A bare `make` lists the targets instead of starting
  a long scan or any other side effect. The list is built from `##` comments on the
  target lines, so it cannot drift from the rules.
- **No knobs for the delay or scan filters.** `scan` is the full scan at the
  scanner's default delay; other runs call the script directly. Only `PYTHON` can be
  overridden, for testing on another interpreter.
- **`serve` binds to `127.0.0.1`.** `python3 -m http.server` listens on all
  interfaces by default; the local preview needs no network exposure.
- **Ignore `/offers.json`, anchored.** An unanchored `offers.json` pattern would also
  match `tests/fixtures/offers.json`.

## Risks / Trade-offs

- `make map` from a clean clone shows six fixture offers from Munich, not live data.
  The note says so.
- `make lint` needs `pre-commit` on the PATH; the Makefile does not install it.
