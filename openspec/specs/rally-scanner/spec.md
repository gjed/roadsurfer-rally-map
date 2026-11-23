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

Each list row SHALL show the start date, end date, pick-up and return station as
`Name, CC`, road distance (with `~` when estimated), the price when the page has
prices, a `Map` button and a `Book` link that opens in a new tab. Below 700 px the
dates SHALL show as `Thu 19 Nov`, with the ISO date in the cell's `title`. Every value
from the API SHALL be escaped before it is inserted as HTML.

#### Scenario: Booking from the list

- **WHEN** the user clicks the booking link of a row
- **THEN** the trip's booking URL opens in a new tab and the view does not change

#### Scenario: Dates on a phone

- **WHEN** the list is shown 375 px wide
- **THEN** dates read `Thu 19 Nov`, and the cell's title is `2026-11-19`

### Requirement: Trip list sorting

Rows SHALL be sorted by start date by default and SHALL be re-sortable by start date,
end date and distance from the column headers.

#### Scenario: Sort by distance

- **WHEN** the user clicks the distance header in the list
- **THEN** the rows are ordered by distance, and a second click reverses the order

### Requirement: Trip list selection

Each list row SHALL have a `Map` button named `Show <from> to <to> on the map`, the
only way to open a route from the list: the row itself SHALL NOT be focusable,
clickable or have a key handler. Activating the button SHALL show that route on the map
with its popup open; with the keyboard, focus SHALL move to the popup's first booking
link.

#### Scenario: Row selection

- **WHEN** the user presses the `Map` button of a row
- **THEN** the page shows the map zoomed to that route with the route's popup open

#### Scenario: Keyboard row selection

- **WHEN** a keyboard user activates the `Map` button of a row
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
time, the route and trip counts, the `Reset` button and the map/list toggle, and a
filter area with the groups start date (from, to, week), distance, pick-up and return
(country and station each). Below 700 px the title SHALL be the short `Rally map`, the
filter area SHALL fold behind a `Filters` button that reports its state with
`aria-expanded`, and each dropdown SHALL have a row of its own.

#### Scenario: Phone width

- **WHEN** the page is opened 375 px wide
- **THEN** the toolbar shows only the short title, the counts, the last-updated time,
  the `Filters` button, the map/list toggle and, while a filter is active, `Reset`,
  and the map fills the rest of the screen

#### Scenario: Filters opened on a phone

- **WHEN** the user presses `Filters` at 375 px
- **THEN** every filter is shown, each dropdown on its own row with its text readable,
  part of the map stays visible, and pressing `Filters` again hides them without
  changing any filter

#### Scenario: Desktop width

- **WHEN** the page is opened 1280 px wide
- **THEN** the summary row is shown, the four filter groups share one row, and there is
  no `Filters` button

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

The map SHALL show a legend that the user can collapse, with a one-trip line, a
five-or-more-trips line at their drawn weights and opacities, the highlighted route
and a station marker, worded `1 trip on this route`, `5 or more trips`,
`selected route` and `station: click for trips from here`. While the page has an
estimated distance, it SHALL add a fifth entry, `~ estimated distance, not routed`.
It SHALL start open at desktop widths and collapsed below 700 px.

#### Scenario: Reading the map

- **WHEN** the page is opened 1280 px wide with routed distances only
- **THEN** the legend shows the four samples with those labels and no explanation of
  the arc direction

#### Scenario: Estimates on the page

- **WHEN** the page is opened with at least one estimated distance
- **THEN** the legend also shows `~ estimated distance, not routed`

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
sorted list column SHALL carry `aria-sort`. Each booking link SHALL be named after its
route and date, and the route arrow SHALL be read as `to`.

#### Scenario: Contrast

- **WHEN** the page is checked with an automated WCAG AA contrast check
- **THEN** no text or control fails it

#### Scenario: Booking links in a link list

- **WHEN** a screen reader lists the page's links
- **THEN** each reads like `Book Turin, IT to Marburg, DE, Thu 19 Nov`

### Requirement: Map page keyboard use

