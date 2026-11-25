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
load from Esri's World Light Gray Canvas, base and reference labels, up to zoom 16.

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

When the map page has scan metadata, its app bar SHALL show the time the scan
finished, in UTC to the minute, as `Updated 18 Nov, 03:12 UTC`, with the offer, request
and failed-request counts in its tooltip. Without scan metadata it SHALL show no time.

#### Scenario: Page with scan metadata

- **WHEN** a page whose scan finished at `2026-11-18T03:12:05Z` is opened
- **THEN** its app bar shows `Updated 18 Nov, 03:12 UTC`

#### Scenario: Page without scan metadata

- **WHEN** a page rendered from a data file without a `scan` object is opened
- **THEN** its filter bar shows the trip and route counts and the page shows no time

### Requirement: Trips view

The page SHALL have two views, `Map` and `Trips`, chosen with links in the app bar that
mark the current one with `aria-current="page"`. The Trips view SHALL be a full page
with one row per trip that passes the active filters, a heading with the trip count and
a line with the route count and the date span. The list SHALL use the same filter check
as the map, so its row count equals the trip count in the filter bar, and switching
views SHALL keep every filter selection.

#### Scenario: Filtered list

- **WHEN** the user picks a pick-up country and a distance range and switches to `Trips`
- **THEN** the list has as many rows as the trip count in the filter bar, and switching
  back to `Map` keeps both filters

### Requirement: Trip list columns

Each Trips row SHALL show the start date, end date, nights, pick-up and return station
as `Name, CC`, road distance (with `~` when estimated), the price when the page has
prices, a `Map` button and a `Book` link that opens in a new tab. Dates SHALL show as
`Thu 19 Nov`, with the ISO date in the cell's `title`. Every value from the API SHALL be
escaped before it is inserted as HTML.

#### Scenario: Booking from the list

- **WHEN** the user clicks the booking link of a row
- **THEN** the trip's booking URL opens in a new tab and the view does not change

#### Scenario: Dates on a phone

- **WHEN** the Trips view is shown 375 px wide
- **THEN** dates read `Thu 19 Nov`, and the cell's title is `2026-11-19`

### Requirement: Trip list sorting

Rows SHALL be sorted by start date by default and SHALL be re-sortable by start date,
end date and distance from the column headers.

#### Scenario: Sort by distance

- **WHEN** the user clicks the distance header in the list
- **THEN** the rows are ordered by distance, and a second click reverses the order

### Requirement: Route from the Trips view

Each Trips row SHALL have a `Map` button named `Show <from> to <to> on the map`, the
only way to open a route from a row: the row itself SHALL NOT be focusable, clickable or
have a key handler. Activating the button SHALL switch to the Map view with that route
open (see `Route detail`) and focus on the detail's heading.

#### Scenario: Row selection

- **WHEN** the user presses the `Map` button of a row
- **THEN** the page shows the Map view zoomed to that route with its detail open

#### Scenario: Keyboard row selection

- **WHEN** a keyboard user activates the `Map` button of a row
- **THEN** focus is on the route detail's heading, and Back returns to the Trips view

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

### Requirement: App bar and filter bar layout

The page SHALL have an app bar with the logo, `Rally map`, the `Map | Trips` views,
the `Single rallies | Chains` switch and the scan time, and a filter bar with one chip
per filter, the counts and `Clear all`. Each chip SHALL be a button with
`aria-haspopup="dialog"` and `aria-expanded` that shows the filter's name and value and
opens a panel (`role="dialog"`) with its controls, which Escape and a click outside
close. Below 700 px the chips SHALL scroll sideways on one row.

#### Scenario: Phone width

- **WHEN** the page is opened 375 px wide
- **THEN** the app bar shows the title, the views, the mode switch and the scan time,
  the chips scroll sideways on one row, and the map and the route list fill the rest of
  the screen

#### Scenario: Filters opened on a phone

- **WHEN** the user presses a chip at 375 px
- **THEN** its panel opens inside the screen with every control readable, and pressing
  `Done` or Escape closes it without changing any filter

#### Scenario: Desktop width

- **WHEN** the page is opened 1280 px wide
- **THEN** the four filter chips share one row, and there is no `Filters` button

### Requirement: Active filter indication

The page SHALL highlight every control whose value differs from its reset value, and
each chip that has an active filter SHALL turn blue, show its value in bold and get an
`×` button named `Clear <name> filter` that clears that filter. Clearing SHALL remove
every highlight.

#### Scenario: Pick-up country chosen

- **WHEN** the user picks a pick-up country
- **THEN** that dropdown is highlighted and the `Pick-up` chip is blue, shows the country
  and has an `×`

