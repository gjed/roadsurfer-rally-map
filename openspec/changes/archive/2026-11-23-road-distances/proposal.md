# Proposal

## Why

The page estimates every distance as straight line × 1.3
([#7](https://github.com/gjed/roadsurfer-rally-map/issues/7)). That is far off for
mountain routes and for anything that crosses water, such as the UK, Ireland and
Scandinavia, and the distance filter, the `km` sort and the popups all inherit the
error.

## What Changes

- A scan looks up the driving distance of every pick-up and return pair on an OSRM
  server (the public demo server by default) and stores it in each offer record as
  `km`, with `km_estimated` set to `false`.
- Pairs are cached in a git-ignored JSON file (`--road-cache`, default
  `road-distances.json`). Only pairs missing from it are routed, so a second scan
  with no new pair sends no routing request.
- `scan.yml` restores that file from the GitHub Actions cache before the scan and
  saves it after a scan that succeeded. Nothing is committed.
- A pair that cannot be routed gets the straight line × 1.3 value with
  `km_estimated` set to `true`. It is not cached, and it never fails the scan.
- The page uses the record's `km` for the distance filter, the `km` column and sort,
  and the popup and tooltip. A record without `km` keeps the × 1.3 estimate in the
  page. Estimates are labelled with `~` and a note; routed values show as road km.
- The page credits OSRM and OpenStreetMap when it shows routed distances.
- README and AGENTS.md describe the distances, the service and the cache.

Out of scope: route durations, drawing the real road geometry, any change to
`release.yml`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: road distances in the scan data and the page, the cache, the new
  options.
- `site-publishing`: the scheduled scan keeps the routing cache in the Actions cache.

## Impact

- `roadsurfer-rally.py`, `rally-map.template.html`, `scan.yml`, `.gitignore`,
  README.md, AGENTS.md and the tests. No new dependency, Python 3.8 stays the
  minimum.
- `release.yml` is unchanged: it renders from the `offers` artifact, which now holds
  the routed distances, and sends no routing request.
