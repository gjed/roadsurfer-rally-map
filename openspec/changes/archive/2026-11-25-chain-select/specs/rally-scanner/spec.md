# Spec Delta

## MODIFIED Requirements

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
  `Click to only show trips from here`, or `Click to show trips from every station` when
  selected

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

The `Map` button of a chain, a click on its row and a chain chosen from a leg popup SHALL draw
that chain over the others, which are dimmed, with its legs in the highlight colour and
numbered, its stations and its connections, and open a popup above it that lists the legs
with a booking link each, the hand-overs, the rest days and the km driven, with the whole
chain fitted below the popup. With the keyboard, focus SHALL move to the popup's
first booking link.

#### Scenario: Chain from the list

- **WHEN** the user presses the `Map` button of a chain
- **THEN** the page shows the map fitted to the chain with its legs highlighted and a
  popup with a `Book` link for each leg

#### Scenario: Keyboard

- **WHEN** a keyboard user activates the `Map` button of a chain
- **THEN** focus is on the first `Book` link of its popup

### Requirement: Chain selection lifetime

The selected chain SHALL stay drawn until Escape, a click on empty map or a change of the
filters or settings. A click on any part of the chain, or on a leg or a connection of
the overview, SHALL NOT clear it. Escape SHALL also close its popup and, for a chain
opened from the list, return to the list. Escape with a leg popup open SHALL only close
that popup.

#### Scenario: Closing the popup

- **WHEN** the user closes the popup with its close button
- **THEN** the chain stays highlighted until the user presses Escape or clicks the map

#### Scenario: Escape in a leg popup

- **WHEN** a chain is selected and the user presses Escape with a leg popup open
- **THEN** the popup closes and the chain stays; a second Escape clears it

### Requirement: Chain legend

In chain mode the legend SHALL read `leg of 1 chain`, `10 or more chains`, `connection to the next pick-up (train, bus)`, `selected chain` and `station: click to only show chains starting here`, and it
SHALL keep the estimate entry when a connection is allowed or a distance is estimated and
end with `click a line to pick a chain`.

#### Scenario: Legend in chain mode

- **WHEN** the user opens the legend in chain mode
- **THEN** it has an entry with a dotted line labelled `connection to the next pick-up (train, bus)`

## ADDED Requirements

### Requirement: Chain leg popup

In chain mode a click or tap on a leg or a connection SHALL open a popup headed `In N chains`, where N counts the chains on the map that use it, with `on the map` added while the
toolbar reads `Showing 200 of N chains`. Under it the popup SHALL show the leg or
connection with its distance and list up to 8 of those chains in the order of the list,
each as a button with its stations, dates, days and km driven. Choosing a chain SHALL
show it like the list's `Map` button.

#### Scenario: Leg used by three chains

- **WHEN** the user clicks a blue leg used by three chains
- **THEN** the popup reads `In 3 chains` with three buttons, in list order, and no
  `Show all` link

#### Scenario: Choosing a chain

- **WHEN** the user chooses a chain in the popup
- **THEN** the map shows that chain as the list's `Map` button does

#### Scenario: Busy leg

- **WHEN** the user clicks a leg used by 14 of the chains on the map and 37 in all
- **THEN** the popup lists 8 chains and ends with `Show all 37 in the list`

### Requirement: Chain leg popup layout

Only the chain list of a leg popup SHALL scroll, and the selected chain, if listed,
SHALL be marked. When more chains use the leg or connection than the popup lists, the
popup SHALL end with `Show all N in the list`, counting every chain that passes the
filters. At 700 px or less a tap on a line SHALL close the filter panel first.

#### Scenario: Tap on a line on a phone

- **WHEN** the user taps a leg at 375 px with the filter panel open
- **THEN** the panel closes and the popup opens on the taller map

### Requirement: Chain leg filter

`Show all N in the list` SHALL show the list with only the chains that use that leg or
connection. That filter SHALL count in `Filters (n)`, show as a `Chain uses` group with a
`×` button in the filter bar and as `Only chains using <leg>` with a `Show all chains`
button over the list, and be cleared by `Reset`, by either button and by switching
between chains and trips.

#### Scenario: Show all

- **WHEN** the user chooses `Show all 37 in the list`
- **THEN** the list shows the chains of that leg, the button reads `Filters (1)` and
  `Reset` shows

#### Scenario: Reset with a leg filter

- **WHEN** the user presses `Reset` with that filter on
- **THEN** the filter is gone and the list shows every chain again

### Requirement: Chain leg filter scope

The leg filter SHALL apply to the map, the list and the station dropdown counts, and
station clicks and the other filters SHALL keep it. With no chain left, the first hint
SHALL be `remove the leg filter`.

#### Scenario: Pick-up dropdown

- **WHEN** the leg filter is on
- **THEN** the `Chain starts at` dropdown counts only the chains that use the leg

### Requirement: Chain row selection

A click or tap on a chain row outside its links, its buttons and a text selection SHALL
show that chain on the map like the `Map` button, and a row SHALL show a pointer cursor.
The row of the chain on the map SHALL be highlighted and its `Map` button marked
`aria-current`.

#### Scenario: Click on a chain row

- **WHEN** the user clicks the days cell of a chain row
- **THEN** the page shows the map with that chain selected, and its row is highlighted
  in the list

#### Scenario: Link in a row

- **WHEN** the user clicks the `Book` link of a leg in a row
- **THEN** the booking page opens and the chain is not shown on the map

### Requirement: Chain line hit area

A leg and a connection SHALL be hit by a click or a tap within a band wider than the
line, and its tooltip SHALL name the number of chains on the map that use it.

#### Scenario: Tap beside a line

- **WHEN** the user taps 8 px beside a thin leg at 375 px
- **THEN** the popup of that leg opens

### Requirement: Chain selection parts

Every leg, connection and station of the selected chain SHALL open its popup when
clicked, with a tooltip that says so, and SHALL NOT clear the chain.

#### Scenario: Second leg

- **WHEN** the popup of the selected chain is closed and the user clicks its second leg
- **THEN** the chain stays selected and its popup opens