#### Scenario: Reset

- **WHEN** the user presses `Clear all`
- **THEN** no control or chip is highlighted and every chip reads its default value

### Requirement: Map legend

The map SHALL show a legend that the user can collapse, with a one-trip line, a
five-or-more-trips line at their drawn weights and opacities, the highlighted route
and a station marker, worded `1 trip on this route`, `5 or more trips`,
`selected route` and `station: click to only show trips from here`. While the page has an
estimated distance, it SHALL add a fifth entry, `~ estimated distance, not routed`.
It SHALL start open at desktop widths and collapsed below 700 px.

#### Scenario: Reading the map

- **WHEN** the page is opened 1280 px wide with routed distances only
- **THEN** the legend shows the four samples with those labels and no explanation of
  the arc direction

#### Scenario: Estimates on the page

- **WHEN** the page is opened with at least one estimated distance
- **THEN** the legend also shows `~ estimated distance, not routed`

### Requirement: Route detail

Clicking a route card or line SHALL open the route in the sidebar, in place of the
list: `← All routes`, the stations, `By road` km, `Windows`, `Longest stay`, the trip
windows under the date and distance filters, each with dates, nights, price when present
and a `Book` link named after the route and date, then `Continue from`, `Also from <pick-up>` and `Show these trips in the list`. The map SHALL fit the route, draw it deep
orange with a `<from> → <to> · N trips` label and dim the others.

#### Scenario: Route with several trips

- **WHEN** the user opens a routed route with nine trips
- **THEN** the sidebar shows the route, `N km` by road, `9` windows and nine windows in
  start-date order, each with a booking link

### Requirement: Map page accessibility

The page SHALL set a device-width viewport. Every filter, button and input SHALL have
an accessible name, text and controls SHALL meet WCAG 2.1 AA contrast, the counts SHALL
be announced when they change, and the sorted column SHALL carry `aria-sort`. The view
links SHALL use `aria-current`, the mode and grouping buttons `aria-pressed`. Each
booking link SHALL be named after its route and date, and the route arrow SHALL be read
as `to`.

#### Scenario: Contrast

- **WHEN** the page is checked with an automated WCAG AA contrast check
- **THEN** no text or control fails it

#### Scenario: Booking links in a link list

- **WHEN** a screen reader lists the page's links
- **THEN** each reads like `Book Turin, IT to Marburg, DE, Thu 19 Nov`

### Requirement: Map page keyboard use

Every interactive element SHALL show a visible focus indicator when focused by
keyboard. Re-sorting or regrouping SHALL keep focus on the control that was used. Route
lines and markers SHALL stay out of the tab order, since the route cards reach every
route; the table rows SHALL NOT be tab stops. Focusing a card SHALL highlight its route
like hovering it.

#### Scenario: Keyboard only

- **WHEN** a keyboard user tabs through the page
- **THEN** the views, the mode switch, every chip and its panel, `Clear all`, the sort
  select, every route card, the zoom and fit buttons, the legend, the table headers, and
  each row's `Map` button and booking link receive a visible focus indicator and can be
  operated with the keyboard, without stepping through the route lines or the rows

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
and be labelled as an estimate in the popup, the tooltip and the list, and the map
legend SHALL explain `~` while the page has such a distance. When the page shows a
routed distance it SHALL credit OSRM and OpenStreetMap contributors in the map's
attribution control. The page SHALL have no footer for either.

#### Scenario: Routed route

- **WHEN** the user opens the popup of a route whose records have `km` 1321 and
  `km_estimated` `false`
- **THEN** the popup shows `1321 km by road`, with no `~`, and the map attribution
  credits OSRM and OpenStreetMap contributors

#### Scenario: Estimated route

- **WHEN** the user opens the popup of a route whose records have `km_estimated` true
  or no `km`
- **THEN** the popup and the tooltip show `~N km (estimated)`, the list row shows `~N`,
  and the legend says that `~` marks an estimate

#### Scenario: No footer

- **WHEN** the page is opened at 1280 px or 375 px wide
- **THEN** the page has no footer element and the attribution shows the credit

### Requirement: Station markers

The map SHALL draw one dark-outlined marker per station with a trip under the active
filters, above the routes, with a click target at least 32 px across; where targets
overlap, the nearest station with departures SHALL get the click. A click SHALL toggle the pick-up filter to that station; the selected station
SHALL be filled and larger, and a station without departures SHALL ignore the click.
The tooltip SHALL show `Name, CC`, the departures and arrivals, and what a click does.

