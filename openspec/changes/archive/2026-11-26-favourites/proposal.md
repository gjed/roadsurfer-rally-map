# Proposal

## Why

A visitor who cares about a few routes, a pick-up station or a chain (for example
Munich → anywhere) has to filter the whole map on every visit and cannot tell what
changed since the last one. Issue #60 asks for favourites that live only in the browser
and for a "New" mark on what appeared since the last visit, plus a feed link per
station now that #61 publishes the feeds.

## What Changes

- A favourite button (a real `<button aria-pressed>` with a catalog name, in two forms:
  the star alone and the star with the word `Favourite`) on route cards and the route
  detail, chain cards and the open chain, Trips rows (a first column) and chain cards, and
  for a pick-up station in the heading of the lists and the Pick-up panel.
- The favourites are saved in `localStorage['rally-map:fav']` as versioned JSON, never in
  the URL hash. A route is its `routeKey()`, a station its `Name, CC`, a chain its key
  (the route keys of its legs, in order).
- A `Favourites` chip in the filter bar (hidden until something is a favourite) and a
  switch at the top of the phone filter sheet show only favourites: routes that are
  favourites or leave a favourite station, and favourite chains. It counts in
  `Filters · n`; `Clear all` and `Reset` switch it off and never remove a favourite. The
  route list gets `Favourites` and `All routes` header rows and the Trips table lists
  favourite trips first.
- New since the last visit: per favourite the page stores the offer keys (route, start,
  end) it has shown and the scan time. A window that was not stored gets a solid `New`
  badge (route detail, Trips rows, a count on route cards), and the chip shows how many
  there are. Opening the item (a route, a chain or a chosen pick-up station) stores its
  windows as seen. Windows that ended before today (UTC) are dropped from storage.
- A `RSS feed` link for a pick-up station, pointing to `feeds/from-<slug>.xml`. The
  scanner embeds the station-to-slug table that `--feeds` uses in the page, so the page
  does not repeat the slug rule; a station without an entry shows no link.
- Every new text is in the catalog, in all seven languages.

Out of scope: sync between browsers or an account, notifications, favourites in the
URL, a star on the map's route lines, feed links for return stations or chains.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: Clear all and the Filters chip count, and new requirements for the feed
  table in the page, the favourite buttons, the favourites filter, the favourites first
  in the route list and in Trips, the new-window mark and the station feed link.
