# Delta for site-publishing

## MODIFIED Requirements

### Requirement: Published site contents

The Pages artifact SHALL contain the generated `index.html`, a copy of `vendor/` and the
generated `feeds/` directory next to it, and nothing else from the repository.

#### Scenario: Published page loads Leaflet

- **WHEN** the deployed page is opened
- **THEN** it loads Leaflet from `vendor/leaflet/` on the same site

#### Scenario: Published feeds

- **WHEN** the site is deployed
- **THEN** `feeds/all.xml` and one `feeds/from-<slug>.xml` per pick-up station are
  served next to `index.html`, and the page's `<head>` links `feeds/all.xml`

### Requirement: Release deploy

When `release.yml` publishes a release, it SHALL render the page and the feeds with
`--from-json` from the newest unexpired `offers` artifact of a `scan.yml` run on
`main`, whether or not that run's deploy job has finished, with the new release tag,
assemble the Pages artifact as `scan.yml` does, and deploy it from a
job that needs the release job, runs only when a release was published, has
`pages: write` and `id-token: write`, and uses the concurrency group `pages` without
cancelling a run in progress.

#### Scenario: Release redeploys the page

- **WHEN** release `v1.3.0` is published
- **THEN** the page is redeployed with the offers and scan time of the last scan and
  `v1.3.0` in its map attribution, and the feeds are redeployed with the same offers

#### Scenario: Scan deploy still queued

- **WHEN** a release is published while the deploy job of a scan that uploaded its
  `offers` artifact is still queued or running
- **THEN** the release deploy renders that scan's offers, not an older scan's

#### Scenario: No release, no deploy

- **WHEN** a push to `main` creates no release
- **THEN** nothing is rendered or deployed

## ADDED Requirements

### Requirement: Feeds from the scan data

After the scan, `scan.yml` SHALL render the feeds with `--feeds feeds` in the same
`--from-json` run that renders the page, so that the page and the feeds come from one
scan. Neither `scan.yml` nor `release.yml` SHALL send an additional request, or need
an additional secret or permission, for the feeds. The feeds of a scan that failed or
was blocked SHALL NOT be deployed.

#### Scenario: Feeds in step with the page

- **WHEN** a scheduled scan succeeds
- **THEN** the deployed page and the deployed feeds are rendered from the same
  `offers.json`

#### Scenario: Blocked scan

- **WHEN** the scanner exits non-zero
- **THEN** the deploy job does not run and the published feeds stay unchanged
