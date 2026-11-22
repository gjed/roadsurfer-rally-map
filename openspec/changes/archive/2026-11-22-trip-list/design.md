# Design

## Context

`rally-map.template.html` keeps every filter in the `#bar` toolbar. `passes(r)` is
the only filter predicate; `render()` refills the facet dropdowns, redraws one arc per
route with a popup listing its trips, and writes `N routes · n / total trips` to
`#count`. `roadKm()` gives the distance the popups show and the distance filter
uses.

## Goals / Non-Goals

**Goals:**

- Browse, sort and book the filtered trips without opening popups.
- The list and the map can never disagree with each other or with `#count`.
- Usable at 375 px wide.

**Non-Goals:**

- A visual redesign of the page; that is
  [#27](https://github.com/gjed/roadsurfer-rally-map/issues/27).
- Remembering the view or the sort across reloads.

## Decisions

- **The list replaces the map, at every width.** A `#view` button in the toolbar
  switches between them; its label names the view it switches to. A side-by-side
  layout on wide screens was rejected: it halves the map, needs a breakpoint and a
  second layout to test, and the issue allows either. One view at a time behaves the
  same at 1280 px and at 375 px.
- **One pass builds both views.** `render()` collects the trips that pass the filters
  while it groups them into routes, and builds the list from that array. The view
  toggle only flips a class on `<body>`; it never filters, so a filter selection
  survives any number of switches.
- **Columns and narrow screens.** Start, end, from (cc), to (cc), distance in km,
  price (only when some record has a price) and a `book` link with
  `target="_blank" rel="noopener"`. The table scrolls inside its own container with a
  sticky header; below 600 px the font and padding shrink and the station and date
  cells wrap, so every column, including the booking link, fits at 375 px without
  sideways scrolling.
- **Sorting.** Default is start date, ascending. Start, end and distance headers are
  buttons, so they work from the keyboard; clicking the active one reverses the
  order. Ties fall back to start date, then pick-up station, so the order is stable.
  Price is not sortable: it is a free-text string from the API.
- **Selecting a row opens the route on the map.** A click (or Enter on a focused row)
  switches to the map, calls `invalidateSize()` because the map was hidden, fits the
  route's arc and opens the same popup the arc has. Highlighting in place was
  rejected because the list hides the map. A click on the booking link only follows
  the link.
- **Escaping.** Every API-supplied value in a row, including dates and the route key
  stored in `data-key`, goes through `esc()`.

## Risks / Trade-offs

- Rebuilding the table on every filter change costs a few milliseconds for the
  current ~700 trips; it would need paging only at tens of thousands of rows.