#### Scenario: Busy station

- **WHEN** the user clicks the marker of a station with many routes
- **THEN** the `Pick-up` chip shows that station, the list is headed `From <station>`
  and the map shows only its departures

#### Scenario: Station tooltip

- **WHEN** the user hovers a station marker
- **THEN** the tooltip reads like `Munich, DE · N departures · M arrivals · Click to only show trips from here`, or `Click to show trips from every station` when selected

### Requirement: Route highlight

A route SHALL be drawn deep orange (`#C2410C`) on a white halo, above the other lines,
which drop to a low opacity, while the pointer or keyboard focus is on its card, while
the pointer is over its line, and while it is open. Pointing at a line SHALL also mark
its card and scroll it into view. The highlight SHALL go when none of these holds. A
line SHALL NOT stay highlighted after a tap on a touch screen unless the tap opened it.

#### Scenario: Popup open

- **WHEN** the user opens a route, by clicking the line or its card
- **THEN** the line is deep orange on a white halo, drawn on top of the other lines,
  even after the pointer leaves it

#### Scenario: Popup closed

- **WHEN** the route is closed, with `← All routes`, Escape or Back
- **THEN** the line has its normal colour and opacity

#### Scenario: Tap on a touch screen

- **WHEN** the user taps a route and then taps another route
- **THEN** only the route that is open is highlighted

### Requirement: Route line weight

A route line SHALL have the weight `min(1.5 + trips * .8, 5)` px and the opacity
`min(.4 + trips * .1, .85)`, so that busy routes stand out and single trips stay
faint.

#### Scenario: Single and busy routes

- **WHEN** the page draws a route with 1 trip and a route with 5 or more trips
- **THEN** the first line is 2.3 px wide at opacity .5, the second 5 px wide at .85

### Requirement: Initial map view

On first load the map SHALL fit the stations that have trips, at a whole-number zoom.
Later changes to the filters SHALL NOT move or zoom the map. When there are no
stations, the map SHALL show a default view of Europe.

#### Scenario: First load

- **WHEN** the page is opened at 1280 px or 375 px wide
- **THEN** every station is inside the visible map

#### Scenario: Filter after first load

- **WHEN** the user zooms the map and then changes a filter
- **THEN** the map keeps its centre and zoom

### Requirement: Booking link tap area

Under `@media (pointer: coarse)`, every booking link in the lists and the route and
chain details SHALL have a tap area of at least 24 by 24 CSS px.

#### Scenario: Phone

- **WHEN** the page is used with a coarse pointer
- **THEN** each booking link measures at least 24 by 24 px

### Requirement: Trip list layout

On a wide screen the trips table SHALL fill the page up to 1320 px, inside a box that
scrolls sideways when it must, with the distance header right-aligned over the
distances and a sticky header with a visible bottom edge. Below 700 px each row SHALL
be a card that fits the screen without horizontal scrolling, with its dates, distance,
stations and full-width `Map` and `Book` buttons, under a sticky bar with the sortable
headers.

#### Scenario: Desktop list

- **WHEN** the Trips view is shown at 1280 px
- **THEN** the distance header sits over the right edge of the distances and the header
  keeps a bottom line while scrolling

#### Scenario: Phone list

- **WHEN** the Trips view is shown 375 px wide
- **THEN** each trip is a card with its dates, distance, stations, `Map` button and
  `Book` link, and the list does not scroll sideways

### Requirement: Week slider follows typed dates

When the user types a start date range by hand, the week slider SHALL reset to its
first position and its `aria-valuetext` SHALL read `custom dates`.

#### Scenario: Dates typed after using the slider

- **WHEN** the user moves the week slider and then edits the earliest start date
- **THEN** the slider is back at its first position and announces `custom dates`

### Requirement: Return from a route or chain

`← All routes` (`← All chains`), Escape and the browser's Back SHALL close an open
route or chain and show the list again, with focus on the card that opened it, or on
the first card when it was opened from the map.

#### Scenario: Escape returns to the row

- **WHEN** the user presses Escape in a route opened from a card
- **THEN** the route closes, the list is shown again and focus is on that card

#### Scenario: Escape in a popup opened on the map

- **WHEN** the user presses Escape in a route opened by clicking its line
- **THEN** the route closes and focus is on its card, or the first card when it is not
  listed

### Requirement: Clear all

`Clear all` SHALL be in the filter bar and SHALL be shown only while at least one
filter differs from its reset value. Pressing it SHALL clear every filter and the chain
options, and focus SHALL move to the first chip.

#### Scenario: Nothing filtered

