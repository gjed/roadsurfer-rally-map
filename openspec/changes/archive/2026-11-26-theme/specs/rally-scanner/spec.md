# Delta for rally-scanner

## MODIFIED Requirements

### Requirement: Vendored Leaflet

The map template SHALL load Leaflet's JavaScript and CSS from `vendor/leaflet/` by
relative path. The repository SHALL ship an unmodified, pinned Leaflet 1.x release
there (`leaflet.js`, `leaflet.css`, `images/` and `LICENSE`) and record its version
in `vendor/leaflet/VERSION`. The page SHALL make no request to `unpkg.com`. Map tiles
load from Esri's World Light Gray Canvas in the light theme and World Dark Gray Canvas
in the dark theme, base and reference labels, up to zoom 16.

#### Scenario: unpkg blocked

- **WHEN** the map is generated in the repository root and served over HTTP with
  `unpkg.com` unreachable
- **THEN** Leaflet loads, the route lines and the default marker icon render, and the
  browser sends no request to `unpkg.com`

#### Scenario: Published page

- **WHEN** the map is published
- **THEN** `vendor/` is shipped next to `index.html`

### Requirement: Route highlight

A route SHALL be drawn in the selected colour (`#C2410C` in light, `#FF8A4C` in dark) on a
halo in the page's background colour, above the other lines, which drop to a low opacity, while the pointer or keyboard focus is on its card, while
the pointer is over its line, and while it is open. Pointing at a line SHALL also mark
its card and scroll it into view. The highlight SHALL go when none of these holds. A
line SHALL NOT stay highlighted after a tap on a touch screen unless the tap opened it.

#### Scenario: Popup open

- **WHEN** the user opens a route, by clicking the line or its card
- **THEN** the line is in the selected colour on a halo, drawn on top of the other lines,
  even after the pointer leaves it

#### Scenario: Popup closed

- **WHEN** the route is closed, with `← All routes`, Escape or Back
- **THEN** the line has its normal colour and opacity

#### Scenario: Tap on a touch screen

- **WHEN** the user taps a route and then taps another route
- **THEN** only the route that is open is highlighted

### Requirement: Route line weight

A route line SHALL have the weight `min(1.5 + trips * .8, 5)` px and the opacity
`min(floor + (trips - 1) * .1, ceiling)`, the floor and ceiling being the theme's
`--route-op-min` and `--route-op-max` (.8 and .95 in light, .75 and .9 in dark), so that
busy routes stand out and a single trip is still 3:1 against the land of the tiles.

#### Scenario: Single and busy routes

- **WHEN** the page draws a route with 1 trip and a route with 5 or more trips
- **THEN** the first line is 2.3 px wide at the floor, the second 5 px wide at the ceiling

### Requirement: Chain map lines

In chain mode the map SHALL draw each leg of the listed chains once, as a solid arc
with the weight of the number of chains that use it and the opacity
`min(floor + (chains - 1) * .05, ceiling)` (`--chain-op-min`, `--route-op-max`), and each
connection to another station as a dotted straight line in a second colour on a casing. Station
markers SHALL show
how many chains start and end there, and clicking one that has chains starting there
SHALL toggle the pick-up filter.

#### Scenario: Connections drawn dotted

- **WHEN** chain mode lists a chain with a 40 km connection
- **THEN** its two legs are solid arcs and the connection between the two stations is a
  dotted line

## ADDED Requirements

### Requirement: Colour themes

The map page SHALL have a light and a dark theme. Every colour of the page SHALL come
from a CSS custom property defined for `:root[data-theme=light]` and
`:root[data-theme=dark]`: no component rule, Leaflet path option or inline SVG SHALL
hold a colour value of its own. The map's colours SHALL be read from the properties
with `getComputedStyle`.

#### Scenario: One set of properties per theme

- **WHEN** the rendered page is searched for hex colours outside the property
  definitions and the favicon
- **THEN** there are none, and `data-theme` on `<html>` is `light` or `dark`

### Requirement: Native controls and dark borders

The page SHALL set `color-scheme` to the theme and SHALL carry
`<meta name="color-scheme" content="light dark">`, so native inputs, date pickers and
scrollbars follow the theme. In the dark theme a shadow SHALL be a 1 px border, or
nothing where the panel has one.

#### Scenario: Native controls

- **WHEN** the dark theme is on
- **THEN** `color-scheme` is `dark`, and the date inputs and scrollbars are drawn dark

