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

### Requirement: Vendored Leaflet

The map template SHALL load Leaflet's JavaScript and CSS from `vendor/leaflet/` by
relative path. The repository SHALL ship an unmodified, pinned Leaflet 1.x release
there (`leaflet.js`, `leaflet.css`, `images/` and `LICENSE`) and record its version
in `vendor/leaflet/VERSION`. The page SHALL make no request to `unpkg.com`. Map tiles
load from Esri's World Light Gray Canvas in the light theme and World Dark Gray Canvas
in the dark theme, base and reference labels, up to zoom 16.

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
close. Below 700 px the chips SHALL scroll on one row after a `Filters` chip.

#### Scenario: Phone width

- **WHEN** the page is opened 375 px wide
- **THEN** the app bar shows the logo, the title and the views on one row, the chips
  scroll sideways on one row after the `Filters` chip, and the map fills the rest of
  the screen under the results sheet

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
and a station marker, worded `1 trip on a route`, `5 or more trips`, `Selected` and
`Station — click to filter pick-ups`. While the page has an estimated distance, it SHALL
add a fifth entry, `~ Estimated distance, not routed`. It SHALL start open at desktop
widths and SHALL be hidden below 700 px.

#### Scenario: Reading the map

- **WHEN** the page is opened 1280 px wide with routed distances only
- **THEN** the legend shows the four samples with those labels and no explanation of
  the arc direction

#### Scenario: Estimates on the page

- **WHEN** the page is opened with at least one estimated distance
- **THEN** the legend also shows `~ Estimated distance, not routed`

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

A route SHALL be drawn in the selected colour (`#C2410C` in light, `#FF8A4C` in dark) on a
halo in the page's background colour, above the other lines, which drop to a low opacity, while the pointer or keyboard focus is on its card, while
the pointer is over its line, and while it is open. Pointing at a line SHALL also mark
its card and scroll it into view. The highlight SHALL go when none of these holds. A
line SHALL NOT stay highlighted after a tap on a touch screen unless the tap opened it.

#### Scenario: Popup open

- **WHEN** the user opens a route, by clicking the line or its card
- **THEN** the line is in the selected colour on a halo, drawn on top of the other lines,
  even after the pointer leaves it

#### Scenario: Popup closed

- **WHEN** the route is closed, with `← All routes`, Escape or Back
- **THEN** the line has its normal colour and opacity

#### Scenario: Tap on a touch screen

- **WHEN** the user taps a route and then taps another route
- **THEN** only the route that is open is highlighted

### Requirement: Route line weight

A route line SHALL have the weight `min(1.5 + trips * .8, 5)` px and the opacity
`min(floor + (trips - 1) * .1, ceiling)`, the floor and ceiling being the theme's
`--route-op-min` and `--route-op-max` (.8 and .95 in light, .85 and .95 in dark), so that
busy routes stand out and a single trip is still 3:1 against the land of the tiles.

#### Scenario: Single and busy routes

- **WHEN** the page draws a route with 1 trip and a route with 5 or more trips
- **THEN** the first line is 2.3 px wide at the floor, the second 5 px wide at the ceiling

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
chain details SHALL have a tap area of at least 24 by 24 CSS px. Below 700 px the
`Book` links of the route and chain details and of the chain cards SHALL be at least
44 px tall.

#### Scenario: Phone

- **WHEN** the page is used with a coarse pointer
- **THEN** each booking link measures at least 24 by 24 px

#### Scenario: Route detail on a phone

- **WHEN** the user opens a route at 390 px
- **THEN** every window's `Book` link is at least 44 px tall

### Requirement: Trip list layout

On a wide screen the trips table SHALL fill the page up to 1320 px, inside a box that
scrolls sideways when it must, with the distance header right-aligned over the
distances and a sticky header with a visible bottom edge. Below 700 px each row SHALL
be a card that fits the screen without horizontal scrolling, with its dates in bold,
its distance and nights, its stations and its `Map` and `Book` buttons, under the
count, the mode switch, `Sort` and `Group`.

#### Scenario: Desktop list

- **WHEN** the Trips view is shown at 1280 px
- **THEN** the distance header sits over the right edge of the distances and the header
  keeps a bottom line while scrolling

#### Scenario: Phone list

- **WHEN** the Trips view is shown 375 px wide
- **THEN** each trip is a card with its dates, distance, stations, `Map` button and
  `Book` link, and the list does not scroll sideways

#### Scenario: Phone card buttons

- **WHEN** the Trips view is shown 390 px wide
- **THEN** each card's `Map` button and `Book` link are 44 px tall and `Book` is twice
  as wide as `Map`

#### Scenario: Phone sort

