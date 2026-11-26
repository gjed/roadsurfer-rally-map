# Delta for rally-scanner

## MODIFIED Requirements

### Requirement: Route line weight

A route line SHALL have the weight `min(1.5 + trips * .8, 5)` px and the opacity
`min(floor + (trips - 1) * .1, ceiling)`, the floor and ceiling being the theme's
`--route-op-min` and `--route-op-max` (.8 and .95 in light, .85 and .95 in dark), so that
busy routes stand out and a single trip is still 3:1 against the land of the tiles.

#### Scenario: Single and busy routes

- **WHEN** the page draws a route with 1 trip and a route with 5 or more trips
- **THEN** the first line is 2.3 px wide at the floor, the second 5 px wide at the ceiling

### Requirement: Chain map lines

In chain mode the map SHALL draw each leg of the listed chains once, as a solid arc
with the weight of the number of chains that use it and the opacity
`min(floor + (chains - 1) * .02, ceiling)` (`--chain-op-min`, `--route-op-max`), and each
connection to another station as a dotted straight line in a second colour on a casing. Station
markers SHALL show
how many chains start and end there, and clicking one that has chains starting there
SHALL toggle the pick-up filter.

#### Scenario: Connections drawn dotted

- **WHEN** chain mode lists a chain with a 40 km connection
- **THEN** its two legs are solid arcs and the connection between the two stations is a
  dotted line

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

#### Scenario: Accepted exceptions

- **WHEN** a one-trip line is measured on the sea of the Light Gray tiles, or the border
  of a chip or pill (`--field`) on its surface
- **THEN** they are 2.6:1 and 1.5:1 (light) or 1.7:1 (dark), below 3:1, and are accepted:
  the light route colour is 3.4:1 on that sea even at full opacity, and a chip or pill is
  named by its text
