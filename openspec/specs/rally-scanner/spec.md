# rally-scanner Specification

## Purpose

Find roadsurfer Rally one-way relocation offers through the unofficial booking API
and present them as a list and as an HTML map.

## Requirements

### Requirement: Polite API access

The scanner SHALL send every request to `https://booking.roadsurfer.com/api/en` with
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

### Requirement: Offer listing

The scanner SHALL list every rally timeframe that overlaps the requested window,
optionally filtered by origin and destination stations, and print the number of
offers found and one booking link per offer. The scanner SHALL NOT keep state between
runs and SHALL NOT mark offers as new.

#### Scenario: Full scan

- **WHEN** the user runs `python3 roadsurfer-rally.py`
- **THEN** the scanner prints a line with the offer count, then each offer and its
  booking link

#### Scenario: Filtered scan

- **WHEN** the user runs the scanner with `--from`, `--to`, `--start` or `--end`
- **THEN** only offers from the matching origins to the matching destinations that
  overlap the window are listed, and no file is written

### Requirement: Map output

With `--map FILE`, the scanner SHALL write an HTML file from
`rally-map.template.html` next to the script, replacing `/*DATA*/[]` with the JSON
offer records and `/*SCAN*/null` with the JSON scan metadata or `null`, escaping
every embedded `</` as `<\/`, and SHALL print the number of offers on the map. Both
SHALL come from the scan of the same run or, with `--from-json`, from a data file.
The page SHALL load Leaflet from `vendor/leaflet/` next to it.

#### Scenario: Map from a clean clone

- **WHEN** the user runs `python3 roadsurfer-rally.py --map index.html` in a clean
  clone
- **THEN** `index.html` is written, the scanner prints `map (N offers)`, and git
  ignores `index.html`

#### Scenario: Map from a data file

- **WHEN** the user runs `python3 roadsurfer-rally.py --from-json offers.json --map index.html`
- **THEN** `index.html` embeds the records and the `scan` object of `offers.json` and
  the scanner prints `map (N offers)` with the number of records in the file

#### Scenario: Data file without metadata

- **WHEN** the user renders with `--from-json` a data file that has no `scan` object
- **THEN** `index.html` is written and embeds `null` as the scan metadata

### Requirement: Scan data file

With `--json-out FILE`, the scanner SHALL write a UTF-8 JSON object whose `offers` key
holds the same offer records that `--map` embeds in the page, each with `km` and
`km_estimated`, and whose `scan` key holds the scan metadata: `finished_at` (UTC, ISO
8601), `offers`, `requests`, `failed`, `rate_limited`, `start`, `end`, `from` and `to`.
Readers SHALL tolerate other top-level keys and records without `km`.

#### Scenario: Scan to a data file

- **WHEN** the user runs `python3 roadsurfer-rally.py --from 1 --json-out offers.json`
- **THEN** `offers.json` holds an object whose `offers` list has one record per listed
  offer, each with `km` and `km_estimated`, and whose `scan` object has the finish time
  such as `2026-11-18T03:12:05Z`, the number of offers, the request, failed and HTTP
  429 counts the summary prints, the `--start` and `--end` window, `from` set to
  `["1"]` and `to` set to `null`

### Requirement: Offline rendering

With `--from-json FILE`, the scanner SHALL render the map from the data file without
sending any request, to roadsurfer or to a routing server. `--from-json` SHALL require
`--map` and SHALL be rejected together with `--list`, `--json-out`, `--from`, `--to`
or `--prices`.

#### Scenario: Render without network

- **WHEN** the user runs `python3 roadsurfer-rally.py --from-json offers.json --map index.html`
  with networking disabled
- **THEN** `index.html` is written and the scanner exits with status 0

#### Scenario: Data file without map

- **WHEN** the user runs `python3 roadsurfer-rally.py --from-json offers.json`
- **THEN** the scanner exits with a usage error and writes nothing

#### Scenario: Data file without road distances

- **WHEN** the user renders a data file whose records have no `km`
- **THEN** `index.html` is written, no request is sent, and the page shows the
  estimated distances labelled as estimates

### Requirement: Supported options

The scanner SHALL accept only `--to`, `--from`, `--start`, `--end`, `--prices`,
`--map`, `--json-out`, `--from-json`, `--delay`, `--release`, `--road-cache`,
`--routing-url`, `--list` and `--help`.

#### Scenario: Removed local-only option

- **WHEN** the user passes `--notify`, `--watch`, `--via` or `--detour`
- **THEN** the scanner exits with an unrecognized-argument error

### Requirement: Vendored Leaflet

