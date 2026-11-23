# Proposal

## Why

The road distance cache from [#7](https://github.com/gjed/roadsurfer-rally-map/issues/7)
lives only in the GitHub Actions cache. GitHub evicts an entry after 7 days without
use and when the repository goes over its cache limit, and then the next scan has to
route every station pair again, which is the load the cache exists to avoid. The cache
cannot be committed: `main` requires signed commits.
([#39](https://github.com/gjed/roadsurfer-rally-map/issues/39))

## What Changes

- `scan.yml` keeps the cache file in an S3 bucket in the maintainer's AWS account
  (`eu-central-1`, versioned, noncurrent versions expire after 30 days). The build
  job downloads it before the scan and uploads it after a scan that succeeded.
- The job authenticates with GitHub OIDC through `aws-actions/configure-aws-credentials`,
  pinned to a commit SHA, with a role that can read and write that one object. No
  long-lived keys. The bucket name and the role ARN are the Actions variables
  `ROAD_DISTANCE_CACHE_BUCKET` and `ROAD_DISTANCE_CACHE_ROLE_ARN`.
- The Actions cache stays as the fallback. The S3 copy wins when it can be read;
  otherwise the Actions cache copy is used; with neither, the scanner routes every
  pair as before.
- Any AWS failure (variables unset, authentication, network, access denied, upload)
  logs a warning and never fails or blocks the scan.
- Only the build job gets `id-token: write`.
- README and AGENTS.md describe where the cache lives, the fallback order, the
  rollback through object versions and the two variables.

Out of scope: the scanner, `release.yml` (it stays offline and never reads the
bucket), the bucket and the role (managed in `gjed/homelab-aws`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `site-publishing`: the scan workflow keeps the road distance cache in S3 with the
  Actions cache as the fallback, and its build job gets `id-token: write`.

## Impact

- `.github/workflows/scan.yml`, README.md, AGENTS.md. No scanner, test or
  dependency change.
