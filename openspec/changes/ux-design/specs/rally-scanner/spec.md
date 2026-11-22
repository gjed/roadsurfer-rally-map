# Spec Delta

## ADDED Requirements

### Requirement: Map page toolbar layout

The map page toolbar SHALL have a summary row with the page title, the last-updated
time, the route and trip counts and the map/list toggle, and a filter area that
groups the filters as start date (from, to, week), distance, pick-up (country,
station) and return (country, station), followed by the reset button. Below 700 px
the filter area SHALL be hidden behind a `Filters` button that shows and hides it and
reports its state with `aria-expanded`, so the map or list fills the rest of the
screen.

#### Scenario: Phone width

- **WHEN** the page is opened 375 px wide
- **THEN** the toolbar shows only the counts, the last-updated time, the `Filters`
  button and the map/list toggle, and the map fills the rest of the screen

#### Scenario: Filters opened on a phone

- **WHEN** the user presses `Filters` at 375 px
- **THEN** every filter and the reset button are shown, part of the map stays
  visible, and pressing `Filters` again hides them without changing any filter

#### Scenario: Desktop width

- **WHEN** the page is opened 1280 px wide
- **THEN** the summary row and the grouped filters are both shown and there is no
  `Filters` button

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
the thicker line for routes with more trips, the hollow pick-up marker and the filled
return marker. The legend SHALL start open at desktop widths and collapsed below
700 px.

#### Scenario: Reading the map

- **WHEN** the page is opened 1280 px wide
- **THEN** the legend shows a one-trip line, a five-or-more-trips line, the pick-up
  marker and the return marker with their meaning

### Requirement: Route popups

A route popup SHALL show the route, its estimated road distance and trip count, and
a table with one row per trip: start date, end date, price when present and a
booking link that opens in a new tab with `rel="noopener"`. A long table SHALL scroll
inside the popup with its header row visible. Every value from the API SHALL be
escaped before it is inserted as HTML.

#### Scenario: Route with several trips

- **WHEN** the user opens the popup of a route with nine trips
- **THEN** the popup shows the route heading, `~N km by road · 9 trips` and nine
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
route, and Escape inside an open popup SHALL close it.

#### Scenario: Keyboard only

- **WHEN** a keyboard user tabs through the page
- **THEN** every filter, the reset button, the `Filters` button, the map/list toggle,
  the zoom buttons, the legend, the list headers and the list rows receive a visible
  focus indicator and can be operated with the keyboard, without stepping through
  the route lines

### Requirement: Favicon

The map page SHALL embed its favicon in the page head as an inline SVG data URI, so
the published page and a page rendered locally with `--map` show it without any
extra file, and the browser SHALL request no favicon file from the server.

#### Scenario: Published page

- **WHEN** the published page is opened
- **THEN** the browser tab shows the route icon and no request returns 404 for a
  favicon

## MODIFIED Requirements

### Requirement: Trip list selection

Selecting a row SHALL show that route on the map with its popup open. When the row is
selected with the keyboard, focus SHALL move to the popup's first booking link.

#### Scenario: Row selection

- **WHEN** the user selects a row outside its booking link
- **THEN** the page shows the map zoomed to that route with the route's popup open

#### Scenario: Keyboard row selection

- **WHEN** a keyboard user presses Enter on a focused row
- **THEN** the map shows the route's popup and focus is on its first booking link