The map template SHALL load Leaflet's JavaScript and CSS from `vendor/leaflet/` by
relative path. The repository SHALL ship an unmodified, pinned Leaflet 1.x release
there (`leaflet.js`, `leaflet.css`, `images/` and `LICENSE`) and record its version
in `vendor/leaflet/VERSION`. The page SHALL make no request to `unpkg.com`. Map tiles
keep loading from Esri World Street Map.

#### Scenario: unpkg blocked

- **WHEN** the map is generated in the repository root and served over HTTP with
  `unpkg.com` unreachable
- **THEN** Leaflet loads, the route lines and the default marker icon render, and the
  browser sends no request to `unpkg.com`

#### Scenario: Published page

- **WHEN** the map is published
- **THEN** `vendor/` is shipped next to `index.html`

### Requirement: Blocked scan detection

After a scan, the scanner SHALL print the number of requests, failed requests and
HTTP 429 responses, and the scan duration. A request counts as failed when the
scanner gives up on it. When more than 10% of the requests failed, the scanner SHALL
exit with a non-zero status and SHALL NOT write the `--json-out` or `--map` file.

#### Scenario: Healthy scan

- **WHEN** a scan with `--json-out offers.json --map index.html` finishes with at most
  10% failed requests
- **THEN** the scanner prints the request count, the failed count and the duration,
  writes both files and exits with status 0

#### Scenario: Blocked scan

- **WHEN** more than 10% of the requests of a scan fail
- **THEN** the scanner prints the request count, the failed count and the duration,
  exits with a non-zero status and writes neither the `--json-out` nor the `--map`
  file

### Requirement: Last-updated timestamp

When the map page has scan metadata, its toolbar SHALL show the time the scan
finished, in UTC to the minute. Without scan metadata it SHALL show no timestamp.

#### Scenario: Page with scan metadata

- **WHEN** a page whose scan finished at `2026-11-18T03:12:05Z` is opened
- **THEN** its toolbar shows `updated 2026-11-18 03:12 UTC`

#### Scenario: Page without scan metadata

- **WHEN** a page rendered from a data file without a `scan` object is opened
- **THEN** its toolbar shows the route and trip counts and no timestamp

### Requirement: Trip list view

The map page SHALL offer a list view, selected with a toggle in the toolbar, with one
row per trip that passes the active filters. The list SHALL use the same filter check
as the map, so its row count equals the trip count in the toolbar, and switching
views SHALL keep every filter selection.

#### Scenario: Filtered list

- **WHEN** the user picks a pick-up country and a distance range and switches to the
  list
- **THEN** the list has as many rows as the trip count in the toolbar, and switching
  back to the map keeps both filters

### Requirement: Trip list columns

Each list row SHALL show the start date, end date, pick-up station and country,
return station and country, road distance (with `~` when estimated), the price when
the page has prices, a booking link that opens in a new tab and a `map` button. Below
700 px the dates SHALL show as `MM-DD`, with the full date in the cell's `title` and
still read in full by assistive technology. Every value from the API SHALL be escaped
before it is inserted as HTML.

#### Scenario: Booking from the list

- **WHEN** the user clicks the booking link of a row
- **THEN** the trip's booking URL opens in a new tab and the view does not change

#### Scenario: Dates on a phone

- **WHEN** the list is shown 375 px wide
- **THEN** dates read `11-24` on one line, and the cell's title is `2026-11-24`

### Requirement: Trip list sorting

Rows SHALL be sorted by start date by default and SHALL be re-sortable by start date,
end date and distance from the column headers.

#### Scenario: Sort by distance

- **WHEN** the user clicks the distance header in the list
- **THEN** the rows are ordered by distance, and a second click reverses the order

### Requirement: Trip list selection

Each list row SHALL have a `map` button named `Show <from> to <to> on map`, the only
way to open a route from the list: the row itself SHALL NOT be focusable, clickable or
have a key handler. Activating the button SHALL show that route on the map with its
popup open; with the keyboard, focus SHALL move to the popup's first booking link.

#### Scenario: Row selection

- **WHEN** the user presses the `map` button of a row
- **THEN** the page shows the map zoomed to that route with the route's popup open

#### Scenario: Keyboard row selection

- **WHEN** a keyboard user activates the `map` button of a row
- **THEN** the map shows the route's popup and focus is on its first booking link

#### Scenario: Click on a row

- **WHEN** the user clicks a row outside its buttons and links
- **THEN** nothing happens

### Requirement: Supported Python versions

The scanner SHALL run on Python 3.8 and every newer Python 3 release, using only the
standard library.

