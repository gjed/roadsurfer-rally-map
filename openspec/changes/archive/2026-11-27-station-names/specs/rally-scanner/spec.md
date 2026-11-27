# Delta for rally-scanner

## ADDED Requirements

### Requirement: Station names per language

After the English station list, the scanner SHALL request `/rally/stations` once for
each of `de`, `fr`, `es`, `it`, `nl` and `pt`, through the same pacing and retries as every
other request, and SHALL join the answers to the English list by station `id`. Each
record's `from` and `to` SHALL get `names`, an object of language code to name holding
only the languages whose name differs from the English `name`; `name` stays English.

#### Scenario: Six more requests

- **WHEN** a scan runs with `--json-out`, `--map` or `--feeds`
- **THEN** it sends six more requests than before, one `/api/{lang}/rally/stations`
  request per language other than English

#### Scenario: Console-only scan

- **WHEN** a scan runs without `--json-out`, `--map` and `--feeds`
- **THEN** it sends no station list request for a language other than English

#### Scenario: Name that differs

- **WHEN** the English name of a station is `Munich` and the Italian one is
  `Monaco di Baviera`
- **THEN** a record from that station has `name` `Munich` and `names` holding
  `it` `Monaco di Baviera`

#### Scenario: Name that does not differ

- **WHEN** a station has the same name in every language
- **THEN** its record has no `names`

### Requirement: Failed language requests

A failed station list request of a language SHALL NOT stop the scan: that language SHALL
fall back to the English names, and the request SHALL count as failed toward the share
that blocks a scan, like any other.

#### Scenario: A language fails

- **WHEN** the request for one language fails
- **THEN** the scan goes on, the names of that language fall back to English, and the
  failed request is in the `failed` count, which can block the scan like any other

### Requirement: Station names in the page

The page SHALL show each station by `names[lang]` of its record when it has one for the
page language, else by `name`, wherever it displays one: cards, the route and chain
details, tooltips, popups, chips, the station selects, the Trips view, chains and
accessible names. Lists SHALL be sorted on the name shown. Changing the language SHALL
re-label the page without changing the selections or the favourites.

#### Scenario: Station in Italian

- **WHEN** a record has `name` `Munich` and `names` with `it` `Monaco di Baviera` and the
  page is in Italian
- **THEN** its cards, tooltips and select options read `Monaco di Baviera`, and the
  route key and the hash use `Munich`

#### Scenario: Language without a name

- **WHEN** the page is in German and the record has no `de` in `names`
- **THEN** the page shows `name`

#### Scenario: Data file without names

- **WHEN** a page is rendered from a data file whose records have no `names`
- **THEN** every station is shown by its English name, in every language

#### Scenario: Language change keeps the selection

- **WHEN** a station is chosen in the pick-up select and the user changes the language
- **THEN** the station stays chosen, shown by its name in the new language, and the hash
  still holds the English name

### Requirement: Station keys stay English

Route, leg, connection and chain keys, favourites in storage, the URL hash, the values of
the station selects, the station feed table, and the scanner's `--list`, `--from` and
`--to` and `scan.stations` SHALL use the English `name`, whatever the page language and
whether or not a record has `names`.

#### Scenario: Key in Italian

- **WHEN** the page is in Italian and the user stars a route from `Munich`
- **THEN** the favourite and the hash hold `Munich`, not `Monaco di Baviera`

### Requirement: Texts that are never translated

The attribution credits, the release tag, booking links, the price text and the name
`Rally map` with the page title `roadsurfer Rally map` SHALL NOT be translated, in any
language. The feeds SHALL keep the English station names.

#### Scenario: Release tag in German

- **WHEN** the page is shown in German
- **THEN** the release tag and the attribution credits are unchanged

#### Scenario: Feed from records with names

- **WHEN** the feeds are written from records that have `names`
- **THEN** they use the English names, as they do without `names`

## MODIFIED Requirements

### Requirement: Polite API access

The scanner SHALL send every request to `https://booking.roadsurfer.com/api/en`, except
the station list requests of the other page languages, which go to
`https://booking.roadsurfer.com/api/{lang}`, each with
an `X-Requested-Alias` header that matches the route. It SHALL send requests one at a
time, each after a configurable delay (0.5 s by default) plus a random jitter of up to
20% of it. After HTTP 429 it SHALL retry after a jittered wait of at least one minute
that grows with each attempt.

#### Scenario: Default scan pacing

- **WHEN** the scanner runs without `--delay`
- **THEN** requests are sent sequentially, at least 0.5 s apart

#### Scenario: Rate limited

- **WHEN** a request fails with HTTP 429
- **THEN** the scanner waits at least one minute, longer before each later retry,
  and gives up after five attempts

#### Scenario: Wrong route alias

- **WHEN** a request fails with HTTP 404
- **THEN** the scanner gives up on that request without retrying

## REMOVED Requirements

### Requirement: Texts that stay as they are

**Reason**: Its list began with station names, which the page now translates. The
remaining list and the station names move to "Texts that are never translated" and
"Station names in the page".

**Migration**: Read "Texts that are never translated".
