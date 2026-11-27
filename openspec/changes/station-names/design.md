# Design

## Names per language

The probe settled the first step of the issue: every page language answers
`/api/{lang}/rally/stations` with the same station ids as `en` and localised `name`
values (different from English for 26 to 57 of 112 stations, depending on the language).
`city.name` is not localised and is not used for display. A station is joined across
languages by its `id`, never by its name.

## What a record stores

`names` is `{lang: name}` and holds only the languages whose name differs from the
English one. A record from the scanner is embedded in the page once per offer, so
repeating an unchanged name six times per station per offer would grow the page for no
gain, and the page falls back to `name` for a missing language anyway. A station whose
names are all English has no `names` key at all, the same as a record from an older scan.
`name` is the English name and stays the key.

## Scanner

`get()` takes a `lang` (default `en`) and builds the URL from the API root, so the
language pass goes through the same delay, jitter, retry and failure counting as every
other request. `BASE` becomes the API root; `https://booking.roadsurfer.com/api/en` is
still what every other request uses.

The pass runs right after the English station list and before routes are looked up: it
is part of the scan, so its requests are in the `requests` and `failed` counts that
decide a blocked scan. `--list` only prints stations and returns before it, so it still
makes one request. A language whose request fails (or answers something that is not a
list) is skipped: its names fall back to English, the failure counts toward `MAX_FAILED`,
and the scan goes on. A station id missing from a language's answer falls back to English
for that station.

The scanner's own `--from` and `--to` matching, the feed slugs, ids and text, and
`scan.stations` stay English.

## Page

- One helper, `sname(s)`, is the label: `s.names[lang]` when set, else `s.name`.
  `place(s)` becomes the label (`sname(s), cc`), and a new `placeKey(s)` is the old
  English `name, cc` for the favourite station key and the feed table lookup.
- Every display site uses `sname`/`place`; every key site keeps `.name`/`placeKey`:
  `routeKey`, `legKey`, `hopKey`, `ENDS`, `FILTERS`, the `STATIONS` map, favourites, the
  hash (`from`, `to`, `route`, `leg`, `chain`) and `data-*` attributes.
- A string that holds a key and is shown (the leg filter's title, `eff.fst` in a back
  button) is mapped through `STATIONS` to a label.
- Station selects keep the English name as the option value and show the localised one,
  sorted with `F.coll` on the shown label. The page has no free-text station search, so
  nothing else needs to match both names; had there been one, it would match the key and
  the shown name.
- A language change already runs `render()`, which rebuilds every list and select from
  the state; selections, favourites and the hash hold keys, so they survive it.

## Old data

`names` is optional everywhere. `sname` falls back on `name`, so a file from before this
change (the test fixture, or the artifact the release workflow renders) shows the English
names it always did. Nothing reads `names` in the feeds.
