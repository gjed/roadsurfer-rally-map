# Proposal

## Why

Renovate proposes bumping the `executablebooks/mdformat` pre-commit hook from 0.7.22
to 1.0.0. That update cannot work: the hook's `mdformat-tables` 1.0.0 dependency
requires `mdformat<0.8`, which is why the repository pins mdformat 0.7.22. The PR
fails the lint check and has to be closed by hand every time a new mdformat major is
tagged. The maintainer chose to hold mdformat majors
([#21 review](https://github.com/gjed/roadsurfer-rally-map/pull/21#discussion_r4655415921)).

## What Changes

- `.renovaterc.json`: a packageRule disables major updates of the
  `executablebooks/mdformat` pre-commit hook. Its description says to re-enable them
  once `mdformat-tables` supports mdformat 1.x.
- Minor and patch mdformat updates, and all other hook, action and Leaflet updates,
  are unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `dependency-updates`: the pre-commit hook requirement excludes mdformat majors.

## Impact

- One packageRule in `.renovaterc.json`. The open mdformat 1.0.0 Renovate PR closes
  on Renovate's next run after merge, or is closed by hand.
