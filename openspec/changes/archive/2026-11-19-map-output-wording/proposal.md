# Proposal

## Why

Since Leaflet is vendored ([#6](https://github.com/gjed/roadsurfer-rally-map/issues/6)),
the generated page works only with `vendor/` next to it. The `rally-scanner` spec still
calls the map "self-contained" in its Purpose and in the requirement title, which is no
longer true
([review comment](https://github.com/gjed/roadsurfer-rally-map/pull/16#discussion_r4630483487)).

## What Changes

- Rename the requirement "Self-contained map output" to "Map output" and state that the
  page loads Leaflet from `vendor/leaflet/` next to it.
- Reword the spec Purpose from "a self-contained HTML map" to "an HTML map".

No code changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: wording only; the map output requirement no longer claims the page
  is self-contained.

## Impact

Spec text only.
