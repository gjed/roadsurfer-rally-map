# Proposal

## Why

The favourites change (PR #64) keeps a favourite in storage when the scan no longer has
it: a route with no windows this time, a station with no departure, a chain with a missing
route, or a station the API renamed. Such a favourite still counts, so the `Favourites`
chip stays visible, the phone switch is enabled, and the filtered list says none of your
favourites have trips. Nothing on the page shows the entry, so it can't be un-starred.
Issue #65.

## What Changes

- A favourite counts only while the current data has it: a route in the scan, a station
  with at least one departure, a chain whose every route is in the scan.
- The chip's visibility, the phone switch and its hint, and the empty states use that
  count.
- Stale favourites stay in storage, so a route that comes back in a later scan is a
  favourite again.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: adds the requirement "Stale favourites".

## Impact

`rally-map.template.html` only: a `present()` check and an `nFav()` count replace the
three storage-size sums in `syncFav()` and `hasStars()`.
