# Tasks

## 1. Lint

- [x] 1.1 Add `ruff.toml` with `target-version = "py38"`
- [x] 1.2 Remove the `# noqa: UP017` from `roadsurfer-rally.py`
- [x] 1.3 Replace the parenthesized `with (...)` in `tests/test_scanner.py`

## 2. Workflow

- [x] 2.1 Add a `python38` job to `pr-check.yml` that installs 3.8 with uv, compiles the scanner, runs `--help`, the unit tests and the offline fixture render, with `::error::` annotations

## 3. Documentation

- [x] 3.1 README and AGENTS.md state the minimum CI checks and what must change with it

## 4. Validation

- [x] 4.1 `ruff check` and `ruff format --check` pass with the new config, and ruff no longer flags `timezone.utc`
- [x] 4.2 With `datetime.UTC` reintroduced, the 3.8 job's commands fail locally
- [x] 4.3 Unit tests pass on the default Python and on 3.8
- [x] 4.4 actionlint, `pre-commit run --all-files` and `openspec validate --strict --all` pass
