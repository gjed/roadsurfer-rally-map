# Delta for rally-scanner

## ADDED Requirements

### Requirement: Atom feeds

With `--feeds DIR`, the scanner SHALL create `DIR` if needed and write UTF-8 Atom
(RFC 4287) files with the standard library only: `all.xml` with one entry per offer
record, and `from-<slug>.xml` with the entries of one pick-up station's offers, in the
order of the records. It SHALL print the number of files and offers and leave other
files in `DIR` alone.

#### Scenario: Feeds from a data file

- **WHEN** the user runs `python3 roadsurfer-rally.py --from-json tests/fixtures/offers.json --feeds feeds`
  with networking disabled
- **THEN** `feeds/all.xml` and `feeds/from-munich.xml` parse as XML, each has one entry
  per offer, and the scanner exits with status 0

#### Scenario: Name with markup

- **WHEN** a station is named `Ben & Jerry's "Hub" <North>`
- **THEN** the feeds parse and the entry title holds the name unchanged

### Requirement: Feeds of stations without offers

The stations with a feed SHALL be those in the scan's `stations` list and those of the
records, each a name plus a country code. A station without offers SHALL get a feed
with no entries.

#### Scenario: Station without offers

- **WHEN** the scan's `stations` list has Nice, FR and no record starts there
- **THEN** `from-nice.xml` is written with no entries

#### Scenario: Data file without a station list

- **WHEN** the data file has no `scan.stations`
- **THEN** the stations are those of the records

### Requirement: Feed metadata

Each feed SHALL have an `id` that is its own URL, a `title`, a `link` with `rel="self"`
to that URL, a `link` with `rel="alternate"` to
`https://gjed.github.io/roadsurfer-rally-map/`, an `author` and `updated`. The URL of a
feed is `https://gjed.github.io/roadsurfer-rally-map/feeds/` followed by its file name.
The title SHALL be `roadsurfer Rally offers` for `all.xml` and
`roadsurfer Rally offers from <name>, <CC>` for a station feed.

#### Scenario: Station feed

- **WHEN** `from-munich.xml` is written
- **THEN** its id and self link are
  `https://gjed.github.io/roadsurfer-rally-map/feeds/from-munich.xml` and its title is
  `roadsurfer Rally offers from Munich, DE`

### Requirement: Feed update time

`updated` of a feed and of each of its entries SHALL be the scan's `finished_at`, or the
time of the rendering when the scan metadata is absent or has none.

#### Scenario: Scan time

- **WHEN** the data file's `scan.finished_at` is `2026-11-18T03:12:05Z`
- **THEN** every feed and every entry has `updated` `2026-11-18T03:12:05Z`

#### Scenario: No scan metadata

- **WHEN** the data file has no `scan` object
- **THEN** the feeds are written with the time of the rendering as `updated`

### Requirement: Feed entries

Each entry is one offer window and SHALL have a `title`
`<from name>, <CC> → <to name>, <CC> · <start> – <end>` in English, the dates as
weekday, day and month such as `Tue 24 Nov`, independent of the locale, a `link` with
`rel="alternate"` whose `href` is the record's booking link, a plain-text `summary`
and `updated`.

#### Scenario: Entry for an offer

- **WHEN** a record goes from Munich, DE to Bordeaux, FR for 2026-11-24 to 2026-12-01
- **THEN** its entry title is `Munich, DE → Bordeaux, FR · Tue 24 Nov – Tue 1 Dec` and
  its link is the record's booking link

### Requirement: Feed entry summary

The summary of an entry SHALL give the window, the distance in km and the price when the
record has one other than the empty string or `n/a`. The distance SHALL have a leading
`~` when `km_estimated` is true, or when the record has no `km` and the straight-line
× 1.3 estimate of the page is used.

#### Scenario: Estimated distance

- **WHEN** a record has `km` 1230 and `km_estimated` true
- **THEN** its summary shows `~1,230 km`

#### Scenario: Price