- **WHEN** the user picks `Longest drive` in `Sort` at 390 px
- **THEN** the cards are ordered by distance, longest first, and focus stays on `Sort`

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
filter differs from its reset value, the favourites filter included. Pressing it SHALL
clear every filter and the chain options, and focus SHALL move to the first chip. It
SHALL NOT remove any star. Below 700 px the filter sheet's `Reset (n)` SHALL take its
place.

#### Scenario: Nothing filtered

- **WHEN** the page is opened and no filter has been changed
- **THEN** there is no `Clear all`

#### Scenario: Filter active

- **WHEN** the user picks a pick-up station
- **THEN** `Clear all` is shown next to the counts, and pressing it clears every
  filter and hides it

#### Scenario: Reset on a phone

- **WHEN** a filter is active at 375 px and the user presses `Reset (1)` and then
  `Show N trips` in the filter sheet
- **THEN** every filter is cleared and the `Filters` chip reads `Filters`

#### Scenario: Stars survive

- **WHEN** the favourites filter is on, one route is starred, and the user presses
  `Clear all`
- **THEN** the filter is off and the route is still starred

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
`aria-pressed`. A chain is a sequence of 2 or 3 rally legs, each
booked as its own trip, found from the offers on the page without any request.
Switching modes SHALL keep every filter and the view and close an open route or chain.
The count SHALL read `N chains from M trips`, M being the offers the chains are built
from. `Chains` SHALL have a title that says what chains are.

#### Scenario: Entering chain mode

- **WHEN** the user presses `Chains` on a page with offers
- **THEN** the button is pressed and the filter bar reads `N chains from M trips`

#### Scenario: Back to trips

- **WHEN** the user presses `Single rallies`
- **THEN** the map and lists show trips as before

#### Scenario: No chain exists

- **WHEN** no two offers can be joined under the current settings
- **THEN** the page shows the empty state `No chains match` with a reset button, and
  it suggests only the settings that are not already at their maximum

### Requirement: Chain settings

In chain mode a `Chain options` chip SHALL open a panel with: legs (`2`, `3`, `2 or 3`;
default `2`), a `Same day` switch (on), 0 to 7 rest days (0), a `Next pick-up within`
slider from the same station to ~250 km in steps of 25 km (same station), min days, max
days and max km (empty: any) and a `Round trip` switch (off). Every control SHALL update
the results; typed numbers after 250 ms and the slider after 150 ms, with `Finding chains…` in the count meanwhile.

#### Scenario: Defaults

- **WHEN** the user enters chain mode
- **THEN** the controls read `2`, `Same day` on, `0`, `same station`, empty, empty,
  empty and `Round trip` off, and the chip is not marked as changed

#### Scenario: Three legs

- **WHEN** the user selects `2 or 3`
- **THEN** the chains of 3 legs are added to the chains of 2 legs

#### Scenario: Exactly three legs

- **WHEN** the user selects `3`
- **THEN** every chain listed has 3 legs

#### Scenario: Moving the slider

- **WHEN** the user drags the next pick-up slider to `~150 km`
- **THEN** the count reads `Finding chains…` until the slider rests, then the chains
  with a connection of up to 150 km

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

The panel SHALL group the options under `Legs`, `Between legs` and `Whole trip`. The
rest days stepper SHALL read `Rest days, up to N` while `Same day` is on and `Rest days, 1 to N` while it is off. Legs buttons SHALL carry `aria-pressed`, switches
`role="switch"`. The panel SHALL end with `Reset` (the chain options only) and `Show N chains`, which counts live and closes it. The chip SHALL be marked exactly while an
option is not at its default.

#### Scenario: Unchecked

- **WHEN** the user turns `Same day` off and sets 3 rest days
- **THEN** the stepper reads `Rest days, 1 to` 3 and its `−` stops at 1

#### Scenario: Tab order

- **WHEN** a keyboard user opens the `Chain options` panel
- **THEN** focus is on `Legs`, the first control, and Tab stays inside the panel

#### Scenario: Panel reset

- **WHEN** the user changes the legs and presses the panel's `Reset`
- **THEN** every chain option is back to its default and the other filters are kept

#### Scenario: Show the chains

- **WHEN** the user presses `Show 2,192 chains`
- **THEN** the panel closes and focus returns to the `Chain options` chip

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
1.3 rounded to 10 km and shown with `~`; the distance, and the URL's `hop`, SHALL be a
multiple of 25 km up to 250. A station SHALL NOT be a pick-up twice in a chain. A hand-over to another station SHALL read `Hop ~N km <A> → <B> on your own`, then `same day` or `N rest days`, and be drawn with a dotted rule.

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

#### Scenario: A step between the old values

- **WHEN** the user opens a link with `hop=75`
- **THEN** the slider reads `~75 km` and chains with a connection of up to 75 km are
  listed; `hop=80` is ignored

