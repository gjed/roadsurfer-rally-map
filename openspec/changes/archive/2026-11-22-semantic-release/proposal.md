# Proposal

## Why

The project has no versions. A code change merged to `main` reaches the published map
only at the next scheduled scan, up to four days later, and nobody can tell which code
built the page they are looking at
([#10](https://github.com/gjed/roadsurfer-rally-map/issues/10)). The page must still
not cost an extra scan: the roadsurfer API is hit only by the twice-weekly scan.

## What Changes

- Add `.releaserc.json` and `.github/workflows/release.yml`, set up like
  `gjed/songbooks`: every push to `main` runs semantic-release, which reads the
  Conventional Commits since the last tag and, for a `feat` or `fix` commit,
  creates the tag `vX.Y.Z` and a GitHub release with generated notes. It pushes no
  commit to `main` (no changelog file, no version bump in a file).
- When a release is published, the workflow rebuilds the page without scanning: it
  downloads the newest unexpired `offers` artifact of a `scan.yml` run on `main`,
  renders it with `--from-json` and the new tag, and deploys it to GitHub Pages.
  Without such an artifact the release job fails with an error and nothing is
  deployed; it never falls back to a scan.
- The scanner gets a `--release TAG` option. `render()` fills a new
  `/*RELEASE*/null` placeholder in the template, escaped like the other embedded
  values, and the page shows the tag in a small footer (`#release`), linked to the
  GitHub release. Without a tag the footer is empty and hidden.
- `scan.yml` scans to `offers.json`, then renders the page from it with the latest
  published release tag, so a scheduled scan keeps the version on the page. With no
  release yet it renders without one.
- The `pages` concurrency group moves from the workflow level of `scan.yml` to the
  two deploy jobs, so a queued scan and a queued release no longer cancel each other
  while two deploys still never overlap. semantic-release runs in its own `release`
  group.
- README "Published map" and AGENTS.md describe how releases are cut.

Out of scope: a changelog file, a `package.json`, release assets, the page restyle
([#27](https://github.com/gjed/roadsurfer-rally-map/issues/27)) and the favicon
([#29](https://github.com/gjed/roadsurfer-rally-map/issues/29)).

## Capabilities

### New Capabilities

- `releases`: semantic versioning of `main` from Conventional Commits.

### Modified Capabilities

- `site-publishing`: a release redeploys the page from the last scan's data, the
  page carries the release tag, and the concurrency group sits on the deploy jobs.
- `rally-scanner`: `--release` embeds a release tag in the map page, shown in a
  footer. These are new requirements next to "Map output", which is unchanged.

## Impact

- New files: `.releaserc.json`, `.github/workflows/release.yml`.
- `scan.yml` reads the latest release tag with `gh release list`, which its
  `contents: read` token allows, and splits the scan and the render into two steps.
- `rally-map.template.html` must keep `/*RELEASE*/null` and the `#release` element.
- The first release from the current history is `v1.0.0`: semantic-release starts at
  1.0.0 and no commit is marked breaking.
