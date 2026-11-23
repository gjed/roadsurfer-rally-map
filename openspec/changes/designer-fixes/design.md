# Design

## Context

`render()` draws one arc per route with two circle markers per arc, so a busy station
carries dozens of stacked markers. Lines are opacity .75 and weight up to 7, the map
opens on a fixed centre, list rows are focusable and clickable, and the release tag
lives in a full-width footer. The findings come from
[#38](https://github.com/gjed/roadsurfer-rally-map/issues/38).

## Decisions

- **One marker per station, in its own pane.** Markers are collected by station name
  while the route loop runs and drawn afterwards in a Leaflet pane above the overlay
  pane. Highlighting a line with `bringToFront()` then moves it above the other lines
  but never over a marker, so the station stays clickable at the end of a highlighted
  route.
- **Departures and arrivals count trips.** The tooltip sums the trips of the filtered
  routes that leave from or arrive at the station, the same unit as the `(N)` in the
  station dropdowns and the popups. A station with no departures under the current
  filters (arrival only) shows `0 departures` and ignores the click, since the
  dropdown would clear that selection anyway.
- **Highlight is a pair of states, not a toggle.** `mouseover` and `popupopen` set the
  hot style and `bringToFront()`; `popupclose` always resets; `mouseout` resets only
  while the popup is closed. On a phone a tap fires `mouseover`, and the line resets
  when the popup closes or another route is tapped, so no line stays highlighted.
- **Line weight and legend share the formula.** Weight is `min(1.5 + trips * .7, 5)`
  and opacity .4; the legend samples are the weights for 1 trip (2.2) and 5 trips
  (5).
- **First view fits the drawn layers once.** The first `render()` calls `fitBounds`
  with padding; later renders keep the user's view. With no routes at all the old
  centre and zoom are the fallback, since Leaflet needs a view.
- **Arc direction.** `arc()` offsets the control point by `(-dLon, +dLat) * .2` in
  `[lat, lon]`: an eastbound route bulges south, a northbound one east. Every arc
  bulges to the right of the direction of travel, from pick-up to return. The legend
  says so and shows a small curve with an arrowhead.
- **Map button is the only list trigger.** The row keeps no `tabindex`, no pointer
  cursor and no key handler. A keyboard activation (click with `detail === 0`) moves
  focus into the popup's first booking link, as before.
- **Escape returns to the list.** The button is hidden while the map is shown, and a
  hidden element cannot take focus, so Escape closes the popup, switches back to the
  list view and focuses the button that opened the route. A popup opened by clicking a
  route on the map still sends focus to the map. The page remembers the button only
  while that route's popup is open.
- **Tap area by padding and negative margin.** Under `pointer: coarse`, booking links
  get 5 px vertical padding and the same negative margin, so they measure at least
  24 px tall and rows keep their height. The `map` button gets the same treatment.
- **Phone dates.** The year is wrapped in a span that is visually hidden below 700 px
  (not `display: none`, so screen readers still read the full date) and the cell has
  `title` with the full date. The year is ambiguous across New Year; the title and
  the `Start` sort keep it recoverable.
- **Short title instead of a hidden one.** Below 700 px the h1 shows `Rally map`;
  `roadsurfer` is visually hidden so the accessible name stays complete.
- **Filters in one row at 1280 px.** The selects and date inputs get narrower widths so
  the groups and `Reset` fit one row; `Reset` stays in the filter area because on a
  phone it belongs to the folded panel. The earlier design (ux-design) kept two rows to
  avoid truncated station names; the dropdown text is clipped now, the title attribute
  and the list show the full name, and the width is capped, not removed.
- **Release tag in the attribution.** `map.attributionControl.addAttribution(...)`
  receives `release <a>TAG</a>`, built with `esc()` and `encodeURIComponent`. The
  `/*RELEASE*/null` placeholder and the way `render()` fills it do not change, so
  `roadsurfer-rally.py` and `pr-check.yml` are untouched apart from the help string.
  The requirement is renamed from "Release footer" so its scenarios can change.