Every interactive element SHALL show a visible focus indicator when focused by
keyboard. Re-sorting the list SHALL keep focus on the header that was used. Route
lines and markers SHALL stay out of the tab order, since the list view reaches every
route through its `Map` buttons, the list rows SHALL NOT be tab stops, and Escape
inside an open popup SHALL close it.

#### Scenario: Keyboard only

- **WHEN** a keyboard user tabs through the page
- **THEN** every filter, the reset button, the `Filters` button, the map/list toggle,
  the zoom buttons, the legend, the list headers, and each row's `Map` button and
  booking link receive a visible focus indicator and can be operated with the
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
filters, above the route lines. Clicking one SHALL toggle the pick-up filter to that
station without opening a route popup; the selected station SHALL be filled and
larger, and a station with no departures SHALL ignore the click. The tooltip SHALL
show `Name, CC`, the departures and arrivals among the trips that pass the filters,
and what a click does.

#### Scenario: Busy station

- **WHEN** the user clicks the marker of a station with many routes
- **THEN** the pick-up station dropdown shows that station, the map shows only its
  departures and no route popup opens

#### Scenario: Station tooltip

- **WHEN** the user hovers a station marker
- **THEN** the tooltip shows `Munich, DE`, `N departures · M arrivals` and
  `Click to show trips from here`, or `Click to show all pick-ups` when selected

### Requirement: Route highlight

A route line SHALL change to a deep orange (`#bf360c`, at least 3:1 against the
basemap), full opacity, a little more weight and a white halo, and be drawn above the
other lines, while the pointer is over it or while its popup is open. It SHALL return
to its normal style when the pointer has left it and its popup is closed, and always
when its popup closes. A line SHALL NOT stay highlighted after a tap on a touch
screen.

#### Scenario: Popup open

- **WHEN** the user opens a route's popup, by clicking the line or from the list
- **THEN** the line is deep orange, at full opacity and drawn on top of the other
  lines, even after the pointer leaves it

#### Scenario: Popup closed

- **WHEN** the popup is closed, with its close button or Escape
- **THEN** the line has its normal colour and opacity, also when the pointer is still
  over it

#### Scenario: Tap on a touch screen

- **WHEN** the user taps a route and then taps another route or closes the popup
- **THEN** only the route whose popup is open is highlighted

### Requirement: Route line weight

A route line SHALL have the weight `min(1.5 + trips * .7, 5)` px and the opacity
`min(.35 + trips * .1, .8)`, so that busy routes stand out and single trips stay
faint.

#### Scenario: Single and busy routes

- **WHEN** the page draws a route with 1 trip and a route with 5 or more trips
- **THEN** the first line is 2.2 px wide at opacity .45, the second 5 px wide at .8

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

Under `@media (pointer: coarse)`, every booking link in the list and in popups SHALL
have a tap area of at least 24 by 24 CSS px, grown with padding and compensating
negative margins so that the rows do not become taller.

#### Scenario: Phone

- **WHEN** the page is used with a coarse pointer
- **THEN** each booking link measures at least 24 by 24 px and the list rows have the
  height they have with a fine pointer

### Requirement: Trip list layout

On a wide screen the list table SHALL be as wide as its content and at least 720 px or
the list area, whichever is smaller, with the distance header right-aligned over the
distances. Below 700 px each row SHALL be a two-line card that fits the screen without
horizontal scrolling, under a sticky bar with the sortable headers. The sticky header
SHALL have a visible bottom edge.

#### Scenario: Desktop list

- **WHEN** the list is shown at 1280 px
- **THEN** the table is not stretched to the full width, the `km` header sits over the
  right edge of the distances and the header keeps a bottom line while scrolling

#### Scenario: Phone list

- **WHEN** the list is shown 375 px wide
- **THEN** each trip is a card with its dates, distance, stations, `Map` button and
  `Book` link, and the list does not scroll sideways

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

### Requirement: Reset button

The `Reset` button SHALL be in the toolbar's summary row and SHALL be shown only while
at least one filter differs from its reset value. After it is pressed, focus SHALL move
to the map/list toggle.

#### Scenario: Nothing filtered

- **WHEN** the page is opened and no filter has been changed
- **THEN** there is no `Reset` button

#### Scenario: Filter active

