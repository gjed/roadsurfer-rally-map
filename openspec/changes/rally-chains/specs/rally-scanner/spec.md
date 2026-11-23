# Spec Delta

## ADDED Requirements

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