### Requirement: Chain filters

In chain mode the dates SHALL limit the first pick-up day, the distance filter SHALL limit the distance of every leg, the pick-up filters SHALL
apply to where the chain starts and the return filters to where it ends. Their chips
SHALL read `Dates`, `Distance`, `Chain starts at` and `Return`, with the accessible names
`First pick-up date`, `Distance per leg`, `Chain starts at` and `Chain ends at`. The
dropdown options SHALL count chains. The stations in between SHALL NOT be filtered.

#### Scenario: Pick-up station

- **WHEN** the user picks a pick-up station in chain mode
- **THEN** every chain listed starts at it and the dropdowns count chains

#### Scenario: Week

- **WHEN** the user moves the week slider
- **THEN** every chain listed starts in that week

#### Scenario: One row at 1440 px

- **WHEN** the page is in chain mode at 1440 px with no leg picked
- **THEN** the chips, `Chain options` and the count share one row

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

The chain lists SHALL show the first 200 chains in the sort order and say so, and the
filter bar SHALL show how many chains there are in all, as
`23,267 chains from 781 trips`.

#### Scenario: More than 200 chains

- **WHEN** there are 2075 chains
- **THEN** the filter bar reads `2,075 chains from M trips`, the list has 200 cards
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
with the weight of the number of chains that use it and the opacity
`min(floor + (chains - 1) * .02, ceiling)` (`--chain-op-min`, `--route-op-max`), and each
connection to another station as a dotted straight line in a second colour on a casing. Station
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

In chain mode the legend SHALL read `Leg of 1 chain`, `10 or more chains`, `Selected`,
`Hop to the next pick-up`, `Click a leg or hop to list its chains` and
`Station — click to filter chain starts`, and it SHALL keep the estimate entry when a
connection is allowed or a distance is estimated.

#### Scenario: Legend in chain mode

- **WHEN** the user opens the legend in chain mode
- **THEN** it has an entry with a dotted line labelled `Hop to the next pick-up`

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

Below 700 px the `Chain options` panel SHALL be a sheet from the bottom of the screen,
over a dark backdrop, with `Chains: 2–3 rallies booked back to back. Set how they may connect, then browse them on the map.` above it, a title, a close button, 44 px
controls and a footer in view. Turning `Chains` on SHALL open it, with
`aria-expanded` true on its chip. `Show N chains`, the close button, Escape and a tap
above the sheet SHALL close it; only `Show N chains` SHALL keep its changes.

#### Scenario: Chains on at 375 px

- **WHEN** the user presses `Chains` on a 375 px wide screen
- **THEN** the chain options sheet is open and its chip is expanded

#### Scenario: Chains off

- **WHEN** the user presses `Single rallies`
- **THEN** the chain options sheet closes and its chip is hidden

#### Scenario: Back to the map

- **WHEN** the user presses `Show N chains` in the sheet
- **THEN** the sheet closes and the map and its lines can be tapped

#### Scenario: Closed without Show

- **WHEN** the user picks `3` legs in the sheet and closes it with its close button
- **THEN** the legs are `2` again and the chain list is the one from before

#### Scenario: Explanation

- **WHEN** the user presses `Chains` at 390 px
- **THEN** the page behind the sheet is dark and the explanation reads above the sheet

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

### Requirement: Results sheet on phones

Below 700 px the map view SHALL fill the screen with the map and show the route or
chain list in a sheet from the bottom with three heights: peek (at most 330 px and half
the view), half (about 62 % of the view) and full. The sheet header SHALL show the count
and the `Rallies | Chains` switch. The map above the sheet SHALL stay usable, and its
attribution and fits SHALL stay above the sheet. With reduced motion the sheet SHALL
not animate.

#### Scenario: First load on a phone

- **WHEN** the page is opened 390 × 844 px
- **THEN** the sheet is 330 px tall with the route count, the `Rallies | Chains` switch
  and the first cards, every station is visible above it and the page does not scroll
  sideways

### Requirement: Results sheet grip

The sheet's grip SHALL be a button named `Expand results` (`Collapse results` at full)
with `aria-expanded`. A tap, Enter or Space SHALL move the sheet to the next height, the
arrow keys, Home and End SHALL move it between the heights, and a drag SHALL end at the
nearest height.

#### Scenario: Grip

- **WHEN** the user taps the grip three times
- **THEN** the sheet goes to half, to full with the grip named `Collapse results`, and
  back to peek

#### Scenario: Grip from the keyboard

- **WHEN** a keyboard user focuses the grip and presses the up arrow, End and Home
- **THEN** the sheet goes to half, full and peek

### Requirement: Route and chain on phones