- **WHEN** the user picks a pick-up station
- **THEN** `Reset` is shown next to the `Filters` button, and pressing it clears every
  filter and hides it

### Requirement: Filters button state

The `Filters` button SHALL show when its panel is open, besides `aria-expanded`.
Hover styles SHALL apply only to devices that can hover, so no control stays in its
hover style after a tap.

#### Scenario: Panel open on a phone

- **WHEN** the user presses `Filters` at 375 px
- **THEN** the button is highlighted in the accent colour until the panel is closed

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

Clicking or tapping a route SHALL NOT draw a focus rectangle around it, and while a
route popup is open the hover tooltips SHALL be hidden.

#### Scenario: Click a route

- **WHEN** the user clicks a route
- **THEN** its popup opens, only the route is highlighted and no tooltip is shown

### Requirement: Week slider positions

The week slider's first position SHALL mean all dates, and position k SHALL mean the
seven days starting `k - 1` weeks after the first start date, with `aria-valuetext`
`all dates` or `week of Thu 19 Nov`. The slider's label SHALL read `Week`.

#### Scenario: Back to the start

- **WHEN** the user moves the week slider and then drags it back to the first position
- **THEN** the start date range is the full range again and the slider announces
  `all dates`

### Requirement: Chain mode

The map page SHALL have a `Chains` toolbar button, with `aria-pressed`, that switches
between trips and chains. A chain is a sequence of 2 or 3 rally legs, each booked as its
own trip, found from the offers on the page without any request. Switching modes SHALL
keep every filter selection and the view (map or list). The toolbar count SHALL read
`N chains`, or `Showing 200 of N chains` when there are more than 200. The `Chains`
button SHALL have a title that says what chains are.

#### Scenario: Entering chain mode

- **WHEN** the user presses `Chains` on a page with offers
- **THEN** the button is pressed and the toolbar reads `N chains`

#### Scenario: Back to trips

- **WHEN** the user presses `Chains` again
- **THEN** the map and list show trips as before

#### Scenario: No chain exists

- **WHEN** no two offers can be joined under the current settings
- **THEN** the page shows the empty state `No chains match` with a reset button, and
  it suggests only the settings that are not already at their maximum

### Requirement: Chain settings

In chain mode the toolbar SHALL show three more controls: legs (`2`, `2 or 3`;
default `2`), rest days (none, up to 1, up to 2; default none) and connection (same
station, within 50 km, within 100 km; default same station). They SHALL be hidden in
trip mode.

#### Scenario: Defaults

- **WHEN** the user enters chain mode
- **THEN** the controls read `2`, `none` and `same station`

#### Scenario: Three legs

- **WHEN** the user selects `2 or 3`
- **THEN** the chains of 3 legs are added to the chains of 2 legs

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

### Requirement: Chain rest days

Leg N+1 SHALL start on the day leg N ends or up to the selected number of rest days
later, never earlier. A hand-over at the same station SHALL read `Same-day hand-over in <station>` or `N rest days in <station>`.

#### Scenario: No rest days

- **WHEN** rest days are none
- **THEN** every second leg starts on the day the first ends

#### Scenario: Rest days allowed

- **WHEN** the user allows up to 2 rest days
- **THEN** every chain from before is still found and chains with 1 or 2 rest days are
  added, each showing its rest days

### Requirement: Chain connections

Leg N+1 SHALL start at the station where leg N ended or, with a connection selected, at
another station within that many km of it, measured as the straight line × 1.3 rounded
to 10 km and shown with `~`. A station SHALL NOT be a pick-up twice in one chain. A
hand-over to another station SHALL read `Same day` or `N rest days`, then its distance
and both stations.

#### Scenario: Strictest settings

- **WHEN** rest days are none and the connection is the same station
- **THEN** every chain's legs hand over at the same station on the same day

#### Scenario: Connection allowed

- **WHEN** the user allows a connection of 50 km
- **THEN** every chain from before is still found and chains with a connection of up to
  50 km are added

#### Scenario: Connection shown

- **WHEN** a chain's second leg starts 40 km from where the first ended
- **THEN** its hand-over reads like `Same day · ~40 km from A to B`

