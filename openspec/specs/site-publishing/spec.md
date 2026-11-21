# site-publishing Specification

## Purpose

Refresh the rally map on a schedule and publish it to GitHub Pages, without
publishing the result of a blocked scan.

## Requirements

### Requirement: Scheduled publish

The workflow `.github/workflows/scan.yml` SHALL run the scanner twice a week on a
schedule and on manual dispatch, with `--delay 5`, and deploy the generated map to
GitHub Pages. It SHALL use the concurrency group `pages` without cancelling a run in
progress, and grant only `contents: read` outside the deploy job.

#### Scenario: Scheduled run

- **WHEN** the schedule fires on Monday or Thursday
- **THEN** the workflow scans with `--delay 5` and deploys the new map to GitHub Pages

#### Scenario: Manual run

- **WHEN** a maintainer dispatches the workflow
- **THEN** it scans and deploys the same way as a scheduled run

### Requirement: Published site contents

The Pages artifact SHALL contain the generated `index.html` and a copy of `vendor/`
next to it, and nothing else from the repository.

#### Scenario: Published page loads Leaflet

- **WHEN** the deployed page is opened
- **THEN** it loads Leaflet from `vendor/leaflet/` on the same site

### Requirement: Scan data artifact

The workflow SHALL upload the scan's `--json-out` file as a workflow artifact named
`offers`.

#### Scenario: Data available after a run

- **WHEN** the build job succeeds
- **THEN** the run has an artifact named `offers` holding `offers.json`

### Requirement: No deploy after a failed scan

The deploy job SHALL run only after the build job succeeds.

#### Scenario: Blocked scan

- **WHEN** the scanner exits non-zero or the build job times out
- **THEN** the deploy job does not run and the published page stays unchanged
