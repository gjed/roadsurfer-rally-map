# pr-check Specification

## Purpose

Validate every pull request offline: lint all files, run the scanner's unit tests
and build the map from a committed fixture, without contacting the roadsurfer API.

## Requirements

### Requirement: Offline pull request validation

Every pull request SHALL be validated automatically, with read-only repository
permissions and without secrets. No validation step SHALL send a request to
`booking.roadsurfer.com`.

#### Scenario: Pull request opened

- **WHEN** a pull request is opened or updated
- **THEN** the lint and build checks run against its head

#### Scenario: No roadsurfer traffic

- **WHEN** the checks run
- **THEN** no step contacts `booking.roadsurfer.com`

### Requirement: Lint

The lint check SHALL run the repository's pre-commit hooks on all files, including the
Python linter and formatter and the Markdown linters, and SHALL fail when any hook
fails or changes a file. The Python linter and formatter SHALL target the minimum
supported Python version, so they never suggest newer syntax or standard library
names.

#### Scenario: Unformatted Python

- **WHEN** a pull request contains Python that ruff would reformat
- **THEN** the lint check fails and shows the diff

#### Scenario: Syntax newer than the minimum

- **WHEN** a pull request uses syntax that Python 3.8 cannot parse
- **THEN** the lint check fails

#### Scenario: Version-specific rewrite

- **WHEN** the code uses `timezone.utc`
- **THEN** ruff does not ask to replace it with `datetime.UTC`

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
rendering (parsing, ids, links, slugs, escaping), the date-window filter with the API
client replaced, and the `--from-json` error paths.
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

### Requirement: Actionable failures

Every failing validation step SHALL print a GitHub `::error::` annotation that names
what failed and how to fix or reproduce it locally.

#### Scenario: Failed step

- **WHEN** a validation step fails
- **THEN** the run log contains an `::error::` line describing the fix

### Requirement: App bar feed link check

The build check SHALL fail unless the generated page links `feeds/all.xml` from the app
bar with `class="fdbtn" href="feeds/all.xml"`, besides the link in `<head>`.

#### Scenario: Feed button removed

- **WHEN** a pull request removes the app bar feed link from the template
- **THEN** the build check fails
