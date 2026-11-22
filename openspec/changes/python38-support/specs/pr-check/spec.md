# pr-check

## MODIFIED Requirements

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

### Requirement: Unit tests

The build check SHALL run unit tests of the scanner's pure helpers: station
resolution, booking-link building, page rendering with escaping of `</`, the
date-window filter with the API client replaced, and the `--from-json` error paths.
A separate check SHALL install Python 3.8, the minimum supported version, and on it
byte-compile the scanner, run `--help`, run the unit tests and render the fixture
without network access.

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
