# Design

## Context

`roadsurfer-rally.py` is a single stdlib script with a hyphen in its name. Since
[#5](https://github.com/gjed/roadsurfer-rally-map/issues/5) it can render the map from
a `--json-out` file with `--from-json`, without network access. The template embeds
the offers in an inline `<script>` right after the `vendor/leaflet/leaflet.js` tag.

## Goals / Non-Goals

**Goals:**

- Catch template JavaScript and scanner Python breakage before merge.
- Deterministic, offline checks.

**Non-Goals:**

- Running a real scan in CI, browser-level tests of the map, a Python version matrix.

## Decisions

- **Tests load the script with `importlib`.** The hyphen prevents a plain import;
  `importlib.util.spec_from_file_location` loads it as a module without renaming it.
- **Patch `get()`, not `urlopen`.** `find_offers()` is tested with the module's
  `get` replaced by a fake that serves station details and timeframes, so the date
  filter runs on known data and no request is made.
- **`--from-json` errors run as a subprocess.** That checks the real process exit
  status instead of the `SystemExit` payload.
- **Script extraction in the workflow.** A short inline Python snippet extracts the
  `<script>` that follows the Leaflet tag into a file for `node --check`. It uses the
  runner's preinstalled Node, so no extra action is needed.
- **Python `3.x` in CI only.** `setup-python` has no 3.8 build for `ubuntu-24.04`;
  the tests are run on 3.8 locally instead.
- **No paths filter.** The checks are fast, and filtering would let a workflow or
  fixture change skip them.

## Risks / Trade-offs

- The distance code lives in the template's JavaScript and gets only a syntax check.
- The fixture can drift from the live API format; the scheduled scan exercises the
  live format.
