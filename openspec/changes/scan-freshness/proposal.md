# Proposal

## Why

The map is refreshed only twice a week, so the age of its data matters, but the page
does not say when it was scanned
([#4](https://github.com/gjed/roadsurfer-rally-map/issues/4)). The scan metadata must
also travel in the scan data file, so that a later re-render from the `offers`
artifact ([#10](https://github.com/gjed/roadsurfer-rally-map/issues/10)) shows the
time of the scan, not the time of the render.

The other half of #4, keeping the last good map when a scan fails, already holds:
a scan with more than 10% failed requests exits non-zero and writes no file, and the
deploy job of `scan.yml` runs only after a successful build job.

## What Changes

- `--json-out` writes a top-level `scan` object next to `offers`: finish time (UTC,
  ISO 8601), offers found, requests, failed requests, HTTP 429 answers, the
  `--start`/`--end` window and the `--from`/`--to` terms.
- The map template gets a second placeholder, `/*SCAN*/null`, which `render()`
  replaces with the scan object, or `null` when there is none, with the same `</`
  escaping as the offers.
- `--from-json` embeds the file's `scan` object as is and keeps accepting files
  without one.
- The toolbar shows `updated YYYY-MM-DD HH:MM UTC` before the route and trip counts,
  with the request counts in its tooltip, and nothing when the page has no metadata.
- README documents the metadata keys and the toolbar timestamp.

Out of scope: a release tag or footer
([#10](https://github.com/gjed/roadsurfer-rally-map/issues/10)), workflow changes,
a relative age ("3 days ago") in the toolbar.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the scan data file carries scan metadata and the map shows the
  scan time.

## Impact

- `offers.json` gains a `scan` key; readers that only use `offers` are unaffected.
- `rally-map.template.html` must keep both `/*DATA*/[]` and `/*SCAN*/null`.
