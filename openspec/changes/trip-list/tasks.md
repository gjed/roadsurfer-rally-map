# Tasks

## 1. Map page

- [x] 1.1 Add a map/list toggle to the toolbar that swaps the map for the list without touching the filters
- [x] 1.2 Build the list from the trips that pass the filters, in the same `render()` pass as the map and `#count`
- [x] 1.3 Show start, end, from (cc), to (cc), distance, price when present and an escaped booking link per row
- [x] 1.4 Sort by start date by default and re-sort by start, end and distance from the headers
- [x] 1.5 Selecting a row switches to the map, fits the route and opens its popup
- [x] 1.6 Keep the list usable at 375 px

## 2. Documentation

- [x] 2.1 Describe the list view in the README

## 3. Validation

- [x] 3.1 `make test` and an offline `make map` from the fixture pass
- [x] 3.2 Headless Chrome on a real-data page at 1280 px and 375 px: toggle, filters, row count against `#count`, sorting, row selection, booking link
- [x] 3.3 `pre-commit run --all-files` passes with the repo config and the global markdown config
- [x] 3.4 `openspec validate --strict --all` passes
