# Tasks

## 1. Configuration

- [x] 1.1 Add `.renovaterc.json` extending `github>gjed/renovate-config:default` and `customManagers:githubActionsVersions`
- [x] 1.2 Enable the `pre-commit` manager and set `ignorePaths` to the preset list minus `**/vendor/**`
- [x] 1.3 Add the regex manager on `vendor/leaflet/VERSION` and the Leaflet packageRule (no automerge, PR body note)

## 2. Documentation

- [x] 2.1 README "Vendored Leaflet": how a Renovate Leaflet PR is handled

## 3. Validation

- [x] 3.1 `renovate-config-validator --strict` passes
- [x] 3.2 A local `--platform=local` dry run detects the actions, the pre-commit hooks and Leaflet, and proposes a non-automerged Leaflet branch when `VERSION` is older
- [x] 3.3 `pre-commit run --all-files` (repo and global markdown config) and `openspec validate --strict --all` pass
