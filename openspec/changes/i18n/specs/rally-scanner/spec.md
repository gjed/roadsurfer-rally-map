# Delta for rally-scanner

## MODIFIED Requirements

### Requirement: Last-updated timestamp

When the map page has scan metadata, its app bar SHALL show the time the scan
finished, in UTC to the minute, with the date formatted for the page's language (in
English `Updated 18 Nov, 03:12 UTC`), and the offer, request and failed-request counts in
its tooltip. Below 700 px the time SHALL be at the bottom of the filter sheet instead
(in English `Offers as of the scan of 18 Nov, 03:12 UTC`). Without scan metadata it SHALL
show no time.

#### Scenario: Page with scan metadata

- **WHEN** a page whose scan finished at `2026-11-18T03:12:05Z` is opened in English
- **THEN** its app bar shows `Updated 18 Nov, 03:12 UTC`

#### Scenario: Page without scan metadata

- **WHEN** a page rendered from a data file without a `scan` object is opened
- **THEN** its filter bar shows the trip and route counts and the page shows no time

#### Scenario: Scan time on a phone

- **WHEN** the user opens the filter sheet at 390 px on that page
- **THEN** the sheet ends with `Offers as of the scan of 18 Nov, 03:12 UTC`

#### Scenario: Scan time in German

- **WHEN** the same page is shown in German
- **THEN** the app bar shows the German wording with the date as `18. Nov.` and the
  time `03:12 UTC`

### Requirement: Trip list columns

Each Trips row SHALL show the start date, end date, nights, pick-up and return station
as `Name, CC`, road distance (with `~` when estimated), the price when the page has
prices, a `Map` button and a `Book` link that opens in a new tab. Dates SHALL show with the
weekday, day and month formatted for the page's language (in English `Thu 19 Nov`), with
the ISO date in the cell's `title`. Every value from the API SHALL be escaped before it
is inserted as HTML.

#### Scenario: Booking from the list

- **WHEN** the user clicks the booking link of a row
- **THEN** the trip's booking URL opens in a new tab and the view does not change

#### Scenario: Dates on a phone

- **WHEN** the Trips view is shown 375 px wide in English
- **THEN** dates read `Thu 19 Nov`, and the cell's title is `2026-11-19`

## ADDED Requirements

### Requirement: Interface languages

The map page SHALL be available in English (the source and the fallback), German, French,
Spanish, Italian, Dutch and Portuguese. Every text it shows SHALL come from one catalog,
including text built by the script and accessible names that are not visible. Where this
specification quotes a text of the page it is the English one.

#### Scenario: Page in Italian

- **WHEN** the page is opened in Italian
- **THEN** no English text is left in its views, panels and accessible names other than
  the texts listed under "Texts that stay as they are"

### Requirement: Texts that stay as they are

Station names as scanned, the attribution credits, the release tag, booking links, the
price text and the name `Rally map` with the page title `roadsurfer Rally map` SHALL NOT be
translated, in any language.

#### Scenario: Station name in German

- **WHEN** a route from `Munich` is shown in German
- **THEN** the station is still named `Munich`

### Requirement: Message catalog

The catalog SHALL be one JSON object, `STRINGS`, in a block of the template between
`/*STRINGS*/` and `/*END STRINGS*/`, with one object of flat semantic keys, such as
`filters.pickup` or `count.trips`, per language.

#### Scenario: Catalog in the rendered page

- **WHEN** the page is rendered
- **THEN** the text between the two markers is a JSON object that parses and holds an
  object for each of the seven languages

### Requirement: Message lookup

A message SHALL be looked up by key, with `{name}` placeholders. A count SHALL choose its
form with `Intl.PluralRules` from `key.one`, `key.other` and the other categories where a
language needs them. A key that a language lacks SHALL be shown in English, never blank
and never as the key. A sentence SHALL be one message, not fragments put together in code.

#### Scenario: Missing translation

- **WHEN** a language lacks a key
- **THEN** the page shows the English text for that key

#### Scenario: Plural

- **WHEN** one trip and two trips are counted in German
- **THEN** the page reads `1 Fahrt` and `2 Fahrten`

### Requirement: Language choice

The page SHALL pick its language from, in order, `lang` in the URL hash, then
`localStorage['rally-map:lang']`, then the first of `navigator.languages` whose primary
subtag is one of the seven languages, then English. A value that is not one of the seven
SHALL be ignored, and storage that is unavailable SHALL NOT stop the page.

#### Scenario: Hash before storage

- **WHEN** storage holds `de` and the page is opened at `#map?lang=it`
- **THEN** the page is in Italian

#### Scenario: Browser language

- **WHEN** nothing is stored, the hash has no `lang` and the browser's languages are
  `pt-BR, en`
- **THEN** the page is in Portuguese

#### Scenario: No match

