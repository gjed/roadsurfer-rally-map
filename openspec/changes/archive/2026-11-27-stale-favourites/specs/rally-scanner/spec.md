# Delta for rally-scanner

## ADDED Requirements

### Requirement: Stale favourites

A favourite whose route is not in the scan, whose station has no departure in it, or one
of whose chain's routes is missing SHALL stay in the storage but SHALL NOT count: the
`Favourites` chip, its filter, the phone switch and the empty states SHALL take only the
favourites that exist in the current data into account.

#### Scenario: Only a stale favourite

- **WHEN** the only stored favourite is a route that the scan does not have
- **THEN** the filter bar has no `Favourites` chip and the phone switch is disabled

#### Scenario: Stale and present favourites

- **WHEN** a stale favourite is stored and the user stars one route of the scan
- **THEN** one favourite counts, the chip shows, and the stale entry is still in the storage
