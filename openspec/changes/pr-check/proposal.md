# Proposal

## Why

Nothing validates a pull request today. A change that breaks the map template's
JavaScript or the scanner's Python is only noticed after it is merged, when someone
opens the map
([#9](https://github.com/gjed/roadsurfer-rally-map/issues/9)).

## What Changes

- Add `.github/workflows/pr-check.yml`, run on every `pull_request` with read-only
  repository permissions:
  - a lint job that runs pre-commit with the repository config on all files (ruff,
    ruff-format, mdformat, pymarkdown and the generic hooks);
  - a build job that runs the unit tests, renders the map from a committed fixture
    with `--from-json`, and checks the generated page: the data placeholder is
    replaced, the embedded script parses with `node --check`, and Leaflet is loaded
    from `vendor/leaflet/`, not from unpkg.
  - Every failing step prints an `::error::` annotation that says what to fix.
- Add `tests/fixtures/offers.json`: six offers from station 1 (Munich) in the
  `--json-out` format, taken from one real scan. The sixth record (Munich to Valencia)
  is hand-edited: its destination name is `Valencia "Port" </script><b>`, to exercise
  escaping.
- Add `tests/test_scanner.py` (stdlib `unittest`) covering station resolution,
  booking-link building, rendering and escaping, the date-window filter (with the
  API client patched out) and the `--from-json` error paths.

The issue also asks for a unit test of the distance helper. The Python `km()` helper
no longer exists: distances are computed by the template's JavaScript, so that code
is covered only by the `node --check` syntax check, not by a unit test.

No refactor of `roadsurfer-rally.py` is needed: every helper under test is reachable
through its existing signature.

Out of scope: the scheduled scan and Pages deploy
([#2](https://github.com/gjed/roadsurfer-rally-map/issues/2),
[#3](https://github.com/gjed/roadsurfer-rally-map/issues/3)), a release workflow
([#10](https://github.com/gjed/roadsurfer-rally-map/issues/10)), a Makefile
([#12](https://github.com/gjed/roadsurfer-rally-map/issues/12)) and a Python 3.8 CI
leg (3.8 has no `setup-python` build on `ubuntu-24.04`; it is verified locally).

## Capabilities

### New Capabilities

- `pr-check`: offline validation of every pull request.

### Modified Capabilities

None.

## Impact

- New files: the workflow, the fixture and the tests. `roadsurfer-rally.py` and the
  template are unchanged.
- Pull requests get two required-able checks. They need no secrets and make no
  request to `booking.roadsurfer.com`.