Below 700 px opening a route or a chain SHALL hide the app bar and the filter bar, put
the sheet at half with the route or chain detail, fit the map in the space above the
sheet, dim the other routes and the stations, and show a floating back button and the
route or chain title over the map. Going back, with that button, the detail's back
button, Escape or the browser's Back, SHALL bring the bars back, return the sheet to the
height it had and the focus to the card that opened it.

#### Scenario: Open a route

- **WHEN** the user taps a route card at peek
- **THEN** the sheet is at half with the route's windows and `Book` links, the map shows
  the route above it and a floating bar reads `← Vienna → Berlin-Schönefeld`

#### Scenario: Back

- **WHEN** the user taps the floating back button
- **THEN** the route closes, the sheet returns to peek and focus is on the route's card

#### Scenario: Full-screen map

- **WHEN** a route is open at 390 × 844 px
- **THEN** no app bar or filter bar is shown and the map reaches the top of the screen

### Requirement: Filter sheet on phones

Below 700 px a `Filters` chip SHALL open a full-height sheet (`role="dialog"`) with the
date, distance, pick-up and return filters and, in chain mode, the chain options, with
16 px text and inputs at least 44 px tall. Its footer SHALL have `Reset (n)`, which
clears every filter, and `Show N trips` (`Show N chains` in chain mode) with the live
count.

#### Scenario: Sheet content

- **WHEN** the user presses `Filters` at 390 px in chain mode
- **THEN** a full-height sheet shows the chain options and the four filters, and its
  footer reads `Reset` and `Show N chains`

### Requirement: Filter sheet applies on Show

Changes in the phone filter sheet SHALL apply when `Show` is pressed. The close button,
Escape and a tap outside SHALL close it and restore the filters it opened with. Focus
SHALL return to the `Filters` chip.

#### Scenario: Show applies

- **WHEN** the user sets the maximum distance to 1000 km in the sheet and presses
  `Show N trips`
- **THEN** the sheet closes, the map and list show trips of up to 1000 km and the chip
  reads `Filters · 1`

#### Scenario: Close discards

- **WHEN** the user sets the maximum distance in the sheet and closes it with its close
  button, Escape or a tap outside
- **THEN** no filter is set and the chip reads `Filters`

### Requirement: Filters chip count

Below 700 px the `Filters` chip SHALL read `Filters · n`, where `n` counts the active
filters, the favourites filter, the chain options that differ from their defaults and
the leg filter, and `Filters` when there is none. The trip, route and chain counts SHALL
then show in the results sheet and the Trips heading instead of the filter bar.

#### Scenario: Count in chain mode

- **WHEN** the user turns `Chains` on, picks `3` legs and opens a leg filter
- **THEN** the chip reads `Filters · 2`

#### Scenario: Count with favourites

- **WHEN** the user turns the favourites filter on and picks a pick-up country at 375 px
- **THEN** the chip reads `Filters · 2`

### Requirement: Phone app bar

Below 700 px the app bar SHALL be one row with the logo, `Rally map` and the views; the
`Rallies | Chains` switch SHALL be in the results sheet header and the Trips header.

#### Scenario: One row

- **WHEN** the page is opened 390 px wide
- **THEN** the app bar is one row with the logo, `Rally map`, `Map` and `Trips`, and the
  results sheet header has `Rallies` and `Chains`

### Requirement: Map controls on phones

Below 700 px the map SHALL show a 44 by 44 px `Fit` button and no zoom buttons; the map
SHALL still zoom with a pinch.

#### Scenario: Phone map

- **WHEN** the page is opened at 390 px
- **THEN** the map has a 44 px `Fit all routes` button, no `+` or `−` buttons and no
  legend

### Requirement: Date quick picks

The date panel SHALL offer `Any`, `This week` and `Next week`, each with `aria-pressed`
true exactly while the dates equal its range: all dates, today to Sunday, and next
Monday to Sunday.

#### Scenario: Next week

- **WHEN** the user presses `Next week`
- **THEN** the dates are next Monday to Sunday and only `Next week` is pressed

#### Scenario: Any

- **WHEN** the user then presses `Any`
- **THEN** every date is allowed again and only `Any` is pressed

### Requirement: Map link focus

Opening the page, or going Back, to a `#map` address SHALL NOT move focus to the map.

#### Scenario: Escape from a route

- **WHEN** the user opens a route from the list and presses Escape
- **THEN** focus is on the route's card and the map shows no focus ring

### Requirement: Colour themes

The map page SHALL have a light and a dark theme. Every colour of the page SHALL come
from a CSS custom property defined for `:root[data-theme=light]` and
`:root[data-theme=dark]`: no component rule, Leaflet path option or inline SVG SHALL
hold a colour value of its own. The map's colours SHALL be read from the properties
with `getComputedStyle`.

#### Scenario: One set of properties per theme

- **WHEN** the rendered page is searched for hex colours outside the property
  definitions and the favicon
