# Tasks

## 1. Scanner

- [x] 1.1 Record the scan metadata after the scan and write it as `scan` next to `offers` in `--json-out`
- [x] 1.2 Embed the metadata in the page through a `/*SCAN*/null` placeholder with the `</` escaping
- [x] 1.3 Embed the `scan` object of a `--from-json` file and render files without one

## 2. Map

- [x] 2.1 Show `updated YYYY-MM-DD HH:MM UTC` in the toolbar, with the counts in its tooltip, and nothing without metadata

## 3. Documentation

- [x] 3.1 Document the metadata keys and the toolbar timestamp in the README

## 4. Validation

- [x] 4.1 Unit tests cover the metadata in `--json-out` and in the page, the escaping, and the fixture without metadata
- [x] 4.2 A real `--from 1` scan writes the metadata to the JSON and the page
- [x] 4.3 Offline renders from the new JSON and from `tests/fixtures/offers.json` succeed
- [x] 4.4 Headless Chrome shows the timestamp for the new JSON and none for the fixture
- [x] 4.5 `pre-commit run --all-files` passes with the repo config and the global markdown config
- [x] 4.6 `openspec validate --strict --all` passes
