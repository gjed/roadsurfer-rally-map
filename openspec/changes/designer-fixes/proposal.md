# Proposal

## Why

The designer review of the redesign ([#34](https://github.com/gjed/roadsurfer-rally-map/pull/34))
found that the map itself is still the weakest part of the page
([#38](https://github.com/gjed/roadsurfer-rally-map/issues/38)). On the real scan
(665 trips, 393 routes) every station is a stack of per-route markers, so a click opens
a random route; an opened route is not highlighted; the first view is a solid blue
blob that crops Scandinavia and Iberia; and the list needs about 1,330 tab stops, has
booking links below the WCAG 2.5.8 minimum tap size and drops keyboard focus when a
popup is closed.

## What Changes

- Stations: one marker per station replaces the per-route markers. Clicking it
  filters the pick-ups to that station; its tooltip counts departures and arrivals.
- Routes: lines are thinner and more transparent. A route is highlighted (accent
  colour, full opacity, drawn on top) while hovered or while its popup is open, and is
  reset when neither holds, on touch screens as well.
- First view: the map fits the drawn routes once, instead of a fixed centre and zoom.
- Legend: a single station entry, an explanation of which way arcs bend, and sample
  line weights that match the drawn weights.
- List: an explicit `map` button per row, labelled `Show <from> to <to> on map`, is the
  only way to open a route from the list. Rows are no longer focusable or clickable.
  Escape in the popup returns to the list with focus on that button.
- Touch: booking links get a tap area of at least 24x24 px under `pointer: coarse`
  without making rows taller.
- Phone layout: the country and station selects take a full row each, dates show as
  `MM-DD` with the full date in `title`, and a short page title is shown.
- Desktop polish: the list does not stretch to the full width, the `km` header is
  right-aligned, the sticky header has a bottom edge, the filters fit one row at
  1280 px, and the week slider resets when the dates are typed by hand.
- The release tag moves from the footer strip into the map's attribution control and
  the footer is removed.

Out of scope: road distances ([#7](https://github.com/gjed/roadsurfer-rally-map/issues/7)),
rally chains ([#8](https://github.com/gjed/roadsurfer-rally-map/issues/8)), any scanner
change, any new dependency.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: station markers, route highlight, first view, legend, list row
  button and focus, touch tap area, phone and desktop layout, release tag placement.
- `site-publishing`: the deployed page shows the release tag in its map attribution
  instead of a footer.

## Impact

- `rally-map.template.html`, the README, the `--release` help string in
  `roadsurfer-rally.py`, and a comment in `scan.yml`. The `/*DATA*/[]`, `/*SCAN*/null`
  and `/*RELEASE*/null` placeholders, `esc()`, the faceted filters and the inline script
  after the Leaflet tag stay as they are. No new dependency, no CDN.