- **THEN** there are none, and `data-theme` on `<html>` is `light` or `dark`

### Requirement: Native controls and dark borders

The page SHALL set `color-scheme` to the theme and SHALL carry
`<meta name="color-scheme" content="light dark">`, so native inputs, date pickers and
scrollbars follow the theme. In the dark theme a shadow SHALL be a 1 px border, or
nothing where the panel has one.

#### Scenario: Native controls

- **WHEN** the dark theme is on
- **THEN** `color-scheme` is `dark`, and the date inputs and scrollbars are drawn dark

### Requirement: Theme choice

The page SHALL offer the themes `System`, `Light` and `Dark`, `System` being the
default. A choice SHALL be saved in `localStorage['rally-map:theme']` and SHALL NOT be
written to the URL. A storage that is unavailable, or a stored value that is not one of
the three, SHALL mean `System` and SHALL NOT raise an error.

#### Scenario: Storage unavailable

- **WHEN** `localStorage` throws
- **THEN** the page follows the device setting and a choice still applies until reload

### Requirement: System theme

`System` SHALL follow `prefers-color-scheme` and SHALL change when it does, without a
reload.

#### Scenario: System changes

- **WHEN** the choice is `System` and the device switches from light to dark
- **THEN** the page and the map turn dark at once; with `Light` chosen they do not

### Requirement: Theme before the first paint

A script in `<head>` SHALL set `data-theme` before the first paint, from the saved
choice and `prefers-color-scheme`, so a dark theme never shows the light page first.

#### Scenario: Saved dark

- **WHEN** `Dark` was chosen and the page is reloaded
- **THEN** `data-theme` is `dark` before the first paint and only dark tiles are
  requested

### Requirement: Display button

The app bar SHALL end with a `Display` button showing the current theme as an icon
(a half-filled circle for `System`, a sun, a moon), with the accessible name
`Display settings: theme <choice>` (with the language in it once the page has several, see
"Display button language"). Below 700 px it SHALL show `⋯`, 44 by 44 px, in
place of the icon.

#### Scenario: Display button on a phone

- **WHEN** the page is opened 390 px wide
- **THEN** the app bar ends with a `⋯` button named `Display settings: theme system`

### Requirement: Display panel

The `Display` button SHALL open a dialog labelled `Display settings` with a `Theme`
control of three buttons with `aria-pressed`, built from one section per setting.
Choosing a theme SHALL apply it at once and leave the panel open. Escape SHALL close it
and return focus to the button; Tab SHALL stay inside while it is open. Below 700 px it
SHALL be a sheet from the bottom over a darkened page.

#### Scenario: Choose Dark

- **WHEN** the user opens the Display panel and presses `Dark`
- **THEN** the page and the map turn dark, `Dark` is pressed, the button reads
  `Display settings: theme dark` and shows a moon

#### Scenario: Close with Escape

- **WHEN** the Display panel is open and the user presses Escape
- **THEN** it closes and the Display button has focus

### Requirement: Map tiles follow the theme

The base and reference tile layers SHALL switch with the theme, between the Light Gray
and the Dark Gray canvas, in place. The reference layer SHALL stay in the pane above the
routes, and the attribution SHALL keep the Esri credit, the OSRM and OpenStreetMap
credit and the release tag.

#### Scenario: Tiles swap

- **WHEN** the theme changes from light to dark
- **THEN** the map shows the Dark Gray base and reference tiles and keeps its centre and
  zoom

### Requirement: Theme change keeps the page

A theme change SHALL keep the map view, the open route or chain, the filters, the sort
and the scroll positions. The lines, rings and badges on the map SHALL change to the
new theme's colours without being redrawn.

#### Scenario: Theme change with a route open

- **WHEN** a route is open on the map and the theme changes
- **THEN** the same route stays open and is drawn in the new theme's selected colour

#### Scenario: Theme change on the Trips view

- **WHEN** the Trips view is sorted, grouped and scrolled, and the theme changes
- **THEN** the sort, the grouping, the filters, the URL and the scroll position are the
  same

### Requirement: Theme contrast

In both themes text SHALL have a contrast of at least 4.5:1 with its background, and the
route, selected, hop and station colours of a theme at least 3:1 with the colours of the
tiles shown in that theme.

#### Scenario: Route colours on the tiles

- **WHEN** the route, selected, hop and station colours are measured against the
  dominant colours of the tile set of their theme
- **THEN** each is at least 3:1

#### Scenario: Text

- **WHEN** the visible text of the map, the Trips view, the panels and the sheets is
  measured in each theme
- **THEN** each text is at least 4.5:1 against its background

#### Scenario: Accepted exceptions

- **WHEN** a one-trip line is measured on the sea of the Light Gray tiles, or the border
  of a chip or pill (`--field`) on its surface
