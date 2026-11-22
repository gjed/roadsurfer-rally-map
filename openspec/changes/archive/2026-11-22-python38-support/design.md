# Design

## Context

`roadsurfer-rally.py` uses only the standard library and has run on Python 3.8 since
the prototype. The PR check runs on `ubuntu-latest` (moving from 24.04 to 26.04),
and `actions/setup-python` has no 3.8 build for 24.04 or newer.

## Decisions

- **Keep 3.8 rather than raise the minimum.** The script and tests already run on 3.8
  with one test edit, and checking it costs one short job. Raising the minimum would
  drop users for no code gain.
- **uv on `ubuntu-latest`, not `setup-python` on `ubuntu-22.04`.** GitHub retires
  runner images on a schedule, and `ubuntu-22.04` is the oldest image left; once it
  is retired the job would stop starting. uv downloads a python-build-standalone 3.8
  on any image. `setup-uv` is the only third-party action, so the job pins its commit
  SHA with a `# v10.4.0` comment that Renovate uses to update it.
  The risk moves to uv: 3.8 is end of life and receives no new builds, and a future
  uv could stop offering it. The install step fails with an `::error::` that says to
  raise the minimum everywhere at once when that happens.
- **`ruff.toml`, not `pyproject.toml`.** The repository is not a package and has no
  other use for `pyproject.toml`.
- **Tests run on 3.8 too.** A single-line multi-item `with` is all it takes, and with
  `target-version = "py38"` ruff now rejects the 3.9+ form, so it cannot come back
  unnoticed.