- **WHEN** the page is opened and no filter has been changed
- **THEN** there is no `Clear all`

#### Scenario: Filter active

- **WHEN** the user picks a pick-up station
- **THEN** `Clear all` is shown next to the counts, and pressing it clears every
  filter and hides it

### Requirement: Filter chip state

A chip SHALL show that its panel is open, besides `aria-expanded`. Hover styles SHALL
apply only to devices that can hover, so no control stays in its hover style after a
tap.

#### Scenario: Panel open on a phone

- **WHEN** the user presses a chip at 375 px
- **THEN** the chip's arrow points up and `aria-expanded` is true until the panel is
  closed

### Requirement: Empty state

When no trip passes the filters, the page SHALL say `No trips match the filters.` over
the map and in the list, with a `Reset filters` button that clears every filter. When
the page has no trips at all, it SHALL say `No rally trips are on offer right now.`
and show no button.

#### Scenario: Filters match nothing

- **WHEN** the user filters to a pick-up and a return that no trip connects
- **THEN** the map shows the message and `Reset filters`, and pressing it restores
  every trip

#### Scenario: No data

- **WHEN** the page is rendered from a data file with no offers
- **THEN** it says `No rally trips are on offer right now.` and has no reset button

### Requirement: Map size follows the layout

The map SHALL recompute its size whenever its element changes size, so that its view
and fit stay correct when the toolbar changes height, and a strip of the map SHALL
never be left without tiles.

#### Scenario: Toolbar changes height

- **WHEN** the filters wrap onto another row or the week slider changes the toolbar's
  height
- **THEN** the map fills the space below the toolbar and keeps its centre

### Requirement: Route click presentation

Clicking or tapping a route SHALL NOT draw a focus rectangle around it.

#### Scenario: Click a route

- **WHEN** the user clicks a route
- **THEN** it opens, only that route is highlighted and no focus rectangle is drawn

### Requirement: Week slider positions

The week slider's first position SHALL mean all dates, and position k SHALL mean the
seven days starting `k - 1` weeks after the first start date, with `aria-valuetext`
`all dates` or `week of Thu 19 Nov`. The slider's label SHALL read `Week`.

#### Scenario: Back to the start

- **WHEN** the user moves the week slider and then drags it back to the first position
- **THEN** the start date range is the full range again and the slider announces
  `all dates`

### Requirement: Chain mode

The app bar SHALL have a `Single rallies | Chains` switch whose buttons carry
`aria-pressed`. A chain is a sequence of 2 or 3 rally legs, each booked as its own
trip, found from the offers on the page without any request. Switching modes SHALL keep
every filter and the view and close an open route or chain. The count SHALL read
`N chains`, or `Showing 200 of N chains` above 200. `Chains` SHALL have a title that
says what chains are.

#### Scenario: Entering chain mode

- **WHEN** the user presses `Chains` on a page with offers
- **THEN** the button is pressed and the filter bar reads `N chains`

#### Scenario: Back to trips

- **WHEN** the user presses `Single rallies`
- **THEN** the map and lists show trips as before

#### Scenario: No chain exists

- **WHEN** no two offers can be joined under the current settings
- **THEN** the page shows the empty state `No chains match` with a reset button, and
  it suggests only the settings that are not already at their maximum

### Requirement: Chain settings

In chain mode a `Chain options` chip, hidden in trip mode, SHALL show the options and
open a panel with them: legs (`2`, `3`, `2 or 3`; default `2`), `Same day` (on) with 0
to 7 rest days (0), the next pick-up within (same station, `~25`, `~50`, `~100`,
`~150`, `~250 km`; same station), the shortest and longest trip days and the max total
km (empty: any) and `Round trip` (off). Every control SHALL update the results, typed
numbers after a short pause.

#### Scenario: Defaults

- **WHEN** the user enters chain mode
- **THEN** the controls read `2`, `Same day` checked, `0`, `same station`, empty, empty,
  empty and `Round trip` unchecked, and the chip is not marked as changed

#### Scenario: Three legs

- **WHEN** the user selects `2 or 3`
- **THEN** the chains of 3 legs are added to the chains of 2 legs

#### Scenario: Exactly three legs

- **WHEN** the user selects `3`
- **THEN** every chain listed has 3 legs

### Requirement: Chain legs

An offer SHALL be treated as a window. A leg SHALL be a pick-up day and a return day
inside one window, the return after the pick-up and at most 7 nights later, on days that
are the start or end of some offer on the page.

#### Scenario: Leg inside a window

- **WHEN** an offer's window is 14 to 21 December and offers start or end on every
  day from the 14th to the 21st
