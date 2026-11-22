# Design

## Context

`rally-map.template.html` is the whole page: a `#bar` toolbar with eight filters,
reset, the map/list toggle, `#updated` and `#count` in one wrapping flex row, then
`#map` and `#list`. `render()` builds one arc per route (`#06c`, weight
`min(2 + trips, 7)`), a hollow start marker, a filled end marker and a popup with an
inline-styled `<ul>`. The review below was made on the page rendered from the test
fixture (6 trips) and from the latest published scan (665 trips, 393 routes), at
1280 px and 375 px. The `designer` agent could not be started from this session (the
agent runner refused a nested subagent), so the review was made by hand against the
same checklist.

## Review findings

| #   | Finding                                                                                                                                                      | Decision                                                            |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| 1   | At 375 px the toolbar takes 8 rows (about 225 of 740 px) before the map starts.                                                                              | Applied: filters fold behind a `Filters` button below 700 px.       |
| 2   | Filters have no grouping; `Start`/`to` and `From`/`To` read as one run of labels.                                                                            | Applied: four labelled groups (start date, distance, pick-up, return). |
| 3   | Nothing shows which filters are active, so a narrowed map looks like missing data.                                                                           | Applied: highlighted controls and groups, count on `Filters`.       |
| 4   | Line weight and the two markers have no legend.                                                                                                              | Applied: collapsible legend, open on desktop, closed on phones.     |
| 5   | Booking links are `#0b6` on white, 2.5:1, below AA (4.5:1).                                                                                                  | Applied: links use a darker green that passes AA.                   |
| 6   | The second date input and the maximum distance input have no accessible name; the week slider announces only a number.                                       | Applied: `aria-label` on every unlabelled input, `aria-valuetext` with the week's dates. |
| 7   | List rows show focus only as a pale background; other controls rely on browser defaults.                                                                      | Applied: one `:focus-visible` outline for every interactive element. |
| 8   | Count changes are silent for screen readers; sorted header state is only a glyph.                                                                            | Applied: `aria-live` on `#count`, `aria-sort` on the sorted header. |
| 9   | Selecting a list row by keyboard hides the focused row and drops focus on `<body>`.                                                                         | Applied: focus moves to the popup's first booking link.            |
| 10  | Popups use inline styles and a bullet list; dates and links do not line up.                                                                                  | Applied: a small table with a sticky header, styled from the stylesheet. |
| 11  | Popup booking links have `target="_blank"` without `rel="noopener"`.                                                                                         | Applied.                                                            |
| 12  | No page title is visible and the page has no landmarks.                                                                                                      | Applied: `<h1>` in the summary row, `<header>` and `<main>`.        |
| 13  | The page has no viewport meta tag, so a phone renders it 980 px wide and scales it down. | Applied: `width=device-width, initial-scale=1`. |
| 14  | Re-sorting the list redraws its header and drops keyboard focus on `<body>`.               | Applied: focus returns to the header that was used. |
| 15  | Chrome puts all 1184 route paths and markers in the tab order, so the zoom buttons and attribution sit behind them. | Applied: paths get `tabindex="-1"`; the list is the keyboard path. |
| 16  | Escape does not close a popup while focus is inside it (Leaflet only handles it when the map has focus). | Applied: Escape in a popup closes it and focuses the map. |
| 17  | Dropdown defaults read `any (665)` with no hint of what they filter once the outer labels are gone. | Applied: `any country (N)` and `any station (N)`. |
| 18  | 393 routes in one colour form a dense blue mass over central Europe.                                                                                         | Not applied: per-route colours carry no meaning, and clustering or colour by distance would be a new encoding or dependency outside #27. The filters and the list are the way to narrow it down. |
| 19  | Route arcs and markers are not reachable by keyboard.                                                                                                        | Not applied: the list view is the keyboard path to every route and opens the same popup; making 393 routes focusable would add hundreds of tab stops (see 15). |

## Decisions

- **Collapse breakpoint at 700 px.** At 1280 px the grouped filters take two rows
  below the summary row (one from about 1400 px); below about 700 px they would wrap
  into five or more rows, so they fold away there. Squeezing them into one row at
  1280 px meant truncating the station names in the dropdowns. The filter panel scrolls inside at most 60% of the viewport height, so
  part of the map stays visible while it is open.
- **Reset values define "active".** A date input is active when it differs from the
  first or last start date, a distance input when it is not empty, a dropdown when it
  is not `any`. The week slider only moves the dates, so it adds no group of its own.
- **Reset stays enabled.** Disabling it when nothing is active would take it out of
  the tab order and hide it from keyboard users looking for it.
- **Legend is a Leaflet control holding a `<details>` element.** Native disclosure
  gives keyboard support and state without script; the script only sets its initial
  state from the viewport width.
- **Colours.** Route blue `#06c` (5.6:1 on white) stays and becomes the accent for
  focus and active filters; links become `#067a3f` (5.3:1). Hover orange stays.
- **Favicon inline.** A data URI in `<head>` needs no extra file, works for a local
  `--map` file opened from disk, and needs no change to `scan.yml`. The icon repeats
  the legend: a white arc from a hollow pick-up marker to a filled return marker on a
  route-blue tile.
