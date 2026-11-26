# Tasks

## 1. Feed table in the page

- [x] 1.1 `feed_stations()` gives the stations and their records for `write_feeds()` and `render()`; `render()` embeds `[name, cc, slug]` for them in `/*FEEDS*/null`
- [x] 1.2 Unit test: render the fixture with `--map` and `--feeds`; every embedded slug has its file; a duplicate-name station gets the file of its own country

## 2. Favourites

- [ ] 2.1 Storage: versioned JSON in `rally-map:fav`, guarded reads and writes, sanitised on load, expired windows dropped, unknown version never written
- [ ] 2.2 Favourite buttons (`.fav` and `.favt`), the `--fav`, `--new-bg` and `--new-fg` tokens, buttons on route cards, route detail, chain cards, open chain, Trips rows and chain cards, and the station controls in the list heading and the Pick-up panel
- [ ] 2.3 `Favourites` chip, phone sheet switch, filter in `passes()` and `endsPass()`, `Filters · n`, `Clear all`/`Reset`, empty states
- [ ] 2.4 `Favourites` header rows in the route list, favourites first in Trips
- [ ] 2.5 New windows: seen sets per item, `New` badges and counts, the chip count, marking seen on open
- [ ] 2.6 `RSS feed` link in the station heading and the Pick-up panel, hidden without an entry; the station tooltip shows the state
- [ ] 2.7 Catalog: every new text in the seven languages

## 3. Documentation and validation

- [ ] 3.1 README note on favourites and the station feed link
- [ ] 3.2 `make lint test map`, `openspec validate favourites --strict`
- [ ] 3.3 Browser check at 1440×900, 390×844 and 360×740, light and dark, English and German: stars from every place, persistence, the filter and its count, new windows from a second synthetic scan, throwing storage, the empty state, the feed links, state kept on starring, accessible names
