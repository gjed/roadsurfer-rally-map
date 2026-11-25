# Delta for rally-scanner

## MODIFIED Requirements

### Requirement: App bar and filter bar layout

The page SHALL have an app bar with the logo, `Rally map`, the `Map | Trips` views,
the `Single rallies | Chains` switch and the scan time, and a filter bar with one chip
per filter, the counts and `Clear all`. Each chip SHALL be a button with
`aria-haspopup="dialog"` and `aria-expanded` that shows the filter's name and value and
opens a panel (`role="dialog"`) with its controls, which Escape and a click outside
close. Below 700 px the chips SHALL scroll sideways on one row that starts with a
`Filters` chip, and the counts SHALL move from the filter bar to the results sheet and
the Trips heading.

#### Scenario: Phone width

- **WHEN** the page is opened 375 px wide
- **THEN** the app bar shows the title, the views, the mode switch and the scan time,
  the chips scroll sideways on one row after the `Filters` chip, and the map fills the
  rest of the screen under the results sheet

#### Scenario: Filters opened on a phone

- **WHEN** the user presses a chip at 375 px
- **THEN** its panel opens inside the screen with every control readable, and pressing
  `Done` or Escape closes it without changing any filter

#### Scenario: Desktop width

- **WHEN** the page is opened 1280 px wide
- **THEN** the four filter chips share one row, and there is no `Filters` button

### Requirement: Trip list layout

On a wide screen the trips table SHALL fill the page up to 1320 px, inside a box that
scrolls sideways when it must, with the distance header right-aligned over the
distances and a sticky header with a visible bottom edge. Below 700 px each row SHALL
be a card that fits the screen without horizontal scrolling, with its dates in bold,
its distance and nights, its stations, and a `Map` button one third and a `Book` link
two thirds wide, both at least 44 px tall, under a sticky bar with the sortable
headers.

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

### Requirement: Clear all

`Clear all` SHALL be in the filter bar and SHALL be shown only while at least one
filter differs from its reset value. Pressing it SHALL clear every filter and the chain
options, and focus SHALL move to the first chip. Below 700 px the filter sheet's
`Reset (n)` SHALL take its place.

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

### Requirement: Chain options on phones

Below 700 px the `Chain options` panel SHALL be a sheet from the bottom of the screen
with the title `Chain options`, a close button, controls at least 44 px tall and a
footer that stays in view. Turning `Chains` on SHALL open it, with `aria-expanded` true
on its chip. `Show N chains`, the close button, Escape and a tap above the sheet SHALL
close it; only `Show N chains` SHALL keep the options changed in it, and the other ways
SHALL restore the options it opened with.

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

## ADDED Requirements

### Requirement: Results sheet on phones

Below 700 px the map view SHALL fill the screen with the map and show the route or
chain list in a sheet from the bottom with three heights: peek (at most 330 px and half
the view), half (about 62 % of the view) and full. The map above the sheet SHALL stay
usable, and the map's attribution, its fits and the legend SHALL stay above the sheet.
With reduced motion the sheet SHALL not animate.

#### Scenario: First load on a phone

- **WHEN** the page is opened 390 × 844 px
- **THEN** the sheet is 330 px tall with the route count, the sort and the first cards,
  every station is visible above it and the page does not scroll sideways

### Requirement: Results sheet grip

The sheet's grip SHALL be a button named `Expand results` (`Collapse results` at full)
with `aria-expanded`. A tap, Enter or Space SHALL move the sheet to the next height, the
arrow keys, Home and End SHALL move it between the heights, and a drag SHALL end at the
nearest height.

#### Scenario: Grip

- **WHEN** the user taps the grip three times
- **THEN** the sheet goes to half, to full with the grip named `Collapse results`, and
  back to peek

#### Scenario: Keyboard

- **WHEN** a keyboard user focuses the grip and presses the up arrow, End and Home
- **THEN** the sheet goes to half, full and peek

### Requirement: Route and chain on phones

Below 700 px opening a route or a chain SHALL put the sheet at half with the route or
chain detail, fit the map in the space above the sheet, and show a floating back button
and the route or chain title over the map. Going back, with that button, the detail's
back button, Escape or the browser's Back, SHALL return the sheet to the height it had
and the focus to the card that opened it.

#### Scenario: Open a route

- **WHEN** the user taps a route card at peek
- **THEN** the sheet is at half with the route's windows and `Book` links, the map shows
  the route above it and a floating bar reads `← Vienna → Berlin-Schönefeld`

#### Scenario: Back

- **WHEN** the user taps the floating back button
- **THEN** the route closes, the sheet returns to peek and focus is on the route's card

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
filters, the chain options that differ from their defaults and the leg filter, and
`Filters` when there is none.

#### Scenario: Count in chain mode

- **WHEN** the user turns `Chains` on, picks `3` legs and opens a leg filter
- **THEN** the chip reads `Filters · 2`
