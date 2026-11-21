# developer-tooling

## ADDED Requirements

### Requirement: Make targets

The repository SHALL provide a `Makefile` with the targets `help`, `scan`, `map`,
`serve`, `lint` and `test`. `help` SHALL be the default goal and SHALL list every
target with a one-line description, without running anything else.

#### Scenario: Bare make

- **WHEN** a contributor runs `make` with no target
- **THEN** the target list is printed and no scan, render or server starts

### Requirement: Scan target

`make scan` SHALL run a full scan at the scanner's default delay and write the offers
to `offers.json` in the repository root with `--json-out`. Git SHALL ignore that file.

#### Scenario: Scan

- **WHEN** a contributor runs `make scan`
- **THEN** the scanner runs with `--json-out offers.json` and the file is not shown
  as untracked by git

### Requirement: Offline map target

`make map` SHALL render `index.html` in the repository root with `--from-json`,
without network access. It SHALL read `offers.json` when it exists, and otherwise
SHALL render `tests/fixtures/offers.json` and print a note that it used the fixture.

#### Scenario: Map after a scan

- **WHEN** `offers.json` exists and a contributor runs `make map`
- **THEN** `index.html` is rendered from `offers.json` without any network request

#### Scenario: Map from a clean clone

- **WHEN** `offers.json` does not exist and a contributor runs `make map` offline
- **THEN** `index.html` is rendered from `tests/fixtures/offers.json` and a note
  names the fixture and `make scan`

### Requirement: Serve, lint and test targets

`make serve` SHALL serve the repository root with `python3 -m http.server` on the
loopback interface, so the page finds `vendor/` next to it. `make lint` SHALL run
`pre-commit run --all-files`. `make test` SHALL run
`python3 -m unittest discover -s tests -v`, the command the PR check runs.

#### Scenario: Tests from a clean clone

- **WHEN** a contributor runs `make test` in a clean clone without network access
- **THEN** the unit tests run and the target fails if any test fails
