# Design

## Decisions

- **Granularity.** One feed for everything and one per pick-up station (about 60 files).
  Per-route feeds would be hundreds of files for little gain.
- **Station identity.** A station is a name plus a country code: the offer records carry
  no station id. The same pair identifies the route in an entry id.
- **Slug rule.** NFKD-decompose the name, drop the combining marks, map the few letters
  that do not decompose (`ß`→`ss`, `æ`→`ae`, `œ`→`oe`, `ø`→`o`, `ł`→`l`, `đ`→`d`),
  lowercase, replace every run of characters outside `a-z0-9` with one hyphen and trim
  hyphens; an empty result is `station`. Stations whose base slugs are equal all get
  `-<cc>` (lowercase country code) appended. If a slug is still taken, it takes `-2`,
  `-3`, … in the order of the sorted `(name, country code)` pairs. The result depends
  only on the set of pick-up stations in the offers, so the map (which embeds all
  offers) computes the same file names.
- **Entry id.** `tag:gjed.github.io,2026-11-26:rally:<from>:<to>:<start>:<end>`, where
  `<from>` and `<to>` are `name,CC` percent-encoded. It does not depend on the slug
  rule, so a new duplicate station never changes the id of an old entry. A renamed
  station gives new ids once; that is acceptable.
- **Feed id.** The feed's own URL under the Pages site: absolute, stable, and the same
  as its `self` link.
- **`<updated>`.** The scan's `finished_at`, for the feed and every entry. A data file
  without scan metadata (the fixture) uses the render time: the file carries no
  better answer, and readers go by the entry ids.
- **Summary.** Plain text: window, distance with `~` when `km_estimated`, price when the
  record has one (`""` and `n/a` count as none). A record without `km` gets the same
  straight-line × 1.3 estimate as the page, with `~`.
- **Text language.** English, with dates formatted by a fixed table (`Tue 24 Nov`),
  not by the locale, so the output is the same on every machine.
- **Site URL.** A constant in the script. A fork publishes feeds that name this
  project's Pages URL; making it an option is not worth a flag until someone needs it.
- **Stations without offers.** They have no file; the scanner does not remove files of
  earlier runs from `DIR`. CI starts from an empty directory.
- **Order of writes.** Feeds are written after the page and the data file, after the
  blocked-scan check and the road distance step, like the other outputs.
- **`--from-json` without `--map`.** Allowed when `--feeds` is given, so the feeds can
  be rendered alone. `--release` still needs `--map`.
