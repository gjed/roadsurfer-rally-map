# Design

## Decisions

- **One template, one render.** `render()` still recomputes everything from the
  controls; it now also writes the hash. Filter changes `replaceState`; opening a route
  or chain and switching views `pushState`, so Back closes a detail. A detail opened
  from another detail replaces the entry, so one Back returns to the list.
- **The sidebar is the popup.** The detail sits beside the map, not over it, so the
  map fits the route with fixed padding (`maxZoom` 8) instead of padding for an
  overlaid sidebar. Focus moves to the detail heading; `← All routes`, Escape and Back
  return focus to the card that opened it.
- **Hover layer.** The hovered or opened route is drawn again in its own pane, deep
  orange on a white halo, and the other lines drop to 0.18 stroke opacity via a class,
  so hover never restyles the base lines.
- **Station target.** Each station gets a transparent 16 px radius circle under its
  visible marker. Where the circles of nearby stations overlap, a click goes to the
  nearest station with departures; the tooltip stays on the visible marker.
- **Continue from.** Routes from the return station whose windows end on or after the
  first start of the opened route, from all the scan's offers, not only those passing
  the filters: they are for exploring. A route opened from there shows its windows
  under the date and distance filters, or all of them when none pass.
- **Chain options in a panel.** #45 put the options in the first fieldset of the filter
  area. With chips there is no filter area, so the fieldset moves into the `Chain options` chip's panel, with every control and id unchanged. Tab order now reaches
  the chip after the station chips, as the brief places it. On a phone the panel opens
  when `Chains` is pressed, replacing the open filter panel of #45. Its full design
  (segmented legs, stepper, range) is the later `chain-options` part.
- **Chain picking in the sidebar.** PR #47 picked chains through map popups: `In N chains` with up to 8 rows and `Show all N in the list`. The sidebar is the popup now,
  so a leg or connection sets the leg filter at once and the sidebar lists every chain
  that uses it (the 8-row cap and `Show all` go), as the brief's #44 section says; one
  chain opens directly. A leg of the open chain marks its card instead of opening the
  chain popup. A leg it does not use closes it (the brief), where #47 kept it until a
  chain was chosen. Escape closes the chain, then the leg filter. The `Chain uses` chip
  keeps #47's `gleg` fieldset and `legx` button; the 16/22 px hit lines are #47's.
- **Requirements renamed, not dropped.** Requirements whose subject disappears (the
  `List` toggle, route popups, the `Filters` button, `Reset`, chain list rows) are
  renamed to what replaces them and keep a scenario for each of their old ones.
  `Chain options panel` keeps `Tab order`, now about the panel: the chip placement
  means `Legs` is no longer the first control of the filter bar.

## Hash parameters

`#map` or `#trips`, then `mode=chains`, `week`, `start`, `end`, `kmin`, `kmax`, `fcc`,
`from`, `tcc`, `to`, `legs`, `same`, `rest`, `hop`, `dmin`, `dmax`, `drive`, `round`,
`route` (trips mode), `leg` and `chain` (chains mode), `rsort`, `sort`, `csort`, `group`.
Defaults are omitted.

## Phone

Until the `phone-sheet` part, the map view stacks the map over the list (55/45), the
chips scroll sideways, popovers are clamped to the screen and the Trips table turns
into cards with 40 px `Map` and `Book` buttons. The legend moves to the top-left corner
because the attribution wraps over the bottom corners.
