# Design

## Context

`gjed/renovate-config:default` extends `config:recommended` and automerges minor,
patch and pin updates. `config:recommended` includes `:ignoreModulesAndTests`, whose
`ignorePaths` contains `**/vendor/**`. `vendor/leaflet/VERSION` holds the bare
version (`1.9.4`); the vendored `leaflet.js`, `leaflet.css` and images are replaced
by hand following the README "Vendored Leaflet" procedure.

## Goals / Non-Goals

**Goals:**

- Update PRs for the workflow actions, the pre-commit hooks and Leaflet.
- A Leaflet update can never land with `VERSION` and the vendored files out of sync.

**Non-Goals:**

- Updating the vendored Leaflet files automatically.

## Decisions

- **`ignorePaths` is the preset list minus `**/vendor/**`.** `ignorePaths` is not
  mergeable, so the repository value replaces the preset one. Keeping the other
  entries changes nothing else. Rejected: an empty list (scans test fixtures for no
  gain); moving `VERSION` out of `vendor/` (changes the documented layout).
- **Regex manager on the bare `VERSION` content.** `^(?<currentValue>\d+\.\d+\.\d+)\s*$`
  matches the existing file, so its format stays as is. Rejected: a
  `# renovate:` annotation, which would need a comment in a file that holds only the
  version.
- **Leaflet PRs are notifications, never automerged.** Renovate rewrites only
  `VERSION`; the maintainer runs the README procedure on the PR branch. A packageRule
  sets `automerge: false` (overriding the preset's minor/patch automerge) and adds a
  `prBodyNotes` line pointing at the procedure. Rejected: `postUpgradeTasks` to fetch
  the package (the Mend-hosted app allows only an undocumented list of approved
  commands, not `npm pack`/`tar`/`cp`); `dependencyDashboardApproval` (the issue wants
  Leaflet updates to arrive as PRs; not automerging already prevents a bare bump from
  landing); a draft PR (adds a click without protecting more than `automerge: false`).
- **Unstable Leaflet versions are ignored by default.** Leaflet 2.0 is published only
  as alpha/beta prereleases. Renovate's default `ignoreUnstable` skips them while the
  current version is stable, so no extra rule. A future stable 2.0 arrives as a
  separate major PR, which is never automerged either.
- **Enable the `pre-commit` manager.** The issue covers "tooling versions"; the hook
  revisions are this repository's tooling. Minor and patch hook bumps automerge per the
  preset once the PR check passes. Rejected: leaving it off to match `gjed/songbooks`
  exactly.

## Risks / Trade-offs

- A Leaflet PR merged without running the procedure leaves `VERSION` ahead of the
  files. Mitigation: no automerge and the PR note; a CI consistency check is out of
  scope.
