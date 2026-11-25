# Proposal

## Why

[#45](https://github.com/gjed/roadsurfer-rally-map/issues/45): the three chain
selects are too narrow and badly placed.

- On a phone, pressing `Chains` shows nothing new: the settings sit in the filter panel,
  which stays hidden until `Filters` is tapped.
- Nobody can ask for "at least 1 rest day": no rest days means a same-day change, and
  "up to N" means the same day or later.
- Rest days stop at 2, the connection at 100 km in 3 steps, and "exactly 3 legs" does
  not exist.
- The chain settings are missing from the filter count and from `Reset`.
- There is no way to limit the length or the km of the whole chain, or to ask for a
  round trip.

## What Changes

- A "Chain options" group replaces the `Chains` fieldset: legs (2, 3, 2 or 3), a `Same day` checkbox with rest days up to 0 to 7, next pick-up within (same station, 25, 50,
  100, 150, 250 km), trip days (minimum and maximum), max total km and a round-trip
  checkbox.
- Turning `Chains` on opens the filter panel on a phone, so the options show at once. On
  a desktop the group stays first in the filter bar, on one row.
- The options count in `Filters (n)` and `Reset` restores them.
- The search reads the new options. It is faster than before (about 3 times) so that
  the wider ranges stay usable on a real scan.
- The empty-state hints suggest relaxing the new options.
- README describes the options.