#### Scenario: Oldest supported Python

- **WHEN** the user runs `python3 roadsurfer-rally.py --help` on Python 3.8
- **THEN** the help text is printed and the exit status is 0

### Requirement: Release tag in the map

With `--release TAG`, the scanner SHALL replace `/*RELEASE*/null` in the map page with
the tag as a JSON string, escaping every `</` as `<\/`; without `--release`, or with an
empty tag, it SHALL replace it with `null`. `--release` SHALL require `--map`.

#### Scenario: Map with a release tag

- **WHEN** the user runs
  `python3 roadsurfer-rally.py --from-json offers.json --map index.html --release v1.3.0`
- **THEN** `index.html` embeds `"v1.3.0"` as the release tag

#### Scenario: Map without a release tag

- **WHEN** the user renders without `--release` or with `--release ""`
- **THEN** `index.html` embeds `null` as the release tag

#### Scenario: Release without a map

- **WHEN** the user passes `--release` without `--map`
- **THEN** the scanner exits with a usage error and sends no request

### Requirement: Release tag attribution

When the map page has a release tag, it SHALL show the tag in the map's attribution
control, linked to the GitHub release of that tag, and the page SHALL have no footer.
Without a release tag the attribution SHALL show no release.

#### Scenario: Page with a release tag

- **WHEN** a page rendered with `--release v1.3.0` is opened
- **THEN** the map attribution shows `v1.3.0`, linked to
  `https://github.com/gjed/roadsurfer-rally-map/releases/tag/v1.3.0`

#### Scenario: Page without a release tag

- **WHEN** a page rendered without `--release` is opened
- **THEN** the attribution shows no release

### Requirement: Map page toolbar layout

The map page toolbar SHALL have a summary row with the page title, the last-updated
time, the route and trip counts and the map/list toggle, and a filter area with the
groups start date (from, to, week), distance, pick-up and return (country and station
each), followed by the reset button. Below 700 px the title SHALL be the short
`Rally map`, the filter area SHALL fold behind a `Filters` button that reports its
state with `aria-expanded`, and each dropdown SHALL have a row of its own.

#### Scenario: Phone width

- **WHEN** the page is opened 375 px wide
- **THEN** the toolbar shows only the short title, the counts, the last-updated time,
  the `Filters` button and the map/list toggle, and the map fills the rest of the
  screen

#### Scenario: Filters opened on a phone

- **WHEN** the user presses `Filters` at 375 px
- **THEN** every filter and the reset button are shown, each dropdown on its own row
  with its text readable, part of the map stays visible, and pressing `Filters` again
  hides them without changing any filter

#### Scenario: Desktop width

- **WHEN** the page is opened 1280 px wide
- **THEN** the summary row is shown, the grouped filters and the reset button share
  one row, and there is no `Filters` button

### Requirement: Active filter indication

The map page SHALL highlight every filter whose value differs from its reset value,
mark each filter group that has an active filter, and show the number of active
groups on the `Filters` button. Reset SHALL clear every highlight.

#### Scenario: Pick-up country chosen

- **WHEN** the user picks a pick-up country
- **THEN** that dropdown and the pick-up group are highlighted and the `Filters`
  button reads `Filters (1)`

#### Scenario: Reset

- **WHEN** the user presses reset
- **THEN** no filter or group is highlighted and the `Filters` button reads `Filters`

### Requirement: Map legend

The map SHALL show a legend that the user can collapse, explaining the route line,
the thicker line for routes with more trips, with sample weights that match the drawn
weights, one marker for a station (a click filters its pick-ups) and the direction of
the arcs. The legend SHALL start open at desktop widths and collapsed below 700 px.

#### Scenario: Reading the map

- **WHEN** the page is opened 1280 px wide
- **THEN** the legend shows a one-trip line, a five-or-more-trips line, a station
  marker with `click to filter pick-ups`, and that an arc bends to the right of the
  direction of travel from pick-up to return

### Requirement: Route popups

A route popup SHALL show the route, its road distance (labelled as an estimate when it
is one) and trip count, and a table with one row per trip: start date, end date, price
when present and a booking link that opens in a new tab with `rel="noopener"`. A long
table SHALL scroll inside the popup with its header row visible. Every value from the
API SHALL be escaped before it is inserted as HTML.

#### Scenario: Route with several trips

- **WHEN** the user opens the popup of a routed route with nine trips
- **THEN** the popup shows the route heading, `N km by road · 9 trips` and nine
  table rows in start-date order, each with a booking link

### Requirement: Map page accessibility

