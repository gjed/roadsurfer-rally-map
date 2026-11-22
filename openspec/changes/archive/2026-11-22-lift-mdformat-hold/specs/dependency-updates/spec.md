# dependency-updates

## REMOVED Requirements

### Requirement: Pre-commit hook updates

**Reason**: Its mdformat exception and the "mdformat major release" scenario no longer
apply. A MODIFIED delta cannot drop a scenario, so the requirement is replaced by
"Pre-commit hook revision updates".

**Migration**: None. The replacement requirement covers every hook, mdformat included.

## ADDED Requirements

### Requirement: Pre-commit hook revision updates

Renovate SHALL detect the hook revisions in `.pre-commit-config.yaml` and open update
PRs for them.

#### Scenario: Outdated hook

- **WHEN** a hook `rev` is older than the latest tag of its repository
- **THEN** Renovate opens a PR that updates the `rev`
