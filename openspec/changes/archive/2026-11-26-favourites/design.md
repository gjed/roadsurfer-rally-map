# Design

## Differences from issue #60

The designer review of the page overrides these parts of the issue and of the first
draft of this change:

- The word is `Favourites` everywhere, not `Starred`. A `Starred` choice in the Trips
  `Group by` is dropped: favourites come first in every Trips grouping instead.
- A station is a favourite as a pick-up station, since the feeds are per pick-up: it
  applies to the routes that leave it, not to those that arrive. There is no station
  button in the Return panel.
- The station button is not on the filter chips (too many targets in a 36 px pill). It is
  in the heading of the lists and in the Pick-up panel, with the feed link.
- The station tooltip cannot hold a control, so it only shows the state (a `★` before the
  name). It holds no feed text, which the issue asked for.
- The feed link reads `RSS feed`, never `Atom`, and opens in a new tab.
- The `New` badge is on windows (route detail, Trips rows, a count on route cards) and not
  on chains, whose key fixes their dates.
- The `Favourites` chip is hidden while nothing is a favourite.

## Keys

Keys come from data the page already has and stay the same from scan to scan.

- Route: `routeKey()`, `from.name>to.name`.
- Station: `place()`, `Name, CC`, the pick-up station. The offers carry no station id, so
  a station that the API renames, or whose country changes, drops out of the favourites:
  an accepted limit. The page's own station filter is keyed by name alone, so two stations
  with the same name share one filter; a button and a feed link follow the station the
  page holds for that name.
- Chain: the key `findChains()` gives it, the route keys of its legs joined by `|`. It
  holds no dates and no leg choice, so it is the same in every scan. A favourite chain
  stays a favourite when the current chain options do not produce it; it then does not
  show. `findChains()` is unchanged.

## Storage

`localStorage['rally-map:fav']`, read and written inside `try`/`catch` like the theme
and language keys. Shape:

```json
{"v": 1,
 "route":   {"Munich>Bordeaux": {"seen": ["Munich>Bordeaux|2026-11-24|2026-12-01"], "scan": "2026-11-26T03:12:05Z"}},
 "station": {"Munich, DE": {"seen": [], "scan": ""}},
 "chain":   {"Munich>Bordeaux|Bordeaux>Lisbon": {"seen": [], "scan": ""}}}
```

- A bad value, a wrong shape or a throwing storage gives no favourites; the page then
  works in memory for the visit and shows no error.
- `v` is the version. A page that finds a `v` it does not know reads nothing and never
  writes, so an older page cannot overwrite what a later one saved. A later change that
  needs a new shape migrates from `v: 1`.
- In memory the three kinds are `Map`s, so a station called `__proto__` is harmless.
- Two tabs: a change in one tab reaches the others through the `storage` event, which
  reloads their in-memory favourites, so a write never brings back what another tab
  removed. Favourites are per browser, with no sync between browsers.
- The favourites filter itself is not stored and not in the URL: it is personal, and a
  shared link must not show the reader a different set of trips than the sender saw.

## Buttons

`.fav` is the star alone and `.favt` the star with the word `Favourite`; both are
`<button aria-pressed>`. The name is `Favourite: <item>` and never changes with the state.
The icon is an inline stroke SVG, `aria-hidden`, an outline when off and filled with
`--fav` when on, so the shape carries the state.

Cards of the route list and the chain list are one `<button>`, and a button cannot hold
a button, so the star is a sibling in the list item over the card's corner. Hover and the
route highlight belong to the item, so the pointer on the star does not end them.

Pressing a button changes the buttons in place where it can (an open route or chain);
otherwise the page is drawn again and the scroll positions and the focus are put back. If
the item is gone (un-starred under the filter) the focus goes to the next item's star or
to the list heading.

## Filter, groups, empty states

- Trips mode: an offer passes when its route is a favourite or it leaves a favourite
  station. Chain mode: a chain passes when it is a favourite. A favourite chain the
  current options do not make is not shown.
- The chip is not a popover: it toggles, counts, and is cleared by `Clear all` and
  `Reset`. It is hidden while nothing is a favourite and the filter is off, so the bar
  does not wrap at 1024 px. On a phone the chip row starts with `Filters` and the chip.
- The phone sheet starts with the switch; without a favourite it is disabled and a hint
  says how to make one.
- Route list: while the filter is off, favourite routes move (not copy) to the top under
  a `Favourites` header row, the rest under `All routes`; no headers while the filter is
  on. Trips: favourite trips first under their own header, or the groups that have a
  favourite first with a filled star in their header.
- Empty: nothing is a favourite (with `Show all`), favourites without trips under the
  other filters, no favourite chain that fits the options.

## New since the last visit

- A window is `routeKey|start|end`. The windows of an item are those of its route, of the
  routes of its legs, or of the routes that leave its station.
- When an item is starred its current windows are stored as seen, so a new favourite
  starts with nothing new.
- On load every stored item is compared with the page's data: a window that is not in
  `seen` is new. The chip counts the windows that are new on any item, each once. A route
  card (as a count), a window of the route detail and a Trips row carry a solid badge.
  Chains carry none.
- Opening a route, an open chain or a chosen pick-up station stores its windows as seen
  in every favourite that has them, so a badge never stays on a window that was just
  shown. The badge shows on the render that opens it and goes with the next one.
- `scan` is `SCAN.finished_at`, stored with the seen windows and shown in the badge's
  `title`. The logic works on the offer keys alone, so a page without a scan time still
  marks new windows; its stored `scan` is empty.
- Windows whose end date is before today (UTC) are removed from `seen` on load, so
  storage is bounded by the windows that can still be booked. A window that vanished
  and comes back inside its dates is not new again: accepted, the keys are not removed
  when a scan lacks them, as a narrow scan would otherwise make everything else new.

## The feed table

`render()` embeds the table in a second placeholder, `/*FEEDS*/null`, as a list of
`[name, cc, slug]` computed by `station_slugs()` on the same stations `write_feeds()`
uses (the scan's station list plus those of the offers; one function gives both), so
names and files cannot drift. `/*SCAN*/` keeps its meaning. The page links
`feeds/from-<slug>.xml`, relative like the `all.xml` link of the page head. A test
renders the fixture with `--map` and `--feeds` and checks that every embedded slug has
its file.

## Colours

New tokens in both themes: `--fav` (amber, `#A16207` on light, `#FACC15` on dark) and
`--new-bg`/`--new-fg` (green with white, `#15803D`/`#FFFFFF`, and on dark `#4ADE80`/`#0B1220`).
Orange is not used: it means `selected` on this page, and `--fresh` is not reused.