- **THEN** they are 2.6:1 and 1.5:1 (light) or 1.7:1 (dark), below 3:1, and are accepted:
  the light route colour is 3.4:1 on that sea even at full opacity, and a chip or pill is
  named by its text

### Requirement: Map controls in the theme

The zoom and fit controls, the legend, the attribution and the tooltips SHALL use the
theme's surface, text and border colours, as the rest of the page does.

#### Scenario: Dark controls

- **WHEN** the dark theme is on
- **THEN** the zoom and fit buttons, the legend and the tooltips have the dark surface
  and light text, and the attribution is readable over the dark tiles

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

### Requirement: Feed table in the page

With `--map`, the scanner SHALL also replace `/*FEEDS*/null` in the template with the
JSON list `[name, cc, slug]` of the pick-up stations that `--feeds` writes a feed for,
with the slugs of their files, computed by the same code from the same stations, whether
or not `--feeds` is given. It SHALL keep `/*DATA*/[]` and `/*SCAN*/null` as they are.

#### Scenario: Feed table matches the files

- **WHEN** the user renders a data file with `--map` and `--feeds`
- **THEN** every `[name, cc, slug]` in the page has the file `from-<slug>.xml` in the
  feeds directory

#### Scenario: No stations

- **WHEN** the user renders a data file with no offers and no station list
- **THEN** the page embeds an empty list

### Requirement: Favourite buttons

A favourite button SHALL be a `<button>` with `aria-pressed` and an accessible name from
the message catalog that names the item (`Favourite: Munich, DE to Bordeaux, FR`) and does
not change with its state. A button SHALL NOT be inside another button.

#### Scenario: Names

- **WHEN** a favourite button is read by a screen reader
- **THEN** it is announced as a button, with a name such as `Favourite: Munich, DE to Bordeaux, FR` and its pressed state

### Requirement: Favourite button look

The icon of a favourite button SHALL be an inline SVG with `aria-hidden`, an outline star
that is filled when pressed, so the shape and not only the colour shows the state. The
button SHALL come in two forms: the icon alone (36 px square, 44 px below 700 px or for a
coarse pointer) and the icon with the visible word `Favourite` (32 px high, 44 px below
700 px). Its colour SHALL come from the `--fav` token.

#### Scenario: Colour is not the only sign

- **WHEN** a route is a favourite
- **THEN** its star is filled, and an unpressed star is an outline

### Requirement: Favourite places

The page SHALL offer a favourite button on every route card (beside the card, at its
bottom right) and on the route detail (the word form, in a row with `Back`), on every
chain card and on the open chain, on every Trips row (in a first column; on a phone
before the `Map` and `Book` buttons) and on every Trips chain card (beside its title).

#### Scenario: Favourite a route from its card

- **WHEN** the user presses the star of a route card
- **THEN** the button is pressed and the route stays where it is on the map

#### Scenario: Favourite a route from its detail

- **WHEN** the user opens a route and presses `Favourite` beside `Back`
- **THEN** the route is a favourite and its card shows the star filled after Back

### Requirement: Favourite places for stations

For a pick-up station the page SHALL offer the word form in the heading of the lists
while the station is chosen and in the Pick-up panel under the station menu, but not on
the filter chips and not in the Return panel.

#### Scenario: Favourite a station

- **WHEN** the user picks the pick-up station `Munich` and presses `Favourite` in the
  heading `From Munich, DE`
- **THEN** the station is a favourite, and `Favourite` in the Pick-up panel is pressed too

#### Scenario: No station button on the chips

- **WHEN** a pick-up station is chosen
- **THEN** the Pick-up and Return chips have no favourite button

### Requirement: Card hover with a favourite button

A route card and its favourite button SHALL highlight the route together: the pointer on
the button SHALL NOT end the highlight on the map or the hover of the card.

#### Scenario: Pointer on the star

- **WHEN** the user points at the star beside a route card
- **THEN** the route stays highlighted on the map and the card keeps its hover style

### Requirement: Favouriting keeps the page

Pressing a favourite button SHALL NOT change the filters, the open route or chain, the
sort, the scroll positions, the map view or the keyboard focus. When the list is drawn
again, the focus SHALL return to the same button, or when the item is gone (un-starred
under the favourites filter) to the star of the next item or else the list heading.

#### Scenario: Star in a scrolled list

- **WHEN** the user scrolls the route list, filters by a country and presses a star
- **THEN** the list is where it was, the filter is still on and the star keeps focus

#### Scenario: Last item removed

- **WHEN** the favourites filter is on and the user un-stars the only listed route
- **THEN** focus is on the list heading

### Requirement: Favourites storage

