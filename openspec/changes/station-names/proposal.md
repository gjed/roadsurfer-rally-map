# Proposal

## Why

Since the interface comes in seven languages (issue #56), station names are the one thing
left in English: an Italian page says `Munich`, not `Monaco di Baviera`. The scanner reads
only `/api/en`, which is why PR #63 left the names out. Probing
`/api/{de,fr,es,it,nl,pt}/rally/stations` with the same alias shows that roadsurfer
localises `name` (not `city.name`) and keeps the same station ids. Issue #67.

## What Changes

- The scanner fetches `/rally/stations` once per page language besides English, six
  more sequential requests, and records `names` on each record's `from` and `to`.
- The page shows the name of the language it is in wherever it displays a station.
- Keys stay English: route and chain keys, the favourites storage, the URL hash, feed
  file names, feed entry ids and feed text.
- A data file without `names` renders English names as before.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: adds "Station names per language" and "Station names in the page";
  changes "Polite API access", "Scan data file" and, by renaming it, "Texts that stay as
  they are".

## Impact

`roadsurfer-rally.py` (language-aware `get()`, a language pass after the station list,
`names` on the records), `rally-map.template.html` (a label helper at every display
site), `tests/` and the README "API notes". A scan makes six more requests.
