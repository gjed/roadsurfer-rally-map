# Tasks

## 1. Scanner

- [ ] 1.1 Add `--road-cache` and `--routing-url`, the cache file and its key.
- [ ] 1.2 Route missing pairs with OSRM `/table`, sequential, 1 s apart, with a
  User-Agent; write `km` and `km_estimated` into every record.
- [ ] 1.3 Fall back to the × 1.3 estimate on failure; never cache it, never count it
  as a failed roadsurfer request, stop routing after a 429 or three failures in a row.
- [ ] 1.4 Route only after the scan check and only when `--json-out` or `--map` is
  written; never with `--from-json`.
- [ ] 1.5 Git-ignore `road-distances.json`.

## 2. Page

- [ ] 2.1 Use the record's `km` for the filter, the `km` column and sort, the popup
  and the tooltip; keep × 1.3 for records without it.
- [ ] 2.2 Label estimates with `~`, a title and a footer note; credit OSRM and
  OpenStreetMap when routed distances are shown.

## 3. Workflow

- [ ] 3.1 Restore the cache before the Scan step and save it after it, with a key per
  run and `restore-keys`, keeping `contents: read` and the `pages` concurrency.

## 4. Tests and docs

- [ ] 4.1 Offline tests with the routing call mocked: cache hit, miss, failure
  fallback, stop rules, render with and without the new fields, JSON shape, no request
  with `--from-json`.
- [ ] 4.2 Update README.md and AGENTS.md.
- [ ] 4.3 `make lint test map`, the Python 3.8 test run and
  `openspec validate --strict --all`.
