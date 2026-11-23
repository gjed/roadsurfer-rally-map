# Spec Delta

## MODIFIED Requirements

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

## ADDED Requirements

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

### Requirement: Scans do not overlap

The build job of the scan workflow SHALL use the concurrency group
`road-distance-scan` without cancelling a run in progress, so that two scans never
write the road distance cache at the same time. The group SHALL NOT be `pages`, which
only the deploy jobs share.

#### Scenario: Dispatch during a scheduled scan

- **WHEN** a maintainer dispatches the workflow while a scan is running
- **THEN** the new run waits until the running scan has finished, and the running scan
  is not cancelled

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
