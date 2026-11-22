# rally-scanner

## MODIFIED Requirements

### Requirement: Map output

With `--map FILE`, the scanner SHALL write an HTML file from
`rally-map.template.html` next to the script, replacing `/*DATA*/[]` with the JSON
offer records, `/*SCAN*/null` with the JSON scan metadata or `null`, and
`/*RELEASE*/null` with the `--release` tag as a JSON string or `null`, escaping
every embedded `</` as `<\/`, and SHALL print the number of offers on the map. The
records and the metadata SHALL come from the scan of the same run or, with
`--from-json`, from a data file. `--release` SHALL require `--map`. The page SHALL
load Leaflet from `vendor/leaflet/` next to it.

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

#### Scenario: Map with a release tag

- **WHEN** the user runs
  `python3 roadsurfer-rally.py --from-json offers.json --map index.html --release v1.3.0`
- **THEN** `index.html` embeds `"v1.3.0"` as the release tag

#### Scenario: Map without a release tag

- **WHEN** the user renders without `--release`
- **THEN** `index.html` embeds `null` as the release tag

## ADDED Requirements

### Requirement: Release footer

When the map page has a release tag, it SHALL show the tag in a footer with the id
`release`, linked to the GitHub release of that tag. Without a release tag the page
SHALL show no footer.

#### Scenario: Page with a release tag

- **WHEN** a page rendered with `--release v1.3.0` is opened
- **THEN** its footer shows `v1.3.0`, linked to
  `https://github.com/gjed/roadsurfer-rally-map/releases/tag/v1.3.0`

#### Scenario: Page without a release tag

- **WHEN** a page rendered without `--release` is opened
- **THEN** it shows no footer
