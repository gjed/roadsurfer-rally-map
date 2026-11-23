# Spec Delta

## MODIFIED Requirements

### Requirement: Estimate labels and credit

The page SHALL show a routed distance as road km, without `~`. A distance that is
estimated, because `km_estimated` is true or `km` is missing, SHALL carry a leading `~`
and be labelled as an estimate in the popup, the tooltip and the list, and the map
legend SHALL explain `~` while the page has such a distance. When the page shows a
routed distance it SHALL credit OSRM and OpenStreetMap contributors in the map's
attribution control. The page SHALL have no footer for either.

#### Scenario: Routed route

- **WHEN** the user opens the popup of a route whose records have `km` 1321 and
  `km_estimated` `false`
- **THEN** the popup shows `1321 km by road`, with no `~`, and the map attribution
  credits OSRM and OpenStreetMap contributors

#### Scenario: Estimated route

- **WHEN** the user opens the popup of a route whose records have `km_estimated` true
  or no `km`
- **THEN** the popup and the tooltip show `~N km (estimated)`, the list row shows `~N`,
  and the legend says that `~` marks an estimate

#### Scenario: No footer

- **WHEN** the page is opened at 1280 px or 375 px wide
- **THEN** the page has no footer element and the attribution shows the credit

### Requirement: Map legend

The map SHALL show a legend that the user can collapse, with a one-trip line, a
five-or-more-trips line at their drawn weights and opacities, the highlighted route
and a station marker, worded `1 trip on this route`, `5 or more trips`,
`selected route` and `station: click for trips from here`. While the page has an
estimated distance, it SHALL add a fifth entry, `~ estimated distance, not routed`.
It SHALL start open at desktop widths and collapsed below 700 px.

#### Scenario: Reading the map

- **WHEN** the page is opened 1280 px wide with routed distances only
- **THEN** the legend shows the four samples with those labels and no explanation of
  the arc direction

#### Scenario: Estimates on the page

- **WHEN** the page is opened with at least one estimated distance
- **THEN** the legend also shows `~ estimated distance, not routed`