### Requirement: Chain filters

In chain mode the start date filter and the week slider SHALL limit the first pick-up
day, the distance filter SHALL limit the distance of every leg, the pick-up filters SHALL
apply to where the chain starts and the return filters to where it ends, and their
groups SHALL be labelled `Distance per leg`, `Chain starts at` and `Chain ends at`. The
dropdown options SHALL count chains. The stations in between SHALL NOT be filtered.

#### Scenario: Pick-up station

- **WHEN** the user picks a pick-up station in chain mode
- **THEN** every chain listed starts at it and the dropdowns count chains

#### Scenario: Week

- **WHEN** the user moves the week slider
- **THEN** every chain listed starts in that week

### Requirement: Chain list rows

In chain mode a row SHALL show the first pick-up date and the last return date as
`Mon 14 Dec` with the ISO date in the cell's `title`, the total days with the rest days
under them when there are any, the km driven (the legs only, with `~` when any is
estimated) and a `Map` button named `Show chain <legs> on the map`. The table SHALL have
a caption that says each leg is booked on its own. Every value from the API SHALL be escaped before
it is inserted as HTML.

#### Scenario: Row

- **WHEN** a chain starts on 14 December and ends on 28 December
- **THEN** its row shows `Mon 14 Dec`, `Mon 28 Dec`, `14` days and its km driven

### Requirement: Chain legs in the list

Each chain row SHALL have one numbered entry per leg with its stations as `Name, CC`,
dates, nights, distance and a `Book` link that opens in a new tab, named after the leg,
and the hand-over before every leg after the first. The popup of a chain SHALL use the
same entries.

#### Scenario: Booking each leg

- **WHEN** the user opens the `Book` links of a two-leg chain
- **THEN** each opens the booking page of that leg's stations and dates

### Requirement: Chain list size

The chain list SHALL show the first 200 chains in the sort order, and the toolbar SHALL
show how many chains there are in all, as `Showing 200 of 23,267 chains`.

#### Scenario: More than 200 chains

- **WHEN** there are 2075 chains
- **THEN** the toolbar reads `Showing 200 of 2,075 chains`, the list has 200 rows and a
  note says how many are shown

### Requirement: Chain list sorting

Chains SHALL be sorted by total days, then by km driven, by default, and SHALL be
re-sortable by start, end, total days and km driven from the column headers, with
`aria-sort` on the sorted header and focus kept on it. The map SHALL draw the chains the
list shows.

#### Scenario: Sort by km driven

- **WHEN** the user clicks the km driven header in chain mode
- **THEN** the rows are ordered by km driven, a second click reverses the order, and
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

The `Map` button of a chain SHALL draw that chain over the others, which are dimmed, with
its legs in the highlight colour and numbered, its stations and its connections, and open
a popup above it that lists the legs with a booking link each, the hand-overs, the rest
days and the km driven, with the whole chain fitted below the popup. With the keyboard,
focus SHALL move to the popup's first booking link.

#### Scenario: Chain from the list

- **WHEN** the user presses the `Map` button of a chain
- **THEN** the page shows the map fitted to the chain with its legs highlighted and a
  popup with a `Book` link for each leg

#### Scenario: Keyboard

- **WHEN** a keyboard user activates the `Map` button of a chain
- **THEN** focus is on the first `Book` link of its popup

### Requirement: Chain selection lifetime

The chain opened from the list SHALL stay drawn until Escape, a click on the map or a
change of the filters or settings. Escape SHALL also close its popup and return to the
list.

#### Scenario: Closing the popup

- **WHEN** the user closes the popup with its close button
- **THEN** the chain stays highlighted until the user presses Escape or clicks the map

### Requirement: Chain legend

In chain mode the legend SHALL read `leg of 1 chain`, `10 or more chains`, `connection to the next pick-up (train, bus)`, `selected chain` and `station: click for chains starting here`, and it
SHALL keep the estimate entry when a connection is allowed or a distance is estimated.

#### Scenario: Legend in chain mode

- **WHEN** the user opens the legend in chain mode
- **THEN** it has an entry with a dotted line labelled `connection to the next pick-up (train, bus)`
