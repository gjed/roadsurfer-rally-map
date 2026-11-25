# Proposal

## Why

An audit of the published page against the eleven design artboards of the redesign
(Main, MapRoute, Trips, MapChainOptions, MapChainLeg, MapChains, PhoneMap, PhoneRoute,
PhoneFilters, PhoneChains, PhoneTrips) found gaps that the four redesign PRs left open,
mostly on phones: a two-row app bar, a route view squeezed under the bars, 36 px
`Book` buttons, a chain options sheet without its backdrop and explanation, a Trips
header built for desktop, and, on desktop, a chain-mode filter bar that wraps to two
rows. It also found that opening a `#map` link focuses the map container and draws a
focus ring around it.

## What Changes

- Phone app bar on one row (logo, `Rally map`, `Map | Trips`). The `Rallies | Chains`
  switch moves into the results sheet header and the Trips header; the scan time moves
  into the filter sheet.
- Phone route or chain: the app bar and the filter bar hide, so the map fills the screen
  under the floating back button and title; the other routes and the stations dim.
- Phone `Book` buttons in the route and chain details and the chain cards are 44 px tall.
- Phone map controls: a 44 px `Fit` button only; no zoom buttons and no legend.
- Phone chain options sheet: a dark backdrop and the artboard's explanation above it.
- Phone Trips header: `N trips on M routes` with the mode switch, then `Sort` and
  `Group` selects; the column header bar goes.
- Date panel quick picks: `Any`, `This week`, `Next week`, with `aria-pressed`.
- Desktop chain mode: the chips read `Dates`, `Distance`, `Chain starts at` and
  `Return`, with accessible names that say what they filter, so the filter bar stays on
  one row; the count reads `N chains from M trips`.
- Copy from the artboards: legend entries, `Distance by road`, `Earliest` / `Latest`,
  the em dash in `Continue from`, `End near where you start`.
- The map element no longer has the id `map`, so a `#map` link never focuses it.

The agreed deviations stay: the `Same day` and rest-day defaults, every chip on phones,
no `Weekend` quick pick, the leg filter chip, the chain sort select and the fit padding.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the phone layout, the chain-mode filter bar, the legend copy and
  the map's focus on a `#map` link.

## Impact

`rally-map.template.html`, README wording and one test assertion on the legend copy.
No new dependency, no request.
