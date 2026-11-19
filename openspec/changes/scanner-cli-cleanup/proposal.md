# Proposal

## Why

The imported prototype still carries features that only made sense on one laptop: a
seen-offers state file with a `NEW` flag, desktop notifications, a Brussels detour
filter and a polling loop
([#5](https://github.com/gjed/roadsurfer-rally-map/issues/5)). Later work needs the
opposite: the Pages workflow
([#2](https://github.com/gjed/roadsurfer-rally-map/issues/2)), the PR check
([#9](https://github.com/gjed/roadsurfer-rally-map/issues/9)) and the release
([#10](https://github.com/gjed/roadsurfer-rally-map/issues/10)) must build the page
from scan data without calling the API.

## What Changes

- **BREAKING** Remove the `.roadsurfer-rally-seen.json` state file, the `NEW` flag
  and `--notify` (`notify-send`). Drop the file from `.gitignore`.
- **BREAKING** Remove `--watch`. It is a local polling loop; a scheduler or a CI cron
  replaces it. This also settles two deferred review comments on
  [PR 14](https://github.com/gjed/roadsurfer-rally-map/pull/14): `--notify` without
  `notify-send` and the `--start` default staying fixed during `--watch`.
- **BREAKING** Remove `--via`, `--detour`, the `detour()` helper, its route filter and
  the `+Nkm` column.
- Split scanning from rendering. `--json-out FILE` writes the scanned offers as
  `{"offers": [...]}`. `--from-json FILE --map OUT` builds the map from that file
  without any network request. `--map` alone still scans and renders in one run.
- Keep `--delay`, `--from`, `--to`, `--start`, `--end`, `--prices`, `--list` and
  `--map` with unchanged semantics, the request retry behaviour, the `/*DATA*/[]`
  template contract and the `</` escaping in the data block.
- Update the README: drop the seen-file paragraph, show `--help` verbatim and
  document the scan/render split.

Out of scope: scan metadata in the data file
([#4](https://github.com/gjed/roadsurfer-rally-map/issues/4)), vendoring Leaflet
([#6](https://github.com/gjed/roadsurfer-rally-map/issues/6)), workflows and tests
([#9](https://github.com/gjed/roadsurfer-rally-map/issues/9)).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: offer listing keeps no state between runs, the map can be rendered
  from a data file, and the CLI exposes only the supported options.

## Impact

- `roadsurfer-rally.py`, `.gitignore`, `README.md`.
- Anyone using `--notify`, `--watch`, `--via` or `--detour` gets an argparse error.
  Existing `.roadsurfer-rally-seen.json` files are no longer read or written.