The page SHALL set a device-width viewport. Every filter, button and input SHALL have
an accessible name, text and controls SHALL meet WCAG 2.1 AA contrast, the route and
trip counts SHALL be announced to assistive technology when they change, and the
sorted list column SHALL carry `aria-sort`.

#### Scenario: Contrast

- **WHEN** the page is checked with an automated WCAG AA contrast check
- **THEN** no text or control fails it

### Requirement: Map page keyboard use

Every interactive element SHALL show a visible focus indicator when focused by
keyboard. Re-sorting the list SHALL keep focus on the header that was used. Route
lines and markers SHALL stay out of the tab order, since the list view reaches every
route through its `map` buttons, the list rows SHALL NOT be tab stops, and Escape
inside an open popup SHALL close it.

#### Scenario: Keyboard only

- **WHEN** a keyboard user tabs through the page
- **THEN** every filter, the reset button, the `Filters` button, the map/list toggle,
  the zoom buttons, the legend, the list headers, and each row's booking link and
  `map` button receive a visible focus indicator and can be operated with the
  keyboard, without stepping through the route lines or the rows themselves

### Requirement: Favicon

The map page SHALL embed its favicon in the page head as an inline SVG data URI, so
the published page and a page rendered locally with `--map` show it without any
extra file, and the browser SHALL request no favicon file from the server.

#### Scenario: Favicon on the published page

- **WHEN** the published page is opened
- **THEN** the browser tab shows the route icon and no request returns 404 for a
  favicon

### Requirement: Road distances

When a scan writes `--json-out` or `--map`, after the blocked-scan check, the scanner
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

- **WHEN** a scan writes neither `--json-out` nor `--map`
- **THEN** no routing request is sent

#### Scenario: Blocked scan routes nothing

- **WHEN** more than 10% of the roadsurfer requests of a scan fail
- **THEN** no routing request is sent and the road distance cache is not written

### Requirement: Polite routing

The scanner SHALL send routing requests one at a time, at least one second apart,
each with a User-Agent that names this project and at most 50 destinations. After an
HTTP 429 answer, or three failed routing requests in a row, it SHALL send no more
routing requests in that run. Routing failures SHALL NOT count as failed roadsurfer
requests, SHALL NOT make the scan fail and SHALL NOT change the roadsurfer requests or
their delay.

#### Scenario: Rate limited by the router

- **WHEN** the routing server answers HTTP 429
- **THEN** the scanner sends no further routing request, estimates the remaining pairs
  and still writes its files

#### Scenario: Roadsurfer pacing unchanged

- **WHEN** routing fails during a scan
- **THEN** the roadsurfer failed count and the exit status are the same as without the
  failure

### Requirement: Road distance cache

The scanner SHALL keep routed distances in a JSON file, `road-distances.json` by
default or the path of `--road-cache`, keyed by the pick-up and the return
coordinates in that order. It SHALL read the file before routing and SHALL route only
the pairs missing from it, and it SHALL write the file when it learned a pair. It
SHALL NOT store an estimate in it. An unreadable file SHALL be treated as empty.
Git SHALL ignore the default file.

#### Scenario: Second identical scan

- **WHEN** a scan runs again with the same options and the cache has every pair
- **THEN** the scanner sends no routing request and writes the same distances

#### Scenario: New pair

- **WHEN** a scan finds one pair that the cache does not have
- **THEN** only that pair is routed, and the cache then holds it

#### Scenario: Direction

- **WHEN** the cache has the pair A to B
- **THEN** a scan of the pair B to A routes it

### Requirement: Road distances in the page

The map page SHALL take the distance of a trip from the record's `km` for the
distance filter, the list's `km` column and sort, and the route popup and tooltip,
and SHALL use great-circle × 1.3 rounded to 10 km, as an estimate, for a record
without `km`.

#### Scenario: Distance filter

- **WHEN** the user sets the distance filter to 1000 to 1500 km
- **THEN** a trip passes when its record's `km` is in that range

### Requirement: Estimate labels and credit

The page SHALL show a routed distance as road km, without `~`. A distance that is
estimated, because `km_estimated` is true or `km` is missing, SHALL carry a leading `~`
and be labelled as an estimate in the popup, the tooltip and the list, and the page
SHALL explain `~` in a footer. When the page shows a routed distance it SHALL credit
OSRM and OpenStreetMap contributors in a footer that is visible in the map and in the
list view.

#### Scenario: Routed route

- **WHEN** the user opens the popup of a route whose records have `km` 1321 and
  `km_estimated` `false`
- **THEN** the popup shows `1321 km by road`, with no `~`, and the footer credits OSRM
  and OpenStreetMap contributors

