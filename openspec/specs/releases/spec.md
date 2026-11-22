# releases Specification

## Purpose

Cut versioned GitHub releases from `main` with semantic-release, from the Conventional
Commits since the last tag, without committing back to `main`.

## Requirements

### Requirement: Versioned releases from main

The workflow `.github/workflows/release.yml` SHALL run semantic-release on every push
to `main`, configured by `.releaserc.json` with the branch `main`, the tag format
`v${version}` and the plugins commit-analyzer, release-notes-generator and github.
A push whose new commits include a `feat`, `fix` or `perf` commit SHALL create the tag
`vX.Y.Z` and a GitHub release with generated notes; other commit types SHALL create
neither.

#### Scenario: Feature merged

- **WHEN** a `feat:` commit is pushed to `main` after release `v1.2.3`
- **THEN** the workflow creates the tag `v1.3.0` and a GitHub release `v1.3.0`

#### Scenario: Documentation merged

- **WHEN** only `docs:` or `chore:` commits are pushed to `main`
- **THEN** no tag and no release are created

#### Scenario: First release

- **WHEN** the first release is cut from a history with no tag and no breaking commit
- **THEN** its tag is `v1.0.0`

### Requirement: No commits from the release

The release SHALL NOT push commits to any branch: no changelog file, no version file
and no release assets.

#### Scenario: Release published

- **WHEN** a release is published
- **THEN** `main` has the same head as before and only the tag and the GitHub release
  are new

### Requirement: Release permissions

The release job SHALL have only `contents: write`, `issues: write`,
`pull-requests: write` and `actions: read`, and SHALL run in a concurrency group that
does not cancel a run in progress.

#### Scenario: Two quick pushes

- **WHEN** two pushes to `main` arrive while semantic-release is running
- **THEN** semantic-release runs once at a time and the last push is released
