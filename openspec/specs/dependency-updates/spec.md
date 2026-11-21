# dependency-updates Specification

## Purpose

Keep the pinned versions current with Renovate: the GitHub Actions in the workflows,
the pre-commit hook revisions and the vendored Leaflet, without letting a Leaflet bump
land with `VERSION` and the vendored files out of sync.

## Requirements

### Requirement: Renovate configuration

The repository SHALL have a Renovate configuration that extends the shared
`github>gjed/renovate-config:default` preset and `customManagers:githubActionsVersions`.

#### Scenario: Outdated action

- **WHEN** a workflow in `.github/workflows/` pins an action version older than the
  latest release
- **THEN** Renovate opens a PR that updates it

### Requirement: Pre-commit hook updates

Renovate SHALL detect the hook revisions in `.pre-commit-config.yaml` and open update
PRs for them.

#### Scenario: Outdated hook

- **WHEN** a hook `rev` is older than the latest tag of its repository
- **THEN** Renovate opens a PR that updates the `rev`

### Requirement: Vendored Leaflet updates

Renovate SHALL read the vendored Leaflet version from `vendor/leaflet/VERSION`, look it
up as the npm package `leaflet`, and open a PR when a newer stable version exists. A
Leaflet PR SHALL NOT be automerged and SHALL tell the maintainer to run the README
update procedure on its branch.

#### Scenario: New Leaflet release

- **WHEN** npm has a stable `leaflet` version newer than `vendor/leaflet/VERSION`
- **THEN** Renovate opens a PR that bumps `VERSION`, is not automerged, and whose body
  points to the README "Vendored Leaflet" procedure

#### Scenario: Leaflet prerelease

- **WHEN** npm has only prerelease versions newer than the vendored stable version
- **THEN** Renovate opens no Leaflet PR
