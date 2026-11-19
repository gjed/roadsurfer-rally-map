# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Self-contained map output`
- TO: `### Requirement: Map output`

## MODIFIED Requirements

### Requirement: Map output

With `--map FILE`, the scanner SHALL write an HTML file built from the
`rally-map.template.html` file next to the script, with the literal `/*DATA*/[]`
replaced by the JSON offer records, every `</` in the data escaped as `<\/`, and SHALL
print the number of offers on the map. The records SHALL come from the scan of the
same run or, with `--from-json`, from a data file. The page SHALL load Leaflet from
`vendor/leaflet/` next to it.

#### Scenario: Map from a clean clone

- **WHEN** the user runs `python3 roadsurfer-rally.py --map index.html` in a clean
  clone
- **THEN** `index.html` is written, the scanner prints `map (N offers)`, and git
  ignores `index.html`

#### Scenario: Map from a data file

- **WHEN** the user runs `python3 roadsurfer-rally.py --from-json offers.json --map index.html`
- **THEN** `index.html` embeds the records of `offers.json` and the scanner prints
  `map (N offers)` with the number of records in the file
