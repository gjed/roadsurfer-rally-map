# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Release footer`
- TO: `### Requirement: Release tag attribution`

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Trip list columns

Each list row SHALL show the start date, end date, pick-up station and country,
return station and country, estimated road distance, the price when the page has
prices, a booking link that opens in a new tab and a `map` button. Below 700 px the
dates SHALL show as `MM-DD`, with the full date in the cell's `title` and still read
in full by assistive technology. Every value from the API SHALL be escaped before it
is inserted as HTML.

#### Scenario: Booking from the list

- **WHEN** the user clicks the booking link of a row
- **THEN** the trip's booking URL opens in a new tab and the view does not change

#### Scenario: Dates on a phone

- **WHEN** the list is shown 375 px wide
- **THEN** dates read `11-24` on one line, and the cell's title is `2026-11-24`

### Requirement: Trip list selection

Each list row SHALL have a `map` button whose accessible name is
`Show <from> to <to> on map`, and it SHALL be the only way to open a route from the
list: the row itself SHALL NOT be focusable, clickable or have a key handler.
Activating the button SHALL show that route on the map with its popup open. When the
button is activated with the keyboard, focus SHALL move to the popup's first booking
link. Escape in the popup SHALL close it and, for a popup opened from the list, return
to the list with focus on the button that opened it.

#### Scenario: Row selection

- **WHEN** the user presses the `map` button of a row
- **THEN** the page shows the map zoomed to that route with the route's popup open

#### Scenario: Keyboard row selection

- **WHEN** a keyboard user activates the `map` button of a row
- **THEN** the map shows the route's popup and focus is on its first booking link

#### Scenario: Escape returns to the row

- **WHEN** the user presses Escape in a popup that was opened from a list row
- **THEN** the popup closes, the list is shown again and focus is on that row's `map`
  button

#### Scenario: Click on a row

- **WHEN** the user clicks a row outside its buttons and links
- **THEN** nothing happens

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

### Requirement: Map page toolbar layout

The map page toolbar SHALL have a summary row with the page title, the last-updated
time, the route and trip counts and the map/list toggle, and a filter area that
groups the filters as start date (from, to, week), distance, pick-up (country,
station) and return (country, station), followed by the reset button. Below 700 px
the page title SHALL be the short `Rally map` and the filter area SHALL be hidden
behind a `Filters` button that shows and hides it and reports its state with
`aria-expanded`, so the map or list fills the rest of the screen. In the open filter
area below 700 px, each country and station dropdown SHALL have a row of its own.

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