- **THEN** a chain may use it for 14 to 18 December or 15 to 21 December

#### Scenario: Closed days

- **WHEN** no offer starts or ends on a Sunday
- **THEN** no leg picks up or returns on a Sunday

### Requirement: Chain dates and booking links

For every chain the page SHALL keep the dates with the most nights on the road, then the
fewest rest days, then the earliest first pick-up. Each leg's booking link SHALL be the
offer's own link with `start-date` and `end-date` set to the leg's dates. Total days
SHALL be the days from the first pick-up to the last return.

#### Scenario: Link for part of a window

- **WHEN** a chain uses an offer for 14 to 21 December at 14 to 18 December
- **THEN** its booking link has `start-date=2026-12-14` and `end-date=2026-12-18` and
  the offer's stations

#### Scenario: Whole window

- **WHEN** a leg uses its offer's whole window
- **THEN** its booking link is identical to the offer's link

### Requirement: Chain options panel

The `Same day` checkbox and the rest days SHALL read as one sentence: `Same day or up to N rest days` when checked, `Same day 1 to N rest days` when not. The panel SHALL have a
`Reset` button that restores the chain options only. A control that is not at its
default SHALL be marked, and so SHALL the chip; the chip SHALL NOT be marked while
everything is at its default.

#### Scenario: Unchecked

- **WHEN** the user unchecks `Same day` and selects 3 rest days
- **THEN** the options read `Same day 1 to 3 rest days`

#### Scenario: Tab order

- **WHEN** a keyboard user opens the `Chain options` panel
- **THEN** focus is on `Legs`, the first control, and Tab stays inside the panel

#### Scenario: Panel reset

- **WHEN** the user changes the legs and presses the panel's `Reset`
- **THEN** every chain option is back to its default and the other filters are kept

### Requirement: Chain rest days

Leg N+1 SHALL start on the day leg N ends or up to the selected number of rest days
later, never earlier; with `Same day` unchecked it SHALL start 1 to that many days after
leg N ends. The rest days SHALL go up to 7. A hand-over at the same station SHALL read
`Hand-over in <station> · same day` or `Hand-over in <station> · N rest days`.

#### Scenario: No rest days

- **WHEN** `Same day` is checked and rest days are 0
- **THEN** every second leg starts on the day the first ends

#### Scenario: Rest days allowed

- **WHEN** the user allows up to 2 rest days
- **THEN** every chain from before is still found and chains with 1 or 2 rest days are
  added, each showing its rest days

#### Scenario: Not the same day

- **WHEN** the user unchecks `Same day` and sets 3 rest days
- **THEN** every hand-over of every chain listed is 1, 2 or 3 days long

#### Scenario: Same day unchecked with no rest days

- **WHEN** the user unchecks `Same day` while rest days are 0
- **THEN** rest days become 1 and 0 can not be selected until `Same day` is checked again

### Requirement: Chain connections

Leg N+1 SHALL start at the station where leg N ended or, with a next pick-up distance
selected, at another station within that many km of it, measured as the straight line ×
1.3 rounded to 10 km and shown with `~`. A station SHALL NOT be a pick-up twice in one
chain. A hand-over to another station SHALL read `Hop ~N km <A> → <B> on your own`,
then `same day` or `N rest days`, and be drawn with a dotted rule.

#### Scenario: Strictest settings

- **WHEN** rest days are 0, `Same day` is checked and the next pick-up is the same station
- **THEN** every chain's legs hand over at the same station on the same day

#### Scenario: Connection allowed

- **WHEN** the user allows a next pick-up within 50 km
- **THEN** every chain from before is still found and chains with a connection of up to
  50 km are added

#### Scenario: Widest connection

- **WHEN** the user selects `~250 km`
- **THEN** chains with a connection of up to 250 km are listed

#### Scenario: Connection shown

- **WHEN** a chain's second leg starts 40 km from where the first ended
- **THEN** its hand-over reads like `Hop ~40 km A → B on your own · same day`

### Requirement: Chain filters

In chain mode the start date filter and the week slider SHALL limit the first pick-up
day, the distance filter SHALL limit the distance of every leg, the pick-up filters SHALL
apply to where the chain starts and the return filters to where it ends, and their
chips SHALL be labelled `First pick-up`, `Distance per leg`, `Chain starts at` and
`Chain ends at`. The dropdown options SHALL count chains. The stations in between SHALL
NOT be filtered.

#### Scenario: Pick-up station

- **WHEN** the user picks a pick-up station in chain mode
- **THEN** every chain listed starts at it and the dropdowns count chains

#### Scenario: Week

