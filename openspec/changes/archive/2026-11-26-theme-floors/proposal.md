# Proposal

## Why

The review of the `theme` change (PR #58) raised two points on the route opacity floors
it added for issue #57. A one-trip line in dark is 2.8:1 on the lighter dark land of zoom
9 and beyond, below the 3:1 the issue asks for. And the chain ramp, which steps by .05,
reaches its ceiling at 4 chains, so opacity stops carrying the count and a dense overview
is nearly opaque.

## What Changes

- Dark route and chain opacity floors rise to .85 and the ceiling to .95, so a one-trip
  line is at least 3.1:1 on every dark land colour sampled. Light is unchanged.
- The chain ramp steps by .02, so it reaches its ceiling at about 8 chains (6 in dark), and
  the chain line weight is capped at 3 px instead of 4, growing by .2 per chain so it still
  separates legs up to the 10 chains of the legend, and a dense overview stays legible.
  The comment that said chain lines are fainter is corrected.
- Two exceptions to the 3:1 criterion of #57 are recorded as accepted, with their reasons:
  a one-trip line on the sea of the light tiles (2.6:1) and the borders of chips and pills
  (1.5:1 light, 1.7:1 dark).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the opacity of route and chain lines, and the theme contrast
  requirement.
