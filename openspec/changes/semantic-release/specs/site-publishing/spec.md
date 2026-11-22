# site-publishing

## MODIFIED Requirements

### Requirement: Scheduled publish

The workflow `.github/workflows/scan.yml` SHALL run the scanner twice a week on a
schedule and on manual dispatch, with `--delay 5`, and deploy the generated map to
GitHub Pages. After the scan it SHALL render the page from the scan's data file with
the latest published release tag, or without a tag when no release exists. Its deploy
job SHALL use the concurrency group `pages` without cancelling a run in progress, and
the workflow SHALL grant only `contents: read` outside the deploy job.

#### Scenario: Scheduled run

- **WHEN** the schedule fires on Monday or Thursday
- **THEN** the workflow scans with `--delay 5` and deploys the new map to GitHub Pages

#### Scenario: Manual run

- **WHEN** a maintainer dispatches the workflow
- **THEN** it scans and deploys the same way as a scheduled run

#### Scenario: Version kept between releases

- **WHEN** a scheduled scan runs after release `v1.3.0` was published
- **THEN** the deployed page shows `v1.3.0` in its footer

#### Scenario: No release yet

- **WHEN** a scheduled scan runs before any release exists
- **THEN** the deployed page has no release footer and the workflow succeeds

## ADDED Requirements

### Requirement: Release deploy

When `release.yml` publishes a release, it SHALL render the page with `--from-json`
from the `offers` artifact of the latest successful `scan.yml` run on `main`, with the
new release tag, assemble the Pages artifact as `scan.yml` does, and deploy it from a
job that needs the release job, runs only when a release was published, has
`pages: write` and `id-token: write`, and uses the concurrency group `pages` without
cancelling a run in progress.

#### Scenario: Release redeploys the page

- **WHEN** release `v1.3.0` is published
- **THEN** the page is redeployed with the offers and scan time of the last scan and
  `v1.3.0` in its footer

#### Scenario: No release, no deploy

- **WHEN** a push to `main` creates no release
- **THEN** nothing is rendered or deployed

### Requirement: No roadsurfer traffic on release

The release workflow SHALL NOT run the scanner without `--from-json` and SHALL NOT send
any request to `booking.roadsurfer.com`.

#### Scenario: Release deploy

- **WHEN** the release workflow renders the page
- **THEN** it renders only from the downloaded `offers.json`

### Requirement: Missing scan data on release

When no successful `scan.yml` run on `main` exists or its `offers` artifact cannot be
downloaded, the release workflow SHALL fail with an error that says the page was not
redeployed, SHALL deploy nothing and SHALL NOT scan.

#### Scenario: Artifact expired

- **WHEN** a release is published and the last successful scan's `offers` artifact
  has expired
- **THEN** the release job fails with an error, the release stays published and the
  published page is unchanged