- **WHEN** the user moves the week slider
- **THEN** every chain listed starts in that week

### Requirement: Chain cards

In chain mode the sidebar and the Trips view SHALL show one card per chain with its
stations (`Berlin → Barcelona → Lisbon`), its first pick-up and last return as `Mon 14 Dec`, and badges for the total days, the km driven (legs only, `~` when any is
estimated) and the rest days. Clicking a sidebar card, or a Trips card's `Map` button
named `Show chain <legs> on the map`, SHALL open the chain.

#### Scenario: Row

- **WHEN** a chain starts on 14 December and ends on 28 December
- **THEN** its card shows `Mon 14 Dec – Mon 28 Dec`, `14 days` and its km driven

### Requirement: Chain legs in the list

Each Trips chain card and each open chain SHALL have one numbered entry per leg with its
stations, dates, nights or distance and a `Book` link that opens in a new tab, named
after the leg, and the hand-over before every leg after the first.

#### Scenario: Booking each leg

- **WHEN** the user opens the `Book` links of a two-leg chain
- **THEN** each opens the booking page of that leg's stations and dates

### Requirement: Chain list size

The chain lists SHALL show the first 200 chains in the sort order, and the filter bar
SHALL show how many chains there are in all, as `Showing 200 of 23,267 chains`.

#### Scenario: More than 200 chains

- **WHEN** there are 2075 chains
- **THEN** the filter bar reads `Showing 200 of 2,075 chains`, the list has 200 cards
  and a note says how many are shown

### Requirement: Chain list sorting

Chains SHALL be sorted by total days, then by km driven, by default, and SHALL be
re-sortable with a `Sort` select: most days, earliest start, earliest end, shortest
drive and longest drive, with focus kept on the select. The map SHALL draw the chains
the list shows.

#### Scenario: Sort by km driven

- **WHEN** the user selects `Shortest drive` in chain mode
- **THEN** the cards are ordered by km driven, `Longest drive` reverses the order, and
  the map draws the new first 200

### Requirement: Chain map lines

In chain mode the map SHALL draw each leg of the listed chains once, as a solid arc
with the weight and opacity of the number of chains that use it, and each connection to
another station as a dotted straight line in a second colour on a white casing. Station
markers SHALL show
how many chains start and end there, and clicking one that has chains starting there
SHALL toggle the pick-up filter.

#### Scenario: Connections drawn dotted

- **WHEN** chain mode lists a chain with a 40 km connection
- **THEN** its two legs are solid arcs and the connection between the two stations is a
  dotted line

### Requirement: Chain selection

A chain card, a `Trips` chain card or its `Map` button, and a leg or connection that only
one chain uses SHALL open the chain in the sidebar in place of the list: a back button, its
stations as the heading, `On the road`, `Driven` and `Rest days`, its numbered legs with
dates, nights, km and a `Book` link each, the hand-overs, and a note that the dates are
inferred. The map SHALL fit the chain and draw it over the dimmed others, its legs
highlighted and numbered. Focus SHALL move to the heading.

#### Scenario: Chain from the list

- **WHEN** the user clicks a chain card
- **THEN** the page shows the map fitted to the chain with its legs highlighted and
  numbered, and a `Book` link for each leg in the sidebar

#### Scenario: Keyboard

- **WHEN** a keyboard user activates a chain card
- **THEN** focus is on the chain's heading in the sidebar

### Requirement: Chain selection lifetime

An open chain SHALL stay open until the back button, Escape, Back, a mode switch, a click
on a leg or connection it does not use, or a change of the filters or options that
removes it. A click on empty map or on any part of the chain SHALL NOT close it. Escape
in a chain opened from the chains of a leg SHALL return to that list; a second Escape
SHALL remove the leg filter.

#### Scenario: Closing the popup

- **WHEN** the user clicks the map while a chain is open
- **THEN** the chain stays open until the user presses the back button, Escape or Back

#### Scenario: Escape in a leg popup

- **WHEN** a chain opened from the chains of a leg is open and the user presses Escape
- **THEN** the chain closes and the leg's chains are listed; a second Escape lists every
  chain

### Requirement: Chain legend

In chain mode the legend SHALL read `leg of 1 chain`, `10 or more chains`, `connection to the next pick-up (train, bus)`, `selected chain` and `station: click to only show chains starting here`, and it
SHALL keep the estimate entry when a connection is allowed or a distance is estimated and
end with `click a line to pick a chain`.

#### Scenario: Legend in chain mode

- **WHEN** the user opens the legend in chain mode
- **THEN** it has an entry with a dotted line labelled `connection to the next pick-up (train, bus)`

