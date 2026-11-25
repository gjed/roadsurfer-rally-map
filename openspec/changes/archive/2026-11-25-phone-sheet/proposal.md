# Proposal

## Why

The redesign brief (part 4 of 4, `phone-sheet`) gives phones their own layout. Until
now a phone stacked the map over the route list, 55/45, so neither had room: the map
showed a strip of Europe and the list three cards. The filters sat behind one chip each,
and the Trips cards had narrow buttons.

## What Changes

- Map view below 700 px: the map fills the screen and the results are a bottom sheet
  over it with three snap points, peek (up to 330 px), half (about 62 %) and full. The
  grip is a button: a tap or Enter goes to the next snap point, the arrow keys, Home and
  End move between them, and a drag (or flick) goes to the nearest one. The map stays
  tappable above the sheet, and the attribution and the fits stay above it.
- Opening a route or a chain puts the sheet at half, fits the map above it and shows a
  floating `←` and the route or chain title over the map; going back returns the sheet
  to where it was.
- A dark `Filters · n` chip starts the chip row. It opens a full-height filter sheet with
  every filter (and the chain options in chain mode) and a footer `Reset (n)` and
  `Show N trips` (or chains). `n` counts the active filters, the chain options and the
  leg filter. Changes apply with `Show`; the close button, Escape and a tap outside put
  back the state the sheet opened with. The `Chain options` sheet that `Chains` opens
  behaves the same way.
- Below 700 px the counts and `Clear all` leave the filter bar: the sheet and the Trips
  heading carry the counts and `Reset (n)` in the filter sheet clears everything.
- Trips view below 700 px: each trip is a white card with its dates in bold, distance and
  nights, pick-up and return, and `Map` (one third) and `Book` (two thirds) buttons
  44 px tall.

Desktop does not change. Out of scope: anything above 700 px.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the phone layout of the map view, the filters and the Trips cards.

## Impact

`rally-map.template.html` and README wording only. No new dependency, no request.
