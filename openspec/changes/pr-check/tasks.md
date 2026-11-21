# Tasks

## 1. Tests

- [ ] 1.1 Add `tests/fixtures/offers.json` from a real scan, with one hand-edited station name that needs escaping
- [ ] 1.2 Add `tests/test_scanner.py` for `resolve()`, `link()`, `render()`, the date-window filter in `find_offers()` and the `--from-json` error paths

## 2. Workflow

- [ ] 2.1 Add `.github/workflows/pr-check.yml` with a lint job and a build job that tests, renders the fixture and checks the page, with `::error::` annotations

## 3. Validation

- [ ] 3.1 Unit tests pass on the default Python and on Python 3.8
- [ ] 3.2 The build step and page checks pass with no network (`unshare -rn`)
- [ ] 3.3 A broken template script and a broken `render()` each make the checks fail
- [ ] 3.4 `pr-check.yml` contains no `booking.roadsurfer.com`
- [ ] 3.5 actionlint, `pre-commit run --all-files` (repo and global markdown config) and `openspec validate --strict --all` pass
