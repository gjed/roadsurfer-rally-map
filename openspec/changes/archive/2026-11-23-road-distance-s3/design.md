# Design

## Context

`scan.yml` restores `road-distances.json` from `actions/cache` before the scan and
saves it after a successful scan. The bucket `gjed-roadsurfer-rally-map-cache` and
the OIDC role `roadsurfer-rally-map-cache` exist in `gjed/homelab-aws` (versioned,
noncurrent versions expire after 30 days). The role trusts only
`repo:gjed/roadsurfer-rally-map:ref:refs/heads/main` and may `GetObject` and
`PutObject` the key `road-distances.json` and `ListBucket` the bucket.

## Goals / Non-Goals

**Goals:**

- A cache that survives Actions cache eviction.
- A failed scan uploads nothing; an AWS problem never blocks a scan.

**Non-Goals:**

- Changing the scanner, the cache format or `release.yml`.
- Managing the bucket or the role.

## Decisions

- **Restore order: Actions cache first, then S3 overwrites.** Both restores write
  `road-distances.json`. Restoring the Actions cache first and downloading S3 over it
  means a successful S3 download wins by construction and a failed one leaves the
  Actions copy untouched. The reverse order would need a check before each step.
  The download goes to a temporary name and is moved into place only on success, so a
  failed download never leaves a half-written file over the Actions copy.
- **AWS steps in the build job, not in deploy.** The deploy job uses the
  `github-pages` environment, which changes the OIDC `sub` claim the role trusts.
  `id-token: write` is granted on the build job only; the workflow keeps
  `contents: read` and the deploy job keeps its own permissions.
- **Never fail the scan.** The credentials step runs with `continue-on-error`, and
  the download and upload steps catch the `aws` exit status, log `::warning::` and
  exit 0. A failed credentials step logs a warning step of its own. Later AWS steps
  run only when the credentials step succeeded, so a fork or a repository without
  the variables skips them cleanly. One cost: the action reports its own failure as
  an error annotation even though the job stays green.
- **Missing object is not a warning.** On the first run the key does not exist and
  `aws s3 cp` fails with a 404 (the role has `ListBucket`, so S3 does not answer
  403). The download step logs a notice for that; any other failure, including
  access denied or missing credentials, is a warning.
- **Upload after the scan, before the Actions cache save.** Same condition as the
  Actions cache save today: only after the Scan step succeeded, so a blocked or
  crashed scan uploads nothing. It runs only when the file exists. It comes before
  the Actions cache save so a failure there cannot skip it.
- **One scan at a time.** The upload is a plain `aws s3 cp`, last write wins, so two
  overlapping scans (a dispatch during the 70-90 minute scheduled run) would make one
  drop the pairs the other routed. The build job gets its own concurrency group,
  `road-distance-scan`, with `cancel-in-progress: false`; the deploy jobs keep `pages`.
  GitHub keeps at most one waiting run per group and cancels an older waiting one in
  favour of a newer one, which costs nothing here because the newer run scans anyway.
- **Actions cache stays.** It is the fallback and costs nothing. No change to its key
  or restore key.
- **Variables through `env`, not inline in the script.** The bucket name is passed as
  an environment variable instead of being interpolated into the shell.
- **Pinned action.** `aws-actions/configure-aws-credentials` is pinned to a full
  commit SHA with the version in a comment, like the other third-party actions;
  Renovate keeps it current.
- **Rollback.** The bucket is versioned: restoring a bad write means copying a
  previous object version back (`aws s3api list-object-versions`, then
  `aws s3api get-object --version-id` and `aws s3 cp`). Noncurrent versions expire
  after 30 days.

## Risks / Trade-offs

- The role trusts only `main`, so the workflow cannot be exercised from a branch. The
  step scripts are tested against a stub `aws`, and the first dispatch on `main`
  proves the real path.
- A corrupt object in the bucket is read as an empty cache by the scanner, so it
  costs a full route, not a failed scan.
