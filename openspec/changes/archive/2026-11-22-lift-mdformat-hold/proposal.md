# Proposal

## Why

The hold on mdformat majors existed only because `mdformat-tables` 1.0.0 requires
`mdformat<0.8`. `mdformat-gfm` 1.0.0 now registers the table extension itself, so the
mdformat hook no longer needs `mdformat-tables` and runs on mdformat 1.0.0
([#23](https://github.com/gjed/roadsurfer-rally-map/pull/23)). With mdformat on 1.x,
the hold would only block a future 2.x update for a reason that no longer applies.

## What Changes

- `.renovaterc.json`: remove the packageRule that disables major updates of the
  `executablebooks/mdformat` pre-commit hook.
- Renovate again proposes every hook update, mdformat majors included.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `dependency-updates`: the pre-commit hook requirement covers every hook again,
  without the mdformat exception. OpenSpec does not let a MODIFIED delta drop a
  scenario, so "Pre-commit hook updates" is removed and replaced by "Pre-commit hook
  revision updates", which has the wording it had before the hold.

## Impact

- One packageRule removed from `.renovaterc.json`. No code or workflow changes.
