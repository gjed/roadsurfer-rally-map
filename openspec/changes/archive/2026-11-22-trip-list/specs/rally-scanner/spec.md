# Spec Delta

## ADDED Requirements

### Requirement: Trip list view

The map page SHALL offer a list view, selected with a toggle in the toolbar, with one
row per trip that passes the active filters. The list SHALL use the same filter check
as the map, so its row count equals the trip count in the toolbar, and switching
views SHALL keep every filter selection.

#### Scenario: Filtered list

- **WHEN** the user picks a pick-up country and a distance range and switches to the
  list
- **THEN** the list has as many rows as the trip count in the toolbar, and switching
  back to the map keeps both filters

### Requirement: Trip list columns

Each list row SHALL show the start date, end date, pick-up station and country,
return station and country, estimated road distance, the price when the page has
prices, and a booking link that opens in a new tab. Every value from the API SHALL
be escaped before it is inserted as HTML.

#### Scenario: Booking from the list

- **WHEN** the user clicks the booking link of a row
- **THEN** the trip's booking URL opens in a new tab and the view does not change

### Requirement: Trip list sorting

Rows SHALL be sorted by start date by default and SHALL be re-sortable by start date
and by distance from the column headers.

#### Scenario: Sort by distance

- **WHEN** the user clicks the distance header in the list
- **THEN** the rows are ordered by distance, and a second click reverses the order

### Requirement: Trip list selection

Selecting a row SHALL show that route on the map with its popup open.

#### Scenario: Row selection

- **WHEN** the user selects a row outside its booking link
- **THEN** the page shows the map zoomed to that route with the route's popup open
