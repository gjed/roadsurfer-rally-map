# Delta for pr-check

## MODIFIED Requirements

### Requirement: Map build from a fixture

The build check SHALL render the map and the feeds from a committed offers fixture in the
`--json-out` format, without network access, and SHALL fail unless the generated page
has the data placeholder replaced, an embedded script that parses as JavaScript, and
Leaflet loaded from `vendor/leaflet/` rather than a CDN, and unless every generated
feed parses as XML.

#### Scenario: Broken template JavaScript

- **WHEN** a pull request introduces a syntax error in the template's script
- **THEN** the build check fails

#### Scenario: Valid template

- **WHEN** the template and scanner are unchanged
- **THEN** the build check renders the fixture and passes

#### Scenario: Malformed feed

- **WHEN** a pull request makes the scanner write a feed that is not well-formed XML
- **THEN** the build check fails with an `::error::` line that names the file

### Requirement: Unit tests

The build check SHALL run unit tests of the scanner's pure helpers: station
resolution, booking-link building, page rendering with escaping of `</`, feed
rendering (parsing, entry counts, stable and unique ids, links, slugs and escaping),
the date-window filter with the API client replaced, and the `--from-json` error paths.
A separate check SHALL install Python 3.8, the minimum supported version, and on it
byte-compile the scanner, run `--help`, run the unit tests and render the fixture
and its feeds without network access.

#### Scenario: Broken Python

- **WHEN** a pull request breaks the rendering code
- **THEN** the unit tests fail and the build check fails

#### Scenario: Unreadable fixture

- **WHEN** `--from-json` is given a missing file, invalid JSON, or JSON without
  `offers`
- **THEN** the scanner exits non-zero

#### Scenario: Standard library newer than the minimum

- **WHEN** a pull request makes the scanner import `datetime.UTC`
- **THEN** the Python 3.8 check fails