The page SHALL save the favourites in `localStorage['rally-map:fav']` as JSON with a
version number `v`, one entry per route, station and chain, and SHALL NOT put them in the
URL. A route SHALL be keyed by `from.name>to.name`, a station (a pick-up station) by
`Name, CC` and a chain by the route keys of its legs, in order, joined by `|`.

#### Scenario: Survives a reload

- **WHEN** the user stars a route and reloads the page
- **THEN** the route is still a favourite

#### Scenario: Not in the URL

- **WHEN** the user stars a route
- **THEN** the URL hash is unchanged

#### Scenario: Other keys

- **WHEN** a station is a favourite in a scan and the next scan has it under another name
- **THEN** the favourite no longer applies to that station

#### Scenario: Two tabs

- **WHEN** the user stars a route in one tab and then another route in a second tab that was already open
- **THEN** both routes are favourites in both tabs

### Requirement: Favourites storage failures

Reading and writing the storage SHALL be guarded, so that a storage that throws, or a
value that is not valid, gives no favourites and no error; the favourites then work for
the visit only. A page SHALL NOT write when the stored version is not one it knows.

#### Scenario: Storage that throws

- **WHEN** `localStorage` throws on every access
- **THEN** the page opens without an error, and a star can be pressed and unpressed for
  the rest of the visit

#### Scenario: Unknown version

- **WHEN** the stored value has a `v` the page does not know and the user presses a star
- **THEN** the stored value is left as it was

### Requirement: Favourites filter

The filter bar SHALL have a `Favourites` chip, right after the Return chip, that toggles
with `aria-pressed`: a star, the word and, when windows are new, a count. It SHALL have no
chevron and no `×`. It SHALL be hidden while nothing is a favourite and the filter is
off. Its accessible name SHALL be `Favourites` followed by how many windows are new since
the last visit; the count SHALL be hidden from assistive technology.

#### Scenario: Chip hidden

- **WHEN** nothing is a favourite
- **THEN** the filter bar has no `Favourites` chip

### Requirement: Favourites filter scope

In Trips mode the favourites filter SHALL show only the trips whose route is a favourite
or that leave a favourite station, and in chain mode only favourite chains. A favourite
station applies to the routes that leave it, not to those that arrive.

#### Scenario: Only favourites

- **WHEN** one route is a favourite and the user presses `Favourites`
- **THEN** the map and the list show that route and the trips from the favourite stations

#### Scenario: Favourite chain

- **WHEN** the user turns `Chains` and `Favourites` on with one chain a favourite
- **THEN** only that chain is listed, as long as the chain options produce it

### Requirement: Favourites on phones

The phone filter sheet SHALL start with a `Favourites` section with an `Only favourites`
switch and the number of new windows. While nothing is a favourite the switch SHALL be
disabled and the section SHALL say how to add one. The chip row SHALL start with
`Filters` and then the `Favourites` chip.

#### Scenario: Hint without a favourite

- **WHEN** the filter sheet is opened at 390 px with no favourite
- **THEN** its first section has a disabled switch and a hint to star a route, station or chain

### Requirement: Favourites filter state

The favourites filter SHALL count in `Filters · n`, SHALL be cleared by `Clear all`
and `Reset`, SHALL be kept out of the URL and SHALL NOT be stored. With no favourite in
the current mode it SHALL say so, with a `Show all` button that turns the filter off.
With favourites that have no trips under the other filters it SHALL say
`None of your favourites have trips with these filters.`

#### Scenario: Nothing yet

- **WHEN** the filter is on and nothing is a favourite
- **THEN** the list says so and has `Show all`

#### Scenario: Favourites without trips

- **WHEN** a route is a favourite and the other filters leave none of its trips
- **THEN** the list says `None of your favourites have trips with these filters.`

#### Scenario: Reload

- **WHEN** the filter is on and the user reloads the page
- **THEN** the filter is off and the favourites are kept

### Requirement: Favourites first in the route list

While the favourites filter is off and a listed route is a favourite (or leaves a
favourite station), the route list SHALL move those routes to the top, under a header row
`Favourites` with a filled star and the route count, and the others under `All routes`;
each part SHALL keep the sort order. A route SHALL NOT be listed twice. With the filter
on, the list SHALL have no header rows.

#### Scenario: Favourites group

- **WHEN** one of three listed routes is a favourite
- **THEN** the list shows `Favourites` with that route, and `All routes` with the two others

#### Scenario: No favourite

- **WHEN** no listed route is a favourite
- **THEN** the list shows no header rows

### Requirement: Favourites first in Trips

While the favourites filter is off, the Trips table SHALL list the favourite trips first.
With no grouping they SHALL be a first group under a header row `Favourites` with their
count and a filled star, then the rest. Grouped by route or by pick-up, the groups that
have a favourite trip SHALL come first and their headers SHALL start with a filled star
and a visually hidden `Favourite`. The `Group by` choices SHALL stay none, route and
pick-up.

