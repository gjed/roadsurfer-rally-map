# rally-scanner Specification

## Purpose

Find roadsurfer Rally one-way relocation offers through the unofficial booking API
and present them as a list and as a self-contained HTML map.

## Requirements

### Requirement: Polite API access

The scanner SHALL send every request to `https://booking.roadsurfer.com/api/en` with
an `X-Requested-Alias` header that matches the route. It SHALL send requests one at a
time, wait a configurable delay before each request (0.5 s by default), and retry
with backoff when the API answers HTTP 429.

#### Scenario: Default scan pacing

- **WHEN** the scanner runs without `--delay`
- **THEN** requests are sent sequentially, at least 0.5 s apart

#### Scenario: Rate limited

- **WHEN** a request fails with HTTP 429
- **THEN** the scanner waits longer before each retry and gives up after five attempts

### Requirement: Offer listing

The scanner SHALL list every rally timeframe that overlaps the requested window,
optionally filtered by origin and destination stations, and print the number of
offers found and one booking link per offer.

#### Scenario: Full scan

- **WHEN** the user runs `python3 roadsurfer-rally.py`
- **THEN** the scanner prints a line with the offer count, then each offer and its
  booking link

### Requirement: Self-contained map output

With `--map FILE`, the scanner SHALL write an HTML file built from the
`rally-map.template.html` file next to the script, with the literal `/*DATA*/[]`
replaced by the JSON offer records, and SHALL print the number of offers on the map.

#### Scenario: Map from a clean clone

- **WHEN** the user runs `python3 roadsurfer-rally.py --map index.html` in a clean
  clone
- **THEN** `index.html` is written, the scanner prints `map (N offers)`, and git
  ignores `index.html`
