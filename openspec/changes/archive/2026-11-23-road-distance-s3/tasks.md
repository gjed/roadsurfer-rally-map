# Tasks

## 1. Workflow

- [x] 1.1 Grant the build job `id-token: write` and `contents: read`; leave the
  workflow permissions and the deploy job as they are.
- [x] 1.2 Add the credentials step (`aws-actions/configure-aws-credentials`, pinned,
  role from `ROAD_DISTANCE_CACHE_ROLE_ARN`, `eu-central-1`), skipped when a variable is
  unset and never failing the job.
- [x] 1.3 Add the S3 download after the Actions cache restore, so S3 wins when it
  has the file; warn and continue on any failure.
- [x] 1.4 Add the S3 upload after the Scan step, only when the file exists; warn and
  continue on failure. Keep the Actions cache save.
- [x] 1.5 Check each new step's shell against a stub `aws`: object present, object
  missing, access denied, upload failure.

## 2. Docs

- [x] 2.1 README: cache location, fallback order, rollback through object versions,
  the two Actions variables.
- [x] 2.2 AGENTS.md: the cache location in the rate limit notes.