#### Scenario: No grouping

- **WHEN** one route is a favourite and the Trips view is not grouped
- **THEN** its trips are under `Favourites` and the other trips follow

#### Scenario: Grouped by route

- **WHEN** a route is a favourite and the trips are grouped by route
- **THEN** its group is first and its header starts with a filled star

### Requirement: Seen windows

For each favourite the page SHALL store the keys (`route|start|end`) of the windows it has
shown and the scan time (`scan.finished_at`, empty without one). The windows of an item
are those of its route, of the routes of its legs, or of the routes that leave its
station. Starring an item SHALL store its current windows, so nothing is new yet. Windows
that ended before today (UTC) SHALL be removed from the storage when the page loads. The
logic SHALL work without a scan time.

#### Scenario: Expired window

- **WHEN** the stored windows of a favourite route include one that ended yesterday
- **THEN** it is no longer in the storage after the page has loaded

#### Scenario: No scan time

- **WHEN** a page rendered from a data file without a `scan` object has a favourite route
  that later gains a window
- **THEN** the window is shown as new

### Requirement: New badges

A window that is not stored as seen SHALL carry a solid `New` badge in the colours of the
`--new-bg` and `--new-fg` tokens: first in the line under the dates of the route detail,
in the date cell of its Trips row (on a phone as a tab on the top border of the card),
and as a count (`2 new`) first in the line `Next … · windows until …` of its
route card.

#### Scenario: Window added to a favourite route

- **WHEN** a route is a favourite and a later scan adds a window to it
- **THEN** the route card shows `1 new`

### Requirement: New badge counts

A chain, which has fixed dates, SHALL carry no badge. The `Favourites` chip SHALL show
how many windows are new, each counted once. Badges SHALL NOT be announced as they appear.

#### Scenario: Count on the chip

- **WHEN** a later scan adds two windows to a favourite route and one to a favourite station
- **THEN** the `Favourites` chip shows `3`

#### Scenario: Removed window

- **WHEN** a later scan lacks a window of a favourite route
- **THEN** the page shows no error and no badge for it

### Requirement: Opening marks seen

Opening a route, a chain or a pick-up station (as the pick-up filter) SHALL store its
windows as seen in every favourite that has them, so a badge does not stay on a window
that was shown.

#### Scenario: Open the route

- **WHEN** a favourite route has a new window and the user opens the route
- **THEN** the window shows `New` in the detail, and after the user closes it the card
  and the `Favourites` chip show no new window

### Requirement: Station feed link

When the page has the feed table and a station that it names is chosen as the pick-up
station, the heading of the lists and the Pick-up panel SHALL show a link `RSS feed`
(never `Atom`) to `feeds/from-<slug>.xml` with the slug the table gives for the station.
The link SHALL be absent when the table has no entry for the station. The page SHALL NOT
compute a slug itself.

#### Scenario: Feed of a pick-up station

- **WHEN** the user picks the pick-up station `Munich`
- **THEN** the heading shows `RSS feed`, linking to `feeds/from-munich.xml`

#### Scenario: Station with a duplicate name

- **WHEN** two stations are both named `Neustadt`, in DE and AT, and the feeds are
  `from-neustadt-de.xml` and `from-neustadt-at.xml`
- **THEN** the link of each is the file of its own country

#### Scenario: Station without an entry

- **WHEN** the page has no feed table entry for the chosen station
- **THEN** no feed link is shown

### Requirement: Station feed link details

The feed link SHALL open in a new tab, SHALL have the type `application/atom+xml`, and
SHALL have a title and a description (`New rallies from <station>, for a feed reader app.`),
which the Pick-up panel shows as a line of text.

#### Scenario: Link attributes

- **WHEN** the feed link of `Munich` is shown
- **THEN** it has `target="_blank"`, a title and an `aria-describedby` that names the description

### Requirement: Station tooltip state

The tooltip of a station on the map SHALL start with a filled star (`★`) when the
station is a favourite. It SHALL hold no control and no feed text.

#### Scenario: Favourite station

- **WHEN** `Munich, DE` is a favourite and the user points at its marker
- **THEN** the tooltip starts with `★` and then `Munich, DE`

### Requirement: Favourites in every language

Every label, accessible name, title, empty state and badge of the favourites SHALL be in
the message catalog, in English, German, French, Spanish, Italian, Dutch and Portuguese.
The catalog test SHALL pass with them.

#### Scenario: German at 360 px

- **WHEN** the page is shown in German at 360 px wide with favourites on and a route a
  favourite
- **THEN** no label is cut, the `Map` and `Book` buttons of a trip card fit beside its
  star, and nothing overflows the viewport sideways
