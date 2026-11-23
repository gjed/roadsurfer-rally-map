# Tasks

## 1. Page

- [x] 1.1 Add `findChains`, a pure function: the pick-up and return day pairs inside
  each window, the rest-day and connection rules, the best dates per chain.
- [x] 1.2 Add the `Chains` toolbar button and the legs, rest days and connection
  controls; apply the date, distance, pick-up and return filters to chains.
- [x] 1.3 Draw the listed chains on the map: legs solid, connections dashed, the
  chain opened from the list on top with a popup of per-leg booking links.
- [x] 1.4 List the chains with a booking link per leg, rest days and connection
  distance, sortable by start, end, days and km driven, on desktop and on a phone.
- [x] 1.5 Build the per-leg booking link by replacing the two dates in the record's
  link; show the connection entry in the legend.

## 2. Docs

- [x] 2.1 README: how chains work and their limits.
- [x] 2.2 Spec deltas for `rally-scanner` and `site-publishing`.

## 3. Checks

- [x] 3.1 On a real scan: chain counts for 0, 1 and 2 rest days with 0, 50 and 100 km;
  0 and 0 gives only same-station same-day hand-overs and raising either only adds
  chains.
- [x] 3.2 One real chain checked by hand on the booking pages, both legs.
- [x] 3.3 Headless browser at 1280 px and 375 px, and the computation time on the full
  data.
