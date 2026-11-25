# Proposal

## Why

The map page grew one toolbar control at a time: a row of labelled dropdowns, a
`List` button that swaps the map for a table, a `Chains` button, and route popups that
cover the map and hold up to twenty booking rows. The redesign brief (part 1 of 4,
`ux-shell`) gives the page a clear shell: two views, one mode switch, filter chips and
a sidebar that replaces the popups.

## What Changes

- App bar: logo, `Rally map`, the `Map | Trips` views, the `Single rallies | Chains`
  switch and `Updated 18 Nov, 03:12 UTC` with the scan counts in its tooltip.
- Filter bar: one chip per filter (`Dates`, `Distance`, `Pick-up`, `Return`, and
  `Chain options` in chain mode) that shows its value and opens a small panel with
  today's controls. An active chip is blue with an `×`; `Clear all` replaces `Reset`.
  The filter bar also shows the counts.
- Map view: a sidebar beside the map lists one card per route (sortable). Hovering a
  card highlights its route and hovering a route highlights its card. Clicking either
  opens the route in the sidebar: stats, trip windows with `Book`, `Continue from`
  (routes leaving the return station), `Also from` and `Show these trips in the list`.
  Chains get the same list and detail. Route popups are gone.
- Stations: a 32 px click target, and tooltips that say what a click does.
- Trips view: a full page with the trips table (sort by start, end, distance; group by
  route or pick-up; `Map` opens the route in the map view) or the chain cards.
- URL: the view, the mode, the filters, the chain options, the open route or chain,
  the sort orders and the grouping live in the hash, so a reload or a shared link shows
  the same page. Opening a route or chain and switching views push a history entry;
  filters replace it. Unknown or invalid values are ignored.
- The chain options of #45 move into the `Chain options` chip's panel; on a phone the
  panel opens when `Chains` is pressed. Their behaviour is unchanged.
- Picking a chain from the map (#44, PR #47) moves from popups into the sidebar: a leg
  or connection lists the chains that use it (`N chains use this leg`, the `Chain uses`
  filter), or opens the only one; a leg of the open chain is marked in it; `Trips`
  chain cards open their chain on click.

Out of scope (later parts): the full chain options design (#45), the phone bottom sheet, the full-height phone filter sheet and phone trip
cards beyond keeping the page usable on a phone.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the map page's layout, filters, list and detail views, route and
  chain selection, history and URL state.
