# Delta for rally-scanner

## MODIFIED Requirements

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

## ADDED Requirements

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
