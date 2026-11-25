# Delta for rally-scanner

## MODIFIED Requirements

### Requirement: Last-updated timestamp

When the map page has scan metadata, its app bar SHALL show the time the scan
finished, in UTC to the minute, as `Updated 18 Nov, 03:12 UTC`, with the offer, request
and failed-request counts in its tooltip. Below 700 px the time SHALL be at the bottom of
the filter sheet instead, as `Offers as of the scan of 18 Nov, 03:12 UTC`. Without scan
metadata it SHALL show no time.

#### Scenario: Page with scan metadata

- **WHEN** a page whose scan finished at `2026-11-18T03:12:05Z` is opened
- **THEN** its app bar shows `Updated 18 Nov, 03:12 UTC`

#### Scenario: Page without scan metadata

- **WHEN** a page rendered from a data file without a `scan` object is opened
- **THEN** its filter bar shows the trip and route counts and the page shows no time

#### Scenario: Scan time on a phone

- **WHEN** the user opens the filter sheet at 390 px on that page
- **THEN** the sheet ends with `Offers as of the scan of 18 Nov, 03:12 UTC`

### Requirement: App bar and filter bar layout

The page SHALL have an app bar with the logo, `Rally map`, the `Map | Trips` views,
the `Single rallies | Chains` switch and the scan time, and a filter bar with one chip
per filter, the counts and `Clear all`. Each chip SHALL be a button with
`aria-haspopup="dialog"` and `aria-expanded` that shows the filter's name and value and
opens a panel (`role="dialog"`) with its controls, which Escape and a click outside
close. Below 700 px the app bar SHALL be one row with the logo, `Rally map` and the
views, and the chips SHALL scroll on one row after a `Filters` chip.

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
its distance and nights, its stations and its `Map` and `Book` buttons, under a row
with `N trips on M routes` and the mode switch and a row with `Sort` and `Group`.

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

### Requirement: Chain mode

The app bar SHALL have a `Single rallies | Chains` switch whose buttons carry
`aria-pressed`; below 700 px a `Rallies | Chains` switch in the results sheet and the
Trips header SHALL take its place. A chain is a sequence of 2 or 3 rally legs, each
booked as its own trip, found from the offers on the page without any request.
Switching modes SHALL keep every filter and the view and close an open route or chain.
The count SHALL read `N chains from M trips`, or `Showing 200 of N chains from M trips`
above 200. `Chains` SHALL have a title that says what chains are.

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

### Requirement: Chain filters

In chain mode the start date filter and the week slider SHALL limit the first pick-up
day, the distance filter SHALL limit the distance of every leg, the pick-up filters SHALL
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

### Requirement: Chain list size

The chain lists SHALL show the first 200 chains in the sort order, and the filter bar
SHALL show how many chains there are in all, as
`Showing 200 of 23,267 chains from 781 trips`.

#### Scenario: More than 200 chains

- **WHEN** there are 2075 chains
- **THEN** the filter bar reads `Showing 200 of 2,075 chains`, the list has 200 cards
  and a note says how many are shown

### Requirement: Chain legend

In chain mode the legend SHALL read `Leg of 1 chain`, `10 or more chains`, `Selected`,
`Hop to the next pick-up`, `Click a leg or hop to list its chains` and
`Station — click to filter chain starts`, and it SHALL keep the estimate entry when a
connection is allowed or a distance is estimated.

#### Scenario: Legend in chain mode

- **WHEN** the user opens the legend in chain mode
- **THEN** it has an entry with a dotted line labelled `Hop to the next pick-up`

### Requirement: Chain options on phones

Below 700 px the `Chain options` panel SHALL be a sheet from the bottom of the screen,
over a dark backdrop, with `Chains: 2–3 rallies booked back to back. Set how they may connect, then browse them on the map.` above it, the title `Chain options`, a close
button, 44 px controls and a footer in view. Turning `Chains` on SHALL open it, with
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

## ADDED Requirements

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