#### Scenario: Estimated route

- **WHEN** the user opens the popup of a route whose records have `km_estimated` true
  or no `km`
- **THEN** the popup and the tooltip show `~N km (estimated)`, the list row shows `~N`,
  and the footer says that `~` marks an estimate

### Requirement: Station markers

The map SHALL draw one marker per station that has a trip under the active filters,
above the route lines, instead of a marker per route end. Clicking a marker SHALL set
the pick-up station filter to that station and SHALL NOT open any route popup. The
marker's tooltip SHALL show the station and the number of departures and arrivals
among the trips that pass the filters. A station with no departures SHALL ignore the
click.

#### Scenario: Busy station

- **WHEN** the user clicks the marker of a station with many routes
- **THEN** the pick-up station dropdown shows that station, the map shows only its
  departures and no route popup opens

#### Scenario: Station tooltip

- **WHEN** the user hovers a station marker
- **THEN** the tooltip shows the station name and `N departures · M arrivals` counted
  from the trips that pass the filters

### Requirement: Route highlight

A route line SHALL change to an accent colour at full opacity and be drawn above the
other lines while the pointer is over it or while its popup is open, and SHALL return
to its normal style when the pointer has left it and its popup is closed. A line
SHALL NOT stay highlighted after a tap on a touch screen once its popup closes or
another route is tapped.

#### Scenario: Popup open

- **WHEN** the user opens a route's popup, by clicking the line or from the list
- **THEN** the line is in the accent colour, at full opacity and drawn on top of the
  other lines, even after the pointer leaves it

#### Scenario: Popup closed

- **WHEN** the popup is closed and the pointer is not over the line
- **THEN** the line has its normal colour and opacity

#### Scenario: Tap on a touch screen

- **WHEN** the user taps a route and then taps another route or closes the popup
- **THEN** only the route whose popup is open is highlighted

### Requirement: Route line weight

A route line SHALL have the weight `min(1.5 + trips * .7, 5)` px and an opacity of .4,
so that overlapping routes can be told apart.

#### Scenario: Single and busy routes

- **WHEN** the page draws a route with 1 trip and a route with 5 or more trips
- **THEN** the first line is 2.2 px wide, the second 5 px wide, both at opacity .4

### Requirement: Initial map view

On first load the map SHALL fit the drawn routes and stations. Later changes to the
filters SHALL NOT move or zoom the map. When no route is drawn, the map SHALL show a
default view of Europe.

#### Scenario: First load

- **WHEN** the page is opened at 1280 px or 375 px wide
- **THEN** every drawn route and station is inside the visible map

#### Scenario: Filter after first load

- **WHEN** the user zooms the map and then changes a filter
- **THEN** the map keeps its centre and zoom

### Requirement: Booking link tap area

Under `@media (pointer: coarse)`, every booking link in the list and in popups SHALL
have a tap area of at least 24 by 24 CSS px, grown with padding and compensating
negative margins so that the rows do not become taller.

#### Scenario: Phone

- **WHEN** the page is used with a coarse pointer
- **THEN** each booking link measures at least 24 by 24 px and the list rows have the
  height they have with a fine pointer

### Requirement: Trip list layout

On a wide screen the list table SHALL be as wide as its content, at least 60% of the
list area, and SHALL right-align the distance header over the right-aligned distances.
The sticky header row SHALL have a visible bottom edge while rows scroll under it.

#### Scenario: Desktop list

- **WHEN** the list is shown at 1280 px
- **THEN** the table is not stretched to the full width, the `km` header sits over the
  right edge of the distances and the header keeps a bottom line while scrolling

### Requirement: Week slider follows typed dates

When the user types a start date range by hand, the week slider SHALL reset to its
first position and its `aria-valuetext` SHALL read `custom dates`.

#### Scenario: Dates typed after using the slider

- **WHEN** the user moves the week slider and then edits the earliest start date
- **THEN** the slider is back at its first position and announces `custom dates`

### Requirement: Return from a route popup

Escape in a route popup SHALL close it. For a popup opened from a list row, Escape
SHALL also show the list again with focus on the `map` button that opened it; for any
other popup, focus SHALL move to the map.

#### Scenario: Escape returns to the row

- **WHEN** the user presses Escape in a popup that was opened from a list row
- **THEN** the popup closes, the list is shown again and focus is on that row's `map`
  button

#### Scenario: Escape in a popup opened on the map

- **WHEN** the user presses Escape in a popup opened by clicking a route on the map
- **THEN** the popup closes and focus is on the map