### Requirement: Chain empty-state hints

When no chain matches, the page SHALL suggest relaxing at most two chain options, in this
order and only those not at their widest: `allow same-day changes`, `allow more rest days`, `allow a farther next pick-up`, `allow 3 legs`, `remove the trip length, km or round-trip limit`.

#### Scenario: Two hints

- **WHEN** no chain matches with `Same day` unchecked and 3 rest days
- **THEN** the empty state reads `No chains match. Try: allow same-day changes, allow more rest days, or reset the filters.`

### Requirement: Chain trip limits

The trip days SHALL limit the days from the first pick-up to the last return, the max
total km SHALL limit the km of the legs (connections not included), and an empty field
SHALL mean no limit. `Round trip` SHALL keep only chains whose last return station is
the first pick-up station or, with a next pick-up distance selected, within that
distance of it. A chain SHALL keep the best dates that satisfy the trip days.

#### Scenario: Trip days

- **WHEN** the user sets a minimum of 10 and a maximum of 12 trip days
- **THEN** every chain listed lasts 10 to 12 days

#### Scenario: Max km

- **WHEN** the user sets 1500 max total km
- **THEN** every chain listed has 1500 km or less driven

#### Scenario: Round trip

- **WHEN** the user checks `Round trip` with the same station as next pick-up
- **THEN** every chain listed ends at the station where it starts

### Requirement: Chain options as filters

A chain option that is not at its default SHALL count as an active filter and show
`Clear all` while chain mode is on, and `Clear all` SHALL restore every chain option to
its default. In trip mode the options SHALL NOT count.

#### Scenario: Changed option

- **WHEN** the user changes the legs to `3`
- **THEN** the `Chain options` chip is marked and `Clear all` shows

#### Scenario: Reset restores chain options

- **WHEN** the user presses `Clear all` after changing several chain options
- **THEN** every chain option is back to its default and `Clear all` hides itself

### Requirement: Chain options on phones

On a phone, turning `Chains` on SHALL open the `Chain options` panel, with
`aria-expanded` true on its chip, so that the options show without another tap.

#### Scenario: Chains on at 375 px

- **WHEN** the user presses `Chains` on a 375 px wide screen
- **THEN** the chain options panel is open and its chip is expanded

#### Scenario: Chains off

- **WHEN** the user presses `Single rallies`
- **THEN** the chain options panel closes and its chip is hidden

### Requirement: Chain search time

With the widest chain options on a scan of about 800 offers, finding the chains SHOULD take
well under a second on a desktop, and the default options SHALL take under 100 ms.

#### Scenario: Default options

- **WHEN** the user enters chain mode on a scan of about 800 offers
- **THEN** the chains appear without a noticeable delay

### Requirement: Chain leg list

In chain mode a click or tap on a leg or a connection that the open chain does not use
SHALL close that chain and list in the sidebar, in list order, the chains that use it,
headed `N chains use this leg` (or `hop`) and drawn in orange on the map. When only one
chain uses it, that chain SHALL open at once. Choosing a card SHALL open its chain, with
`← Chains using <leg>` to return to the list.

#### Scenario: Leg used by three chains

- **WHEN** the user clicks a blue leg used by three chains
- **THEN** the sidebar reads `3 chains use this leg` with three cards, in list order

#### Scenario: Choosing a chain

- **WHEN** the user chooses a chain in that list
- **THEN** the chain opens as from any chain card, and its back button reads `Chains using <leg>`

#### Scenario: Busy leg

- **WHEN** the user clicks a leg used by 14 of the chains on the map and 37 in all
- **THEN** the sidebar lists the 37 chains

#### Scenario: Leg used by one chain

- **WHEN** the user clicks a leg that only one chain uses
- **THEN** that chain opens at once with that leg marked

### Requirement: Chain leg list layout

The chains of a leg SHALL be listed under the sidebar's sticky header, `N chains use this leg` (or `hop`) with `Pick one to open it`, so only the cards scroll; the leg filter
itself shows only as its chip. A tap on a line outside an open filter panel SHALL close the panel and still
list that line's chains.

#### Scenario: Tap on a line on a phone

- **WHEN** the user taps a leg outside the open chain options panel
- **THEN** the panel closes and the leg's chains are listed

### Requirement: Chain leg filter

The chains of a leg SHALL be a filter: it SHALL count as an active filter and show
`Clear all`, show once, as a `Chain uses <Leg|Hop> <from> → <to>` chip with a `×`
button after the other filter chips, and be cleared by `Clear all`, by its `×`, by
Escape with no chain open and by switching to single rallies.

