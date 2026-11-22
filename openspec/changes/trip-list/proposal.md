# Proposal

## Why

The map answers "where can I go", but finding the next trip from a given city or
comparing dates means opening popups one route at a time
([#28](https://github.com/gjed/roadsurfer-rally-map/issues/28)). A sortable list of
the same trips answers those questions directly.

## What Changes

- The toolbar gets a map/list toggle. The list view replaces the map; the filters
  and the counts stay in the toolbar and keep their values when the view changes.
- The list shows one row per trip that passes the active filters, built from the
  same `passes()` check in the same `render()` pass as the map, so its row count is
  always the trip count in `#count`.
- Columns: start date, end date, pick-up station (country), return station
  (country), estimated road distance, price when the page has prices, and a booking
  link that opens in a new tab.
- Rows are sorted by start date. The start date, end date and distance headers
  re-sort the list; a second click reverses the order.
- Selecting a row switches to the map, zooms to that route and opens its popup.
- README describes the list view.

Out of scope: restyling the page
([#27](https://github.com/gjed/roadsurfer-rally-map/issues/27)), any scanner change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the map page also shows the filtered trips as a sortable list.

## Impact

- `rally-map.template.html` only; the placeholders and the inline script that the PR
  check extracts stay as they are. No new dependency.
