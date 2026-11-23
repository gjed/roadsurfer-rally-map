# Proposal

## Why

A rally lasts at most 7 days. A longer trip means booking several rallies one after
another, each as its own trip, and finding such a sequence by hand in a list of 800
offers is not realistic
([#8](https://github.com/gjed/roadsurfer-rally-map/issues/8)).

## What Changes

- The page gets a chain mode, switched on with a `Chains` button in the toolbar. It
  finds sequences of up to 2 or 3 rallies in the offers already on the page, with no
  extra request, and shows them on the map and in the list.
- Leg N+1 starts on the day leg N ends, or up to 0, 1 or 2 rest days later, and at the
  same station or at one within 50 or 100 km. The page shows the rest days and the
  connection distance of every hand-over.
- An offer is a window, not a fixed trip: the page books each leg for the dates that
  make the legs line up inside its window, and builds the booking link for those
  dates.
- The map draws the legs solid and the connections dashed. The list has one row per
  chain with a booking link per leg and can be sorted by start, end, total days and
  km driven. The existing date, distance, pick-up and return filters apply.
- README describes how chains work and their limits.

Out of scope: any scanner change, routing the connections, prices, booking several
legs in one step.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the chain mode of the map page.
- `site-publishing`: chains need no extra request, workflow step or data.

## Impact

- `rally-map.template.html`, README.md and the specs. The scanner, the data file and
  both workflows are unchanged, and a data file from any earlier scan works.