#### Scenario: Show all

- **WHEN** the user clicks a leg used by 37 chains
- **THEN** the list shows the chains of that leg, the `Chain uses` chip shows and `Clear all` shows

#### Scenario: Reset with a leg filter

- **WHEN** the user presses `Clear all` with that filter on
- **THEN** the filter is gone and the list shows every chain again

### Requirement: Chain leg filter scope

The leg filter SHALL apply to the map, the list and the station dropdown counts, and
station clicks and the other filters SHALL keep it. With no chain left, the first hint
SHALL be `remove the leg filter`.

#### Scenario: Pick-up dropdown

- **WHEN** the leg filter is on
- **THEN** the `Chain starts at` dropdown counts only the chains that use the leg

### Requirement: Chain card selection

A click or tap on a `Trips` chain card outside its links, its buttons and a text
selection SHALL open that chain like its `Map` button, and a card SHALL show a pointer
cursor. The card of the open chain SHALL be highlighted and its `Map` button marked
`aria-current`.

#### Scenario: Click on a chain row

- **WHEN** the user clicks the days badge of a `Trips` chain card
- **THEN** the map view opens with that chain, and back on `Trips` its card is
  highlighted

#### Scenario: Link in a row

- **WHEN** the user clicks the `Book` link of a leg in a card
- **THEN** the booking page opens and the chain is not opened

### Requirement: Chain line hit area

A leg and a connection SHALL be hit by a click or a tap within a band wider than the
line, and its tooltip SHALL name the number of chains on the map that use it and say
that a click lists them.

#### Scenario: Tap beside a line

- **WHEN** the user taps 8 px beside a thin leg at 375 px
- **THEN** the chains of that leg are listed

### Requirement: Chain selection parts

A click on a leg or a connection of the open chain SHALL keep the chain, mark that leg
or hand-over in the sidebar (orange border, scrolled into view) and draw the other legs
thinner. A click on a station of the open chain SHALL do nothing. Each part SHALL have a
tooltip that says what a click does.

#### Scenario: Second leg

- **WHEN** the user clicks the second leg of the open chain
- **THEN** the chain stays open and its second leg is marked in the sidebar

### Requirement: Route list

The Map view SHALL show a sidebar beside the map with one card per route that passes
the filters: the pick-up and return station, the distance, the trip count and `Next <date> · windows until <date>`. Its sticky header SHALL show the route and trip counts
and the date span, or `From <station>` with a pick-up station filter, and a `Sort`
select: earliest start (default), shortest drive, longest drive, most trips. Each card
SHALL be a button that opens its route.

#### Scenario: Sorted by drive

- **WHEN** the user selects `Shortest drive`
- **THEN** the first card is the route with the fewest km

#### Scenario: Card hover

- **WHEN** the user points at a card
- **THEN** its route is highlighted on the map and the other routes are dimmed

### Requirement: Trips view grouping

The trips table SHALL group its rows by none (default), route or pick-up with a `Group by` switch whose buttons carry `aria-pressed`. Each group SHALL start with a header row
(`<th scope="rowgroup">`) that names it and counts its trips, and the groups SHALL
follow the sorted order of their first rows.

#### Scenario: Group by route

- **WHEN** the user groups by route
- **THEN** every trip is under the header of its route, with the route's km and trip
  count

### Requirement: Page state in the URL

The page SHALL keep its view (`#map` or `#trips`), mode, filters, leg filter, chain options, open
route or chain, sort orders and grouping in the URL hash, leaving defaults out. Filter
changes SHALL replace the history entry; switching views and opening a route or chain
from a list SHALL add one. Opening the page with a hash SHALL restore that state;
unknown parameters and invalid values SHALL be ignored.

#### Scenario: Shared link

- **WHEN** the user opens `#trips?from=Munich&sort=km`
- **THEN** the Trips view lists the trips from Munich by distance

#### Scenario: Back closes a route

- **WHEN** the user opens a route from the list and presses the browser's Back
- **THEN** the route closes and the list is shown

#### Scenario: Invalid value

- **WHEN** the user opens `#map?sort=bogus&route=Nowhere`
- **THEN** the page shows the default route list

### Requirement: Continue from

An open route SHALL list under `Continue from <return station>` the routes of the scan
that leave its return station and whose windows end on or after its first start, each
with its trip count, next start and km, or say `No rally leaves <station> in this scan.` Clicking one SHALL open that route, replacing the history entry.

#### Scenario: Continue from

- **WHEN** the user opens a route and then a route under `Continue from`
- **THEN** the second route opens, and one Back returns to the list
