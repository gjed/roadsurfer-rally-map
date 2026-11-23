# Proposal

## Why

The designer review of [#38](https://github.com/gjed/roadsurfer-rally-map/issues/38)
removes the page footer: a full-width strip for one link wastes the room of the map and
the list. The road distance footer added by
[#7](https://github.com/gjed/roadsurfer-rally-map/issues/7) is the same kind of strip,
so the page would keep a footer for one credit line and one explanation.

## What Changes

- The credit for OSRM and OpenStreetMap contributors moves into the map's attribution
  control, next to the tile credit and the release tag.
- The explanation of `~` moves into the map legend, as an entry shown only when the
  page has an estimated distance. The list cells already carry it as a title.
- The page has no footer.

Out of scope: the distances themselves, the routing service and the cache.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: where the road distance credit and the `~` explanation are shown.

## Impact

- `rally-map.template.html`, the README. No scanner change, no new dependency.
