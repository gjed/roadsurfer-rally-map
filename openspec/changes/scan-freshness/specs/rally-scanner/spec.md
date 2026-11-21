# Spec Delta

## MODIFIED Requirements

### Requirement: Map output

With `--map FILE`, the scanner SHALL write an HTML file from
`rally-map.template.html` next to the script, replacing `/*DATA*/[]` with the JSON
offer records and `/*SCAN*/null` with the JSON scan metadata or `null`, escaping
every embedded `</` as `<\/`, and SHALL print the number of offers on the map. Both
SHALL come from the scan of the same run or, with `--from-json`, from a data file.
The page SHALL load Leaflet from `vendor/leaflet/` next to it.

#### Scenario: Map from a clean clone

- **WHEN** the user runs `python3 roadsurfer-rally.py --map index.html` in a clean
  clone
- **THEN** `index.html` is written, the scanner prints `map (N offers)`, and git
  ignores `index.html`

#### Scenario: Map from a data file

- **WHEN** the user runs `python3 roadsurfer-rally.py --from-json offers.json --map index.html`
- **THEN** `index.html` embeds the records and the `scan` object of `offers.json` and
  the scanner prints `map (N offers)` with the number of records in the file

#### Scenario: Data file without metadata

- **WHEN** the user renders with `--from-json` a data file that has no `scan` object
- **THEN** `index.html` is written and embeds `null` as the scan metadata

### Requirement: Scan data file

With `--json-out FILE`, the scanner SHALL write a UTF-8 JSON object whose `offers` key
holds the same offer records that `--map` embeds in the page, and whose `scan` key
holds the scan metadata: `finished_at` (UTC, ISO 8601), `offers`, `requests`,
`failed`, `rate_limited`, `start`, `end`, `from` and `to`.

#### Scenario: Scan to a data file

- **WHEN** the user runs `python3 roadsurfer-rally.py --from 1 --json-out offers.json`
- **THEN** `offers.json` holds an object whose `offers` list has one record per listed
  offer and whose `scan` object has the finish time such as `2026-11-18T03:12:05Z`,
  the number of offers, the request, failed and HTTP 429 counts the summary prints,
  the `--start` and `--end` window, `from` set to `["1"]` and `to` set to `null`

## ADDED Requirements

### Requirement: Last-updated timestamp

When the map page has scan metadata, its toolbar SHALL show the time the scan
finished, in UTC to the minute. Without scan metadata it SHALL show no timestamp.

#### Scenario: Page with scan metadata

- **WHEN** a page whose scan finished at `2026-11-18T03:12:05Z` is opened
- **THEN** its toolbar shows `updated 2026-11-18 03:12 UTC`

#### Scenario: Page without scan metadata

- **WHEN** a page rendered from a data file without a `scan` object is opened
- **THEN** its toolbar shows the route and trip counts and no timestamp
