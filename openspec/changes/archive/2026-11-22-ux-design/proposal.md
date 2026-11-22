# Proposal

## Why

The map page has never had a design pass
([#27](https://github.com/gjed/roadsurfer-rally-map/issues/27)). On a phone the
toolbar wraps into eight rows and pushes the map below the fold, nothing shows which
filters are active, the line weights and the two marker styles have no legend, the
booking links fail WCAG AA contrast, and several inputs have no accessible name. The
tab also shows a generic icon and the browser gets a 404 for `/favicon.ico`
([#29](https://github.com/gjed/roadsurfer-rally-map/issues/29)).

## What Changes

- The toolbar gets two parts: a summary row (title, last-updated time, counts, the
  map/list toggle) and the filters, grouped as start date, distance, pick-up and
  return. Below 700 px the filters fold behind a `Filters` button, so the map fills
  the screen until the user opens them.
- Active filters are highlighted, their group is marked, and the `Filters` button
  shows how many groups are active.
- A collapsible legend on the map explains the route line, the line weight by trip
  count and the pick-up and return markers.
- Popups use a styled trip table instead of an inline-styled list; their booking
  links open with `rel="noopener"`.
- Accessibility: every control has an accessible name, focus is visible on every
  interactive element, text and controls meet WCAG AA contrast, the counts are
  announced on change, the sorted list header carries `aria-sort`, and selecting a
  list row by keyboard moves focus into the route's popup.
- The page head embeds an inline SVG favicon: a route arc between a pick-up and a
  return marker.

Out of scope: new data fields, road distances
([#7](https://github.com/gjed/roadsurfer-rally-map/issues/7)), chained trips
([#8](https://github.com/gjed/roadsurfer-rally-map/issues/8)), any scanner change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the map page layout, legend, responsive and accessibility
  behaviour, and favicon.

## Impact

- `rally-map.template.html` only, plus README wording. The `/*DATA*/[]` and
  `/*SCAN*/null` placeholders, `esc()`, the empty-scan guards, the faceted filters
  and the inline script after the Leaflet tag stay as they are. No new dependency,
  no CDN, no change to `scan.yml`.
