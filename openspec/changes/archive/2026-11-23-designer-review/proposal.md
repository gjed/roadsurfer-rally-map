# Proposal

## Why

A designer review of the page, run against the real 665-trip scan (393 routes, 76
stations), refined the items of
[#38](https://github.com/gjed/roadsurfer-rally-map/issues/38) and found more problems
in the same areas: the orange highlight is as faint as a motorway on the street
basemap, a click on a route draws a black rectangle across the map, the map keeps a
stale size while the toolbar changes height, an empty result leaves a bare map, dates
read ambiguously, and the phone list overflows once the `map` button is added.

## What Changes

- Basemap: Esri's light grey canvas with a reference-label layer replaces the street
  map, so blue routes and a deep-orange highlight stand out. The highest zoom is 16.
- Routes: opacity grows with the trip count, the highlighted route is a deep orange
  with at least 3:1 contrast and a white halo and is a little thicker, a click leaves
  no focus rectangle, and the tooltip is hidden while a popup is open.
- Stations: a dark outline for contrast, the selected pick-up station is filled, a
  second click on it clears the filter, and the tooltip says what a click does.
- First view: fits the stations, with whole-number zoom.
- Legend: four samples (one trip, five or more trips, selected route, station); the
  arc-direction line is removed, since the tooltip and popup already say `A → B`.
- Copy: `Name, CC` instead of `Name (CC)`, `Any country` and `Any station`,
  `665 of 665 trips`, `Thu 19 Nov` on phones, `Map` and `Book` with descriptive
  accessible names, and `to` for the route arrow in assistive technology.
- Toolbar: `Reset` moves into the top row and shows only while a filter is active, the
  `Filters` button shows when its panel is open, hover styles apply only to devices
  with hover, and the week slider's first position means all dates again.
- Empty state: a message with a `Reset filters` button on the map and in the list.
- Map size follows the layout, so fit and centre stay right when the toolbar changes.
- Phone list: rows are two-line cards, so nothing overflows.

Out of scope: road distances ([#7](https://github.com/gjed/roadsurfer-rally-map/issues/7)),
rally chains ([#8](https://github.com/gjed/roadsurfer-rally-map/issues/8)), any scanner
change, any new dependency.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: basemap, route and station presentation, legend, copy, toolbar,
  empty state, map sizing, phone list.

## Impact

- `rally-map.template.html`, the README. The `/*DATA*/[]`, `/*SCAN*/null` and
  `/*RELEASE*/null` placeholders, `esc()` and the vendored Leaflet files are
  untouched. No new dependency; the tiles still come from Esri.
