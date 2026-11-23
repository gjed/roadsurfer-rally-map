# Design

## Context

The `designer-fixes` change implemented
[#38](https://github.com/gjed/roadsurfer-rally-map/issues/38). A designer review of the
page then measured it on the real scan and at 1280 px and 375 px (with touch
emulation), and returned exact values. Where it refines a #38 item its value replaces
the #38 wording.

## Decisions

- **Grey basemap.** The street map has blue sea and yellow motorways, the same hues as
  the routes and the highlight. Esri's World Light Gray Base needs no new dependency
  or key; its labels come from the Reference layer in a pane between the routes and
  the stations, with `pointer-events: none`. Street-level detail is lost, which does
  not matter for choosing a 7-day rally; the max zoom drops from 18 to 16.
- **Highlight colour `#bf360c`.** It has 4.9:1 on land and 3.6:1 on sea (WCAG 1.4.11
  asks for 3:1) and stays far from the route blue for all three colour-vision types;
  `#e60` had 2.8:1 and 2.1:1. The line also gets 2 px more weight and a white
  drop-shadow halo through a CSS class on its SVG path.
- **`popupclose` always resets.** Leaflet fires it while `isPopupOpen()` is still
  true, so a guarded reset would leave a tapped route highlighted. `mouseout` keeps the
  guard.
- **Opacity by trips.** `min(.35 + trips * .1, .8)`: with 250 of 393 routes at one
  trip, a flat .4 erased the hierarchy. The overview lines do not reach 3:1 contrast;
  the highlighted line, the markers and the list are the accessible route.
- **Station markers.** Radius 4 with a `#003d7a` outline (at least 7:1 on every
  basemap tone); the selected pick-up station is filled and larger. The target is
  small on touch screens, which WCAG 2.5.8 allows because the pick-up dropdown does
  the same. Clicking the selected station clears the filter.
- **Fit to the stations, whole-number zoom.** Fractional zoom leaves seams and shrinks
  labels on raster tiles. The fit happens once, so dragging the week slider never
  moves the map.
- **Legend without direction.** An arc's bend cannot be learned at a glance, and once
  a pick-up is chosen every arc starts at the same place; the tooltip and popup say
  `A → B`. The `designer-fixes` direction sentence is removed.
- **`ResizeObserver`, not manual calls.** The toolbar changes height when selects fill
  and when the week slider moves; Leaflet had cached the first size. An observer on the
  map element calls `invalidateSize()`. Switching from the list back to the map still
  calls it directly, because the map must have its size before `fitBounds` runs.
- **`Name, CC`.** Five station names already contain parentheses, so `Freiburg-Basel (Germany) (DE)` read badly. The format is used in cells, tooltips, headings and
  accessible names.
- **Dates as `Thu 19 Nov` on phones.** `11-12` is ambiguous to European readers and
  the weekday helps planning. Both forms are in the markup and CSS switches them, so
  assistive technology reads only the visible one.
- **Reset in the top row.** It does nothing in the default state, so it is hidden then;
  after pressing it focus moves to the `List` button so keyboard users are not left on
  a hidden element.
- **Week slider.** Position 0 is all dates again and position k is the week starting
  `min + (k - 1) * 7` days, so dragging back to the start restores the full range.
  Typed dates leave the slider at 0 with `custom dates`.
- **Empty state.** One absolutely positioned message with a `Reset filters` button over
  the map, the same copy in the list's empty row. With no data at all it says that no
  trips are on offer and has no button.
- **Phone list as cards.** Rows become two-line cards with a CSS grid, and the header
  becomes a sticky sort bar showing only the sortable columns. Plain CSS, no change to
  the markup order. Roles are not restated: current Chrome, Firefox and Safari keep
  table semantics for `display: grid` rows.
- **Hover and focus.** Hover styles apply only under `(hover: hover)` so they do not
  stick after a tap. Route paths drop the focus outline, since they are `tabindex=-1`
  and keyboard users never land on them. While a popup is open the tooltip pane is
  hidden with `:has()`; browsers without it keep the old behaviour.
