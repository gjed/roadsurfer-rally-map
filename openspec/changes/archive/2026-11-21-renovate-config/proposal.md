# Proposal

## Why

Nothing keeps the repository's pinned versions current: the GitHub Actions in the
workflows, the pre-commit hook revisions and the vendored Leaflet are updated only
when someone remembers
([#11](https://github.com/gjed/roadsurfer-rally-map/issues/11)). The other gjed
repositories use Renovate with the shared `gjed/renovate-config` preset.

## What Changes

- Add `.renovaterc.json`, extending `github>gjed/renovate-config:default` and
  `customManagers:githubActionsVersions`, like `gjed/songbooks`.
- Enable the `pre-commit` manager, which Renovate leaves off by default, so hook
  revisions in `.pre-commit-config.yaml` get update PRs.
- Add a regex custom manager on `vendor/leaflet/VERSION` (npm datasource, package
  `leaflet`). The repository's `ignorePaths` drops `**/vendor/**` from the preset
  list, which would otherwise hide that file from every manager.
- Leaflet PRs never automerge and carry a note: Renovate can only rewrite `VERSION`,
  so the maintainer runs the README update procedure on the PR branch before merging.
- README: say how a Renovate Leaflet PR is handled.

Out of scope: installing or configuring the Renovate app, branch protection, a CI
check that `VERSION` matches the vendored files.

## Capabilities

### New Capabilities

- `dependency-updates`: automated update PRs for actions, pre-commit hooks and the
  vendored Leaflet.

### Modified Capabilities

None.

## Impact

- New file `.renovaterc.json`; a README paragraph. No code change.
- Once the Renovate app runs on the repository, it opens an onboarding or update PR
  and a Dependency Dashboard issue.