- **WHEN** a record has the price `Camper €129.01`
- **THEN** its summary shows it, and a record with price \`\` or `n/a` shows none

### Requirement: Stable entry ids

An entry's `id` SHALL be
`tag:gjed.github.io,2026-11-26:rally:<from>:<to>:<start>:<end>`, where `<from>` and
`<to>` are the station name and country code joined by a comma and percent-encoded,
and `<start>` and `<end>` the window as `YYYY-MM-DD`. It SHALL be the same for the same
route and window in every scan and render, and unique within a feed, so that a feed
reader shows only windows it has not seen.

#### Scenario: Rendered twice

- **WHEN** the same data file is rendered twice
- **THEN** every entry has the same id in both renders

#### Scenario: New window

- **WHEN** a later scan has a window that the earlier scan did not
- **THEN** only that entry has an id that was not in the earlier feed

### Requirement: Feed file names

The file of a pick-up station SHALL be `from-<slug>.xml`. The base slug of a station name
is its NFKD decomposition without combining marks, with `ß`, `æ`, `œ`, `ø`, `ł` and `đ`
written as `ss`, `ae`, `oe`, `o`, `l` and `d`, lowercased, with every run of characters
outside `a-z0-9` replaced by one hyphen and the hyphens at both ends removed; an empty
result is `station`.

#### Scenario: Accented name

- **WHEN** the pick-up station is `Zürich Flughafen`
- **THEN** its feed is `from-zurich-flughafen.xml`

### Requirement: Feed file name collisions

When several pick-up stations have the same base slug, the slug of each
SHALL be the base slug, a hyphen and its lowercase country code. A slug that is still
taken SHALL get `-2`, `-3`, and so on, assigned in the order of the stations sorted by
name and country code. The slugs SHALL depend only on the set of pick-up stations the
scan knows, not on which of them have offers, so that a feed's URL does not change when
another station gets an offer.

#### Scenario: Same name in two countries

- **WHEN** two pick-up stations are both named `Neustadt`, in DE and in AT
- **THEN** their feeds are `from-neustadt-de.xml` and `from-neustadt-at.xml`

#### Scenario: Same slug in one country

- **WHEN** pick-up stations named `Foo` and `Foo!`, both in DE, are known
- **THEN** the feeds are `from-foo-de.xml`, for `Foo`, and `from-foo-de-2.xml`

## MODIFIED Requirements

### Requirement: Scan data file

With `--json-out FILE`, the scanner SHALL write a UTF-8 JSON object whose `offers` key
holds the offer records that `--map` embeds, each with `km` and `km_estimated`, and
whose `scan` key holds the scan metadata: `finished_at` (UTC, ISO 8601), `offers`,
`requests`, `failed`, `rate_limited`, `start`, `end`, `from`, `to` and `stations` (the
pick-up stations asked about, as `{"name", "cc"}`). Readers SHALL tolerate other
top-level keys, records without `km` and a `scan` without `stations`.

#### Scenario: Scan to a data file

- **WHEN** the user runs `python3 roadsurfer-rally.py --from 1 --json-out offers.json`
- **THEN** `offers.json` holds an object whose `offers` list has one record per listed
  offer, each with `km` and `km_estimated`, and whose `scan` object has the finish time
  such as `2026-11-18T03:12:05Z`, the number of offers, the request, failed and HTTP
  429 counts the summary prints, the `--start` and `--end` window, `from` set to
  `["1"]`, `to` set to `null` and `stations` listing station 1

### Requirement: Offline rendering

With `--from-json FILE`, the scanner SHALL render the map and the feeds from the data
file without sending any request, to roadsurfer or to a routing server. `--from-json`
SHALL require `--map` or `--feeds` and SHALL be rejected together with `--list`,
`--json-out`, `--from`, `--to` or `--prices`.

#### Scenario: Render without network

- **WHEN** the user runs `python3 roadsurfer-rally.py --from-json offers.json --map index.html`
  with networking disabled
- **THEN** `index.html` is written and the scanner exits with status 0

#### Scenario: Data file without map

- **WHEN** the user runs `python3 roadsurfer-rally.py --from-json offers.json`
- **THEN** the scanner exits with a usage error and writes nothing

#### Scenario: Feeds without map

- **WHEN** the user runs `python3 roadsurfer-rally.py --from-json offers.json --feeds feeds`
- **THEN** the feeds are written, no page is written and no request is sent

#### Scenario: Data file without road distances

- **WHEN** the user renders a data file whose records have no `km`
- **THEN** `index.html` is written, no request is sent, and the page shows the
  estimated distances labelled as estimates

### Requirement: Supported options

The scanner SHALL accept only `--to`, `--from`, `--start`, `--end`, `--prices`,
`--map`, `--json-out`, `--feeds`, `--from-json`, `--delay`, `--release`, `--road-cache`,
`--routing-url`, `--list` and `--help`.

#### Scenario: Removed local-only option

- **WHEN** the user passes `--notify`, `--watch`, `--via` or `--detour`
- **THEN** the scanner exits with an unrecognized-argument error

### Requirement: Blocked scan detection

After a scan, the scanner SHALL print the number of requests, failed requests and
HTTP 429 responses, and the scan duration. A request counts as failed when the
scanner gives up on it. When more than 10% of the requests failed, the scanner SHALL
exit with a non-zero status and SHALL NOT write the `--json-out` or `--map` file or
the `--feeds` files.

#### Scenario: Healthy scan

- **WHEN** a scan with `--json-out offers.json --map index.html` finishes with at most
  10% failed requests
- **THEN** the scanner prints the request count, the failed count and the duration,
  writes both files and exits with status 0

#### Scenario: Blocked scan

- **WHEN** more than 10% of the requests of a scan fail
- **THEN** the scanner prints the request count, the failed count and the duration,
  exits with a non-zero status and writes neither the `--json-out` nor the `--map`
  file, and no feed

### Requirement: Road distances

When a scan writes `--json-out`, `--map` or `--feeds`, after the blocked-scan check,
the scanner
SHALL give every offer record `km`, the driving distance of its pick-up and return
pair in whole kilometres from an OSRM server (`--routing-url`, the public demo server
by default), and `km_estimated` `false`. A pair it cannot route SHALL get the
great-circle distance × 1.3 rounded to 10 km and `km_estimated` `true`.

#### Scenario: Routed pair

- **WHEN** a scan writes `offers.json` and the router answers for a pair
- **THEN** every record of that pair has the routed `km` and `km_estimated` `false`

#### Scenario: Routing fails

- **WHEN** the routing server is unreachable during a scan that writes `offers.json`
- **THEN** the scan finishes with status 0, `offers.json` is written, and every
  affected record has the estimate as `km` and `km_estimated` `true`

#### Scenario: Scan without a file

- **WHEN** a scan writes neither `--json-out`, `--map` nor `--feeds`
- **THEN** no routing request is sent

#### Scenario: Blocked scan routes nothing

- **WHEN** more than 10% of the roadsurfer requests of a scan fail
- **THEN** no routing request is sent and the road distance cache is not written
