# Tasks

## 1. Shell

- [x] 1.1 App bar: brand, `Map | Trips` views, `Single rallies | Chains` switch, scan time with its tooltip
- [x] 1.2 Filter chips with popovers (Esc, outside click, Tab trap, focus return), `×` per active chip, `Clear all`
- [x] 1.3 Move the chain options fieldset into the `Chain options` chip's panel; open it on a phone when `Chains` is pressed

## 2. Map view

- [x] 2.1 Sidebar route list: one card per route, sort select, card and arc hover linked
- [x] 2.2 Route detail: stats, trip windows with `Book`, `Continue from`, `Also from`, `Show these trips in the list`
- [x] 2.3 Chain list and chain detail in the sidebar; numbered legs on the map
- [x] 2.4 Station hit area and tooltips; fit control; route halo and dimming

## 3. Trips view

- [x] 3.1 Trips table: sort by start, end, distance; group by route or pick-up; `Map` opens the route
- [x] 3.2 Chain cards with `Book leg N` and `Map`

## 4. State

- [x] 4.1 Hash state with replaceState for filters and pushState for views and details; invalid values ignored
- [x] 4.2 Back, Escape and `← All routes` close a detail and restore focus

## 5. Documentation and validation

- [x] 5.1 README "Run it locally" and "Chains"
- [x] 5.2 `make lint test map`, `openspec validate ux-shell --strict`
- [x] 5.3 Browser check at 1440×900 and 390×844, real scan and empty scan, both views