- **WHEN** the browser's languages are `ja, ko`
- **THEN** the page is in English

### Requirement: Language written down

`<html lang>` SHALL be the language shown on every change, and `dir` SHALL stay `ltr`. A
language chosen in the Display menu SHALL be written to the hash with
`history.replaceState` and to `localStorage`. A language that was not chosen SHALL NOT be
written to the hash.

#### Scenario: Chosen language

- **WHEN** the user picks German in the Display menu
- **THEN** `<html lang>` is `de`, the hash has `lang=de` and storage holds `de`

#### Scenario: Language from the browser

- **WHEN** the page opens in Spanish because of the browser's languages
- **THEN** `<html lang>` is `es` and the hash has no `lang`

### Requirement: Language kept on Back

The `lang` of the URL hash SHALL be read once, when the page loads. Back, Forward and a
hash typed in the address bar SHALL keep the language shown, and the page SHALL write that
language into the entry, so the address shows it.

#### Scenario: Back after a language change

- **WHEN** the user picks English, opens a route, picks German and presses Back
- **THEN** the page is still in German, `localStorage['rally-map:lang']` holds `de` and
  the address has `lang=de`

### Requirement: Display button language

The Display button SHALL show a globe and the code of the current language beside the
theme icon, and its accessible name, which is also its `title`, SHALL be `Display settings: language <Language>, theme <Choice>` in the page's language, the language in its own name
and the choice as the Theme control labels it.

#### Scenario: Button in English

- **WHEN** the page is in English with the system theme
- **THEN** the button shows `EN` and is named `Display settings: language English, theme System`

### Requirement: Language section

The Display panel SHALL have a `Language` section above `Theme`: a labelled group with one
button per language, written in its own language with its code (`Deutsch DE`) and a
`lang` attribute, with `aria-pressed` and a check mark on the current one. Below 700 px
the same section SHALL be in the Display sheet with targets of at least 44 px.

#### Scenario: Choosing a language

- **WHEN** the user opens Display and picks `Deutsch`
- **THEN** the page is in German, the button shows `DE` and `Deutsch` is marked as pressed

### Requirement: Language change keeps state

Changing the language SHALL re-render the text in place. The filters, the open route or
chain, the selected leg, the sort and grouping, the theme, the view, the scroll positions
and the map's centre and zoom SHALL stay, and an open Display panel SHALL stay open.

#### Scenario: Chain open

- **WHEN** a chain is open, the Display panel is open and the user picks French
- **THEN** the same chain is open in French, with the same filters, the same sort and the
  same map view

#### Scenario: Trips view on a phone

- **WHEN** the user switches language in the Display sheet of the Trips view on a phone
- **THEN** the same trips are listed in the new language, in the same order and at the
  same scroll position

### Requirement: Formatting for the language

Dates SHALL be formatted with `Intl.DateTimeFormat` for the page's language, in UTC, and a
date range SHALL be one message with each end formatted on its own. Numbers and distances
SHALL be formatted with `Intl.NumberFormat`, distances as a kilometre unit (`1,240 km` in
English, `1.240 km` in German), and the `~` of an estimate SHALL stay in front of the
number. Each language SHALL format as one regional locale: `en-GB`, `de-DE`, `fr-FR`,
`es-ES`, `it-IT`, `nl-NL` and `pt-PT`.

#### Scenario: Distance in German

- **WHEN** a route of 1240 km is shown in German
- **THEN** its card reads `1.240 km`

### Requirement: Country names and sorting

Country names in the pick-up and return menus SHALL come from `Intl.DisplayNames` and
names SHALL sort with `Intl.Collator` for the page's language, while rows and cards keep
`Name, CC`.

#### Scenario: Country menu

- **WHEN** the pick-up menu is shown in Italian
- **THEN** the countries are named `Germania`, `Francia` and so on, in alphabetical order

### Requirement: Layout in longer languages

German and French run about 30% longer than English. Chips, segmented controls, buttons
and the app bar SHALL wrap or grow, and SHALL NOT cut a label, at 1440 px and at 390 and
360 px wide.

#### Scenario: German phone

- **WHEN** the page is shown in German at 360 px wide
- **THEN** no label, chip, segmented control or button is cut or overflows the screen

### Requirement: Catalog test

A unit test SHALL cut the catalog out of the rendered page and check that every key of
every language is a key of English, that every `{placeholder}` of an English message is in
each translation of it, that every plural message has `one` and `other`, and that English
has no missing or malformed message. A key that a language lacks SHALL be a warning, not a
failure.

#### Scenario: Translation without a placeholder

- **WHEN** a translation drops a placeholder that the English message has
- **THEN** the test fails and names the language and the key

#### Scenario: Missing translation in the test

- **WHEN** a language lacks an English key
- **THEN** the test passes and prints a warning that names the language and the key