### Requirement: Theme choice

The page SHALL offer the themes `System`, `Light` and `Dark`, `System` being the
default. A choice SHALL be saved in `localStorage['rally-map:theme']` and SHALL NOT be
written to the URL. A storage that is unavailable, or a stored value that is not one of
the three, SHALL mean `System` and SHALL NOT raise an error.

#### Scenario: Storage unavailable

- **WHEN** `localStorage` throws
- **THEN** the page follows the device setting and a choice still applies until reload

### Requirement: System theme

`System` SHALL follow `prefers-color-scheme` and SHALL change when it does, without a
reload.

#### Scenario: System changes

- **WHEN** the choice is `System` and the device switches from light to dark
- **THEN** the page and the map turn dark at once; with `Light` chosen they do not

### Requirement: Theme before the first paint

A script in `<head>` SHALL set `data-theme` before the first paint, from the saved
choice and `prefers-color-scheme`, so a dark theme never shows the light page first.

#### Scenario: Saved dark

- **WHEN** `Dark` was chosen and the page is reloaded
- **THEN** `data-theme` is `dark` before the first paint and only dark tiles are
  requested

### Requirement: Display button

The app bar SHALL end with a `Display` button showing the current theme as an icon
(a half-filled circle for `System`, a sun, a moon), with the accessible name
`Display settings: theme <choice>`. Below 700 px it SHALL show `⋯`, 44 by 44 px, in
place of the icon.

#### Scenario: Display button on a phone

- **WHEN** the page is opened 390 px wide
- **THEN** the app bar ends with a `⋯` button named `Display settings: theme system`

### Requirement: Display panel

The `Display` button SHALL open a dialog labelled `Display settings` with a `Theme`
control of three buttons with `aria-pressed`, built from one section per setting.
Choosing a theme SHALL apply it at once and leave the panel open. Escape SHALL close it
and return focus to the button; Tab SHALL stay inside while it is open. Below 700 px it
SHALL be a sheet from the bottom over a darkened page.

#### Scenario: Choose Dark

- **WHEN** the user opens the Display panel and presses `Dark`
- **THEN** the page and the map turn dark, `Dark` is pressed, the button reads
  `Display settings: theme dark` and shows a moon

#### Scenario: Close with Escape

- **WHEN** the Display panel is open and the user presses Escape
- **THEN** it closes and the Display button has focus

### Requirement: Map tiles follow the theme

The base and reference tile layers SHALL switch with the theme, between the Light Gray
and the Dark Gray canvas, in place. The reference layer SHALL stay in the pane above the
routes, and the attribution SHALL keep the Esri credit, the OSRM and OpenStreetMap
credit and the release tag.

#### Scenario: Tiles swap

- **WHEN** the theme changes from light to dark
- **THEN** the map shows the Dark Gray base and reference tiles and keeps its centre and
  zoom

### Requirement: Theme change keeps the page

A theme change SHALL keep the map view, the open route or chain, the filters, the sort
and the scroll positions. The lines, rings and badges on the map SHALL change to the
new theme's colours without being redrawn.

#### Scenario: Theme change with a route open

- **WHEN** a route is open on the map and the theme changes
- **THEN** the same route stays open and is drawn in the new theme's selected colour

#### Scenario: Theme change on the Trips view

- **WHEN** the Trips view is sorted, grouped and scrolled, and the theme changes
- **THEN** the sort, the grouping, the filters, the URL and the scroll position are the
  same

### Requirement: Theme contrast

In both themes text SHALL have a contrast of at least 4.5:1 with its background, and the
route, selected, hop and station colours of a theme at least 3:1 with the colours of the
tiles shown in that theme.

#### Scenario: Route colours on the tiles

- **WHEN** the route, selected, hop and station colours are measured against the
  dominant colours of the tile set of their theme
- **THEN** each is at least 3:1

#### Scenario: Text

- **WHEN** the visible text of the map, the Trips view, the panels and the sheets is
  measured in each theme
- **THEN** each text is at least 4.5:1 against its background

### Requirement: Map controls in the theme

The zoom and fit controls, the legend, the attribution and the tooltips SHALL use the
theme's surface, text and border colours, as the rest of the page does.

#### Scenario: Dark controls

- **WHEN** the dark theme is on
- **THEN** the zoom and fit buttons, the legend and the tooltips have the dark surface
  and light text, and the attribution is readable over the dark tiles
