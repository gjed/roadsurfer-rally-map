# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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

### Requirement: Station markers

The map SHALL draw one marker per station that has a trip under the active filters,
above the route lines, with a dark outline that contrasts with the basemap. Clicking a
marker SHALL set the pick-up filter to that station, or clear it when that station is
already selected, and SHALL NOT open any route popup; the selected station SHALL be
filled and larger. The tooltip SHALL show `Name, CC`, the departures and arrivals among
the trips that pass the filters, and what a click does. A station with no departures
SHALL ignore the click.

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

### Requirement: Map legend

The map SHALL show a legend that the user can collapse, with a one-trip line, a
five-or-more-trips line at their drawn weights and opacities, the highlighted route
and a station marker, worded `1 trip on this route`, `5 or more trips`,
`selected route` and `station: click for trips from here`. It SHALL start open at
desktop widths and collapsed below 700 px.

#### Scenario: Reading the map

- **WHEN** the page is opened 1280 px wide
- **THEN** the legend shows the four samples with those labels and no explanation of
  the arc direction

### Requirement: Trip list columns

Each list row SHALL show the start date, end date, pick-up and return station as
`Name, CC`, estimated road distance, the price when the page has prices, a `Map`
button and a `Book` link that opens in a new tab. Below 700 px the dates SHALL show
as `Thu 19 Nov`, with the ISO date in the cell's `title`. Every value from the API
SHALL be escaped before it is inserted as HTML.

#### Scenario: Booking from the list

- **WHEN** the user clicks the booking link of a row
- **THEN** the trip's booking URL opens in a new tab and the view does not change

#### Scenario: Dates on a phone

- **WHEN** the list is shown 375 px wide
- **THEN** dates read `Thu 19 Nov`, and the cell's title is `2026-11-19`

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
