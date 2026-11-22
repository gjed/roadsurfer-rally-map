# Tasks

## 1. Scanner and page

- [x] 1.1 Add `--release TAG` (requires `--map`) and embed it through a `/*RELEASE*/null` placeholder with the `</` escaping
- [x] 1.2 Show the tag in a `#release` footer linked to the GitHub release, hidden without a tag
- [x] 1.3 Unit tests for the render with and without a tag, the escaping and the CLI option

## 2. Release workflow

- [x] 2.1 Add `.releaserc.json` (branch `main`, tag `v${version}`, commit-analyzer, release-notes-generator, github)
- [x] 2.2 Add `release.yml`: semantic-release job, offline render from the last successful scan's `offers` artifact, deploy job
- [x] 2.3 Fail the release job with an error when the scan data is missing; never scan

## 3. Scheduled scan

- [x] 3.1 Split the scan and the render in `scan.yml` and render with the latest release tag, tolerating no release
- [x] 3.2 Move the `pages` concurrency group to the deploy jobs

## 4. Documentation

- [x] 4.1 README "Published map": releases, the release deploy and the footer
- [x] 4.2 AGENTS.md: how releases are cut, which commit types release, first release v1.0.0

## 5. Validation

- [x] 5.1 `make test`, and the unit tests on Python 3.8
- [x] 5.2 actionlint on the changed workflows
- [x] 5.3 semantic-release dry run computes the next version
- [x] 5.4 The release job's render steps run offline on the last scan's `offers` artifact, with and without a tag
- [x] 5.5 `make lint`, the global markdown config and `openspec validate --strict --all` pass
