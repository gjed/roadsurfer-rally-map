# Design

## Context

An offer record has a start, an end, the two stations with coordinates and a booking
link. All offers in the data are 7 days long, and a route has a new window almost
every day, so windows of one route overlap. The booking page treats the window as a
range: on a real route with the window 14 to 21 December it showed one offer, at the
flat price, for 14 to 18, for 15 to 21 and for 14 to 15, and no offer for 14 to 22.
Chains must use that, because with fixed 7-day trips two legs rarely meet.

The page already has every offer, so chains are computed in the browser from the
embedded records. `release.yml` and `--from-json` stay offline and nothing is added to
the data file.

## Goals / Non-Goals

**Goals:**

- Chains of 2 or 3 legs with rest days (0 to 2) and connections (0, 50, 100 km).
- Dates and booking links that the booking page accepts.
- A computation that stays interactive on the full data.

**Non-Goals:**

- Routing the connections, prices, a different scanner, booking several legs at once.

## Decisions

- **A leg is a pick-up day p and a return day q inside one window**, with
  `start <= p < q <= end` and `q - p <= 7`. Leg N+1 needs
  `q <= p' <= q + rest days`. A pair is only valid inside a single window: it never
  joins the end of one window to the start of another.
- **Only days the data shows are used.** A day counts when some offer starts or ends
  on it. This skips Sundays and 25 and 26 December without a calendar: the booking
  page answered "no rallies" for a leg that began on a Sunday inside its window. A
  day nobody shows is dropped, so the page may miss a chain, but it does not offer a
  date the booking page rejects. The booking page has the last word: stations have
  their own opening hours that the data does not carry.
- **One itinerary per chain, the best one.** A chain is a sequence of routes (and the
  connections between them). Among all dates that fit, the page keeps the one with the
  most nights on the road, then the fewest rest days, then the earliest start. Nights
  first because a leg costs the same however long it is. "Total days" is the span from
  the first pick-up to the last return, rest days included.
- **One row per route sequence, not per date combination.** Because windows slide
  daily, the same stations repeat with different dates: the strictest settings give
  2075 route sequences but 5367 date variants of them on the real data. Listing
  variants would bury the list. The start date filter and the week slider choose
  which dates the best itinerary is looked up in: they limit the first pick-up day.
- **No station is a pick-up twice in a chain.** It cuts A to B, B to A, A to B
  loops, which are not a way to travel further.
- **The default is 2 legs, no rest days, same station;** legs (2 or 3), rest days and
  connection are selectable. The strictest setting shows what exists without any
  stretching; 3 legs multiply the results (about 10 000 chains on the real data
  against 2 000) and the cost of a render.
- **Connections use the straight line × 1.3, shown with `~`.** The alternative was to
  route the connection pairs in the scanner through the OSRM cache and store them
  under a new top-level key. It was not done: the connection is a hop by train or bus
  (or a lift) with no van, so its exact road length does not matter, only whether it
  is near; 50 and 100 km are coarse thresholds next to the difference between a road
  and the estimate; the scanner would send about 70 more routing requests on the first
  run and need a new key, tests and a fallback for every older data file anyway; and
  the page would still need the estimate for those files. The page already labels the
  estimate with `~` and a note. The legs' distances keep using the routed `km` when
  the record has it.
- **Filters.** The date filter limits the first pick-up day. The distance filter
  limits every leg, as it limits a trip. The pick-up filters apply to where the
  chain starts and the return filters to where it ends; stations in between are not
  filtered. The dropdown options count chains.
- **Connections are dotted, on a white casing.** A dashed line one pixel thick vanishes
  among 200 legs at overview zoom, and dotted reads as "not driven". The chain opened
  from the list gets numbered badges on its legs, its own stations drawn again over the
  dimmed map, and a popup above it, with the chain fitted below the popup.
- **The list and the map show the same first 200 chains**, in the sort order, and the
  toolbar counts all of them. The real data has thousands of chains and an unbounded
  table is slow on a phone, while a map of all of them is a solid blue blob. Sorting
  or filtering changes which 200 are shown.
- **The booking link replaces the two dates in the record's link.** `link()` in the
  scanner builds `station`, `end_station`, `start-date`, `end-date`, `currency` in that
  order; the page sets the two date parameters of the record's own link, which keeps
  the station ids (the records carry none) and the order. For a full window the result
  equals the record's link.
- **Ranking.** The default order is most total days, then least driving. The columns
  start, end, days and km driven can be sorted. km driven is the sum of the legs'
  distances, without the connections.
- **`findChains` is a pure function** that takes the offers, the set of open days and
  the options, and touches nothing else, so its rules can be checked on a real data
  file in a browser or in Node.

## Risks / Trade-offs

- Dates are inferred from the data: the booking page may refuse a leg the page
  proposes (a station closed that day), and a booking can change while the page is
  old. The page links to the booking page; it does not reserve anything.
- Two legs on one account are booked one after another. The maintainer settled that
  this does not matter.
- The best itinerary hides other dates of the same chain; narrowing the dates shows
  them.
