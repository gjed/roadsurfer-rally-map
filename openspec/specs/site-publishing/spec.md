# site-publishing Specification

## Purpose

Refresh the rally map on a schedule and publish it to GitHub Pages, without
publishing the result of a blocked scan.

## Requirements

### Requirement: Scheduled publish

The workflow `.github/workflows/scan.yml` SHALL run the scanner twice a week on a
schedule and on manual dispatch, with `--delay 5`, and deploy the generated map to
GitHub Pages. After the scan it SHALL render the page from the scan's data file with
the latest release tag it can read, or without one. Its deploy job SHALL use the
concurrency group `pages` without cancelling a run in progress, and the workflow SHALL
grant only `contents: read` outside the deploy and build jobs.

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

### Requirement: No roadsurfer traffic on release

The release workflow SHALL NOT run the scanner without `--from-json` and SHALL NOT send
any request to `booking.roadsurfer.com`.

#### Scenario: Release deploy

- **WHEN** the release workflow renders the page
- **THEN** it renders only from the downloaded `offers.json`

### Requirement: Missing scan data on release

When no unexpired `offers` artifact from a `scan.yml` run on `main` exists or it
cannot be downloaded, the release workflow SHALL fail with an error that says the page was not
redeployed, SHALL deploy nothing and SHALL NOT scan.

#### Scenario: Artifact expired

- **WHEN** a release is published and the newest `offers` artifact from `main` has
  expired
- **THEN** the release job fails with an error, the release stays published and the
  published page is unchanged

### Requirement: Road distance cache in the workflow

The scan workflow SHALL restore the road distance cache file with
`actions/cache/restore` before the scan, under the key `road-distances-<run id>` with
the restore key prefix `road-distances-`, then download the S3 object
`road-distances.json` over it when it can be read. After the scan step succeeded it
SHALL upload the file to S3 when it exists and save it with `actions/cache/save` under
the same key, and SHALL do neither after a scan that failed or crashed.

#### Scenario: Next scan reuses the cache

- **WHEN** a scan run succeeds and a later run starts
- **THEN** the later run restores the earlier run's cache and routes only the station
  pairs that are not in it

#### Scenario: Failed scan saves no cache

- **WHEN** the scan step exits non-zero
- **THEN** no cache is saved or uploaded and the next run restores the last good one

#### Scenario: S3 copy preferred

- **WHEN** the Actions cache and the S3 bucket both have the file
- **THEN** the scan runs with the S3 copy

#### Scenario: Actions cache evicted

- **WHEN** the Actions cache entry is gone and the S3 bucket has the file
- **THEN** the scan runs with the S3 copy and routes only the pairs not in it

### Requirement: No routing on release

The release workflow SHALL read road distances from the `offers` artifact and SHALL NOT
send any request to a routing server.

#### Scenario: Release shows stored distances

- **WHEN** the release workflow renders the page
- **THEN** the page shows the distances stored in the downloaded `offers.json`

### Requirement: Chains from the published data

The published page SHALL compute rally chains in the browser from the offers it
embeds. Neither `scan.yml` nor `release.yml` SHALL send an additional request, run an
additional step or store additional data for chains, and a page rendered from a data
file written by an earlier scan SHALL offer chains too.

#### Scenario: Release from an older artifact

- **WHEN** `release.yml` renders the page from an `offers` artifact written before
  chains existed
- **THEN** the deployed page offers chains and the release job sends no request to
  roadsurfer or to a routing server

### Requirement: AWS access of the road distance cache

The S3 bucket SHALL be the one named by the Actions variable
`ROAD_DISTANCE_CACHE_BUCKET`. The build job, and not the deploy job, SHALL
authenticate with GitHub OIDC through `aws-actions/configure-aws-credentials`, pinned
to a commit SHA, assuming the role in `ROAD_DISTANCE_CACHE_ROLE_ARN` in `eu-central-1`,
and SHALL grant `contents: read` and `id-token: write`. The workflow SHALL NOT use
long-lived AWS keys, commit the cache file or upload it as an artifact.

#### Scenario: Variables unset

- **WHEN** `ROAD_DISTANCE_CACHE_BUCKET` or `ROAD_DISTANCE_CACHE_ROLE_ARN` is not set
- **THEN** the AWS steps are skipped and the scan uses the Actions cache only

### Requirement: AWS failures never block the scan

A failure of any AWS step (credentials, network, access denied, download or upload)
SHALL log a warning and SHALL NOT fail or block the scan. A missing S3 object on
download is not a failure.

#### Scenario: Bucket empty or unreachable

- **WHEN** the S3 object does not exist, or authentication, the network or the
  download fails
- **THEN** the scan runs with the Actions cache copy, or with no cache when there is
  none, and a failure other than a missing object logs a warning

#### Scenario: Upload fails

- **WHEN** the scan succeeded and the S3 upload fails
- **THEN** a warning is logged, the Actions cache is still saved and the run goes on
