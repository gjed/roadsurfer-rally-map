# Design

## Decisions

- **Mode switch on phones.** PhoneMap puts `Rallies | Chains` in the results sheet
  header, and PhoneTrips shows no switch at all. A phone user still needs to switch on
  the Trips page, so the same switch sits in the Trips header next to the count. It is
  rendered with the lists (`.pmode`, `data-mode`) and shown only below 700 px; the app
  bar's switch is hidden there. The route and chain sort selects in the sheet header
  are hidden on phones, as in PhoneMap; the Trips view keeps its `Sort` select.
- **Scan time on phones.** The app bar has no room for it. It moves to the bottom of
  the filter sheet as `Offers as of the scan of 23 Nov, 22:56 UTC`, the place a user
  looks when they wonder how fresh the trips are. The desktop tooltip with the request
  counts stays desktop-only.
- **Route or chain open on phones.** `body.detail` hides the app bar and the filter bar,
  as in PhoneRoute. `pill()` toggles the class and calls `map.invalidateSize()` at once,
  so the fit that follows uses the full-screen size rather than waiting for the
  ResizeObserver. Station markers carry the class `stn`, and `#map.dim path.stn` dims
  them on phones only; the desktop MapRoute artboard keeps them.
- **Phone Trips header.** PhoneTrips has one row: the count and `Sort`. With the mode
  switch it needs two short rows: the count and the switch, then `Sort` and `Group`
  as selects. Group by stays reachable without its segmented control, and the column
  header bar goes, since `Sort` covers start, end and distance in both directions.
- **Short chip names in chain mode.** The design keeps `Dates`, `Distance` and
  `Return` and renames only the pick-up chip. Each chip's visible name is
  `aria-hidden` and a visually hidden name says what it filters (`First pick-up date`,
  `Distance per leg`, `Chain ends at`); the panel headings and the `×` labels use the
  long names. At 1440 px the bar stays one row; the `Chain uses` chip, when a leg is
  picked, may still wrap the bar.
- **Count source.** `from M trips` is the number of offers the chains are built from:
  the offers that pass the distance filter, the input of `findChains()`.
- **`#map` focus.** Chrome focuses the element whose id matches the URL fragment when a
  fragment navigation happens (a `#map` link, Back to `#map`), and the map container
  is focusable, so it got a focus ring. The element's id becomes `rmap`; the hash
  routes stay `#map` and `#trips`.
- **Phone legend.** The legend is hidden on phones, as in PhoneMap; the line weights,
  the orange selection and the dotted hops read without it, and the `~` estimate mark
  is spelled out in the route detail and the Trips footer.
