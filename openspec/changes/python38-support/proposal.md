# Proposal

## Why

The README promises Python 3.8 or newer, but nothing checks it
([#30](https://github.com/gjed/roadsurfer-rally-map/issues/30)). Ruff 0.17 runs with
no configured `target-version`, so it assumes Python 3.11 and its `UP` rules rewrite
code to newer syntax. In [#20](https://github.com/gjed/roadsurfer-rally-map/pull/20)
this turned `timezone.utc` into `datetime.UTC`, which fails at import on Python 3.8
to 3.10, and the line had to be pinned with `# noqa: UP017`. The tests already use a
parenthesized multi-item `with`, which does not parse on 3.8, and CI only installs
the newest 3.x.

## What Changes

- Add `ruff.toml` with `target-version = "py38"`, so ruff check and ruff format never
  suggest syntax newer than 3.8. Drop the `# noqa: UP017` in `roadsurfer-rally.py`.
- `tests/test_scanner.py`: replace the parenthesized `with (...)` by a single-line
  multi-item `with`, so the tests parse and run on 3.8.
- `pr-check.yml`: add a `python38` job that installs Python 3.8 with uv and
  byte-compiles the scanner, runs `--help`, runs the unit tests and renders the
  fixture offline, each step with an `::error::` annotation.
- README and AGENTS.md say which minimum CI checks and that `ruff.toml`, the job and
  the docs change together.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `pr-check`: the lint check lints for the minimum Python, and a check runs the
  scanner and the unit tests on Python 3.8.
- `rally-scanner`: the supported Python versions become a requirement.

## Impact

- New `ruff.toml`; one new job in `pr-check.yml`; one test rewritten without changing
  what it checks; one `noqa` comment removed. `scan.yml` keeps the newest 3.x.
