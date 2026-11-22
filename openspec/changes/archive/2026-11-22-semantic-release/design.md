# Design

## Context

`scan.yml` scans twice a week, renders `index.html` in the same run, deploys it and
keeps `offers.json` as the artifact `offers` (90-day retention). The whole workflow
sits in the concurrency group `pages`. `render(records, path, scan)` fills
`/*DATA*/[]` and `/*SCAN*/null` in the template. `main` is protected by a ruleset
that requires signed commits and linear history; it targets branches only.

## Goals / Non-Goals

**Goals:**

- Version `main` from Conventional Commits and redeploy the page on each release.
- Show the release tag on the page, and keep it there across scheduled scans.
- No request to roadsurfer from the release workflow.

**Non-Goals:**

- A changelog file, a version file, release assets, an npm package.

## Decisions

- **Plugins: commit-analyzer, release-notes-generator, github, without assets.**
  The git and npm plugins would push a commit to `main`, which the ruleset rejects
  (unsigned) and the project does not need. The tag that semantic-release pushes is
  not covered by the branch ruleset.
- **First release is v1.0.0.** semantic-release always starts at 1.0.0 and no commit
  in the history is marked breaking. Later `feat` commits bump the minor version,
  `fix` and `perf` the patch; `docs`, `chore`, `ci`, `build`, `style`, `refactor`
  and `test` cut no release.
- **Action pinned to a commit.** `cycjimmy/semantic-release-action` is third-party,
  so it is pinned to the v8.1.4 commit with a version comment for Renovate, as
  `pr-check.yml` does for `setup-uv`. semantic-release itself is held to major 24.
- **Data from the last successful scan on `main`.** The release job finds it with
  `gh run list --workflow scan.yml --branch main --status success --limit 1` and
  downloads its `offers` artifact with `gh run download`, which needs
  `actions: read`. A dispatched scan on another branch is not used.
- **No data: fail, do not skip and never scan.** If there is no successful scan or
  its artifact has expired, the release job fails with an `::error::` that says the
  release was published, the page was not redeployed, and how to fix it (dispatch
  `scan.yml`). A silent skip would leave the old version on the page with a green
  run. The release itself is already published at that point and stays.
- **Render steps in the release job.** As in songbooks, the build steps run in the
  release job after semantic-release, only when a release was published, and
  `deploy-site` deploys the Pages artifact.
- **`--release TAG` scanner option, `/*RELEASE*/null` placeholder.** The same
  mechanism as the scan metadata: `render()` embeds the tag as JSON with `</`
  escaped, or `null`. `--release` requires `--map`. The page shows it in a
  `<footer id="release">` below the map and the list, as a link to the GitHub release
  built with `textContent` and `encodeURIComponent`. The footer is hidden when empty,
  so an untagged page looks as before. The template change is kept to the
  placeholder, its read and one element, so the restyle in #27 can move it.
- **scan.yml renders after the scan, with the latest tag.** The scan step writes only
  `offers.json`; a render step then reads the tag with
  `gh release list --exclude-drafts --exclude-pre-releases --limit 1` and renders
  with `--from-json`. `gh release list` prints nothing when there is no release, so
  "no release yet" renders without a tag, while an API error still fails the step.
  Reading the tag after the 70 to 90 minute scan, not before it, picks up a release
  cut during the scan.
- **`pages` concurrency on the deploy jobs only.** GitHub keeps one pending run per
  concurrency group and cancels the older pending one. At workflow level a scan
  queued behind a running release (or the reverse) could cancel the other run, and a
  cancelled release run cuts no release until the next push. With the group on the
  two deploy jobs, the release job and the 90-minute scan never wait for each other,
  and two deploys never overlap. If a third deploy queues while one runs and one is
  pending, the pending one is replaced by a newer deploy, which is acceptable.
- **semantic-release in its own `release` group.** Two quick pushes must not run
  semantic-release side by side. A cancelled pending run loses nothing: the next run
  sees the same commits.

## Risks / Trade-offs

- A scan whose render finished before a release and whose deploy runs after it
  publishes the page with the previous tag until the next scan or release. The
  window is the length of a Pages deploy.
- If the scheduled scan is paused for more than 90 days, every release fails at the
  render step until a scan runs again. The error says so.
