# Tasks

## 1. Options

- [x] 1.1 `Chain options` fieldset: legs, same day, rest days 0 to 7 (select), next pick-up distance, trip days, max km, round trip
- [x] 1.2 `findChains` takes legs, break, trip days, km and round-trip options; every option is in the memo key
- [x] 1.3 Search speed: index pairs by pick-up day, build itineraries lazily, keep one itinerary on the last leg
- [x] 1.4 Empty-state hints and the table caption read the new options

## 2. Filter integration

- [x] 2.1 `gchain` in `GROUPS`, counted only in chain mode; `Reset` restores every option
- [x] 2.2 Turning `Chains` on opens the filter panel on a phone
- [x] 2.3 Desktop: the group stays first and on one row; phone: one control per row
- [x] 2.4 Design pass: tab order, `Same day or up to N rest days`, 44 px targets, hints capped at two

## 3. Docs and tests

- [x] 3.1 README describes the options
- [x] 3.2 Test that the rendered page has the controls
- [x] 3.3 Check on a real scan at 375 px and on desktop: rest days, trip days, km, round trip, Reset, search time
