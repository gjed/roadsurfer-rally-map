# dependency-updates

## MODIFIED Requirements

### Requirement: Pre-commit hook updates

Renovate SHALL detect the hook revisions in `.pre-commit-config.yaml` and open update
PRs for them, except major updates of mdformat: `mdformat-tables` 1.0.0 requires
`mdformat<0.8`, so mdformat 1.x cannot be installed with it.

#### Scenario: Outdated hook

- **WHEN** a hook `rev` is older than the latest tag of its repository, and the update
  is not a major mdformat update
- **THEN** Renovate opens a PR that updates the `rev`

#### Scenario: mdformat major release

- **WHEN** a new major mdformat version is tagged
- **THEN** Renovate opens no PR for it
