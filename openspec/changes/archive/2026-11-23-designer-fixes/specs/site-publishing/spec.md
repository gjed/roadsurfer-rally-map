# Spec Delta

## MODIFIED Requirements

### Requirement: Scheduled publish

The workflow `.github/workflows/scan.yml` SHALL run the scanner twice a week on a
schedule and on manual dispatch, with `--delay 5`, and deploy the generated map to
GitHub Pages. After the scan it SHALL render the page from the scan's data file with
the latest release tag it can read, or without one. Its deploy job SHALL use the
concurrency group `pages` without cancelling a run in progress, and the workflow SHALL grant only `contents: read` outside the deploy job.

#### Scenario: Scheduled run

- **WHEN** the schedule fires on Monday or Thursday
- **THEN** the workflow scans with `--delay 5` and deploys the new map to GitHub Pages

#### Scenario: Manual run

- **WHEN** a maintainer dispatches the workflow
- **THEN** it scans and deploys the same way as a scheduled run

#### Scenario: Version kept between releases

- **WHEN** a scheduled scan runs after release `v1.3.0` was published
- **THEN** the deployed page shows `v1.3.0` in its map attribution

#### Scenario: No release yet

- **WHEN** a scheduled scan runs before any release exists
- **THEN** the deployed page shows no release tag and the workflow succeeds

#### Scenario: Release lookup fails

- **WHEN** the latest release cannot be read after a successful scan
- **THEN** the page is rendered without a release tag, a warning is logged, and
  the page and the `offers` artifact are still published

### Requirement: Release deploy

When `release.yml` publishes a release, it SHALL render the page with `--from-json`
from the newest unexpired `offers` artifact of a `scan.yml` run on `main`, whether
or not that run's deploy job has finished, with the new release tag, assemble the Pages artifact as `scan.yml` does, and deploy it from a
job that needs the release job, runs only when a release was published, has
`pages: write` and `id-token: write`, and uses the concurrency group `pages` without
cancelling a run in progress.

#### Scenario: Release redeploys the page

- **WHEN** release `v1.3.0` is published
- **THEN** the page is redeployed with the offers and scan time of the last scan and
  `v1.3.0` in its map attribution

#### Scenario: Scan deploy still queued

- **WHEN** a release is published while the deploy job of a scan that uploaded its
  `offers` artifact is still queued or running
- **THEN** the release deploy renders that scan's offers, not an older scan's

#### Scenario: No release, no deploy

- **WHEN** a push to `main` creates no release
- **THEN** nothing is rendered or deployed
