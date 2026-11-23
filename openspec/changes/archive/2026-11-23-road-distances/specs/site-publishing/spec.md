# Spec Delta

## ADDED Requirements

### Requirement: Road distance cache in the workflow

The scan workflow SHALL restore the road distance cache file with
`actions/cache/restore` before the scan, under the key `road-distances-<run id>` with
the restore key prefix `road-distances-`, and SHALL save it with `actions/cache/save`
under the same key after the scan step succeeded. It SHALL NOT save the cache after a
scan that failed or crashed, SHALL NOT commit the cache file or upload it as an
artifact, and SHALL keep `contents: read` as the only permission outside the deploy
job.

#### Scenario: Next scan reuses the cache

- **WHEN** a scan run succeeds and a later run starts
- **THEN** the later run restores the earlier run's cache and routes only the station
  pairs that are not in it

#### Scenario: Failed scan saves no cache

- **WHEN** the scan step exits non-zero
- **THEN** no cache is saved and the next run restores the last good one

### Requirement: No routing on release

The release workflow SHALL read road distances from the `offers` artifact and SHALL NOT
send any request to a routing server.

#### Scenario: Release shows stored distances

- **WHEN** the release workflow renders the page
- **THEN** the page shows the distances stored in the downloaded `offers.json`
