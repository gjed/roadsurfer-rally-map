# Tasks

## 1. Tokens

- [x] 1.1 Light and dark tokens on `:root[data-theme=…]`, with `color-scheme`; `<meta name="color-scheme">`
- [x] 1.2 Replace every hex and `rgba` in the component rules, the inline SVGs and the JS with a token
- [x] 1.3 Shadows become 1 px borders in dark; Leaflet controls, attribution and tooltips use the tokens

## 2. Theme state

- [x] 2.1 Head script sets `data-theme` before the first paint from `localStorage['rally-map:theme']` and `prefers-color-scheme`
- [x] 2.2 `System` follows `prefers-color-scheme` live; a choice is saved in try/catch and is not in the URL
- [x] 2.3 Map colours read from the tokens; layers keep their token names and are restyled in place; no state is rebuilt
- [x] 2.4 Tile layers swap between Light Gray and Dark Gray, base and reference, without moving the view

## 3. Display menu

- [x] 3.1 `Display` button with the theme icon and `Display settings: theme <choice>` as its name
- [x] 3.2 Popover on a desktop, sheet behind a `⋯` button on a phone; dialog, labelled, Esc and focus return
- [x] 3.3 `Theme` segmented control with `aria-pressed`, in a section a language section can precede

## 4. Documentation and validation

- [x] 4.1 README wording about the basemap and the theme
- [x] 4.2 `make lint test map`, `openspec validate theme --strict`
- [x] 4.3 Browser check at 1440×900 and 390×844, light and dark: no flash, live System, state kept, tiles swapped
- [x] 4.4 Contrast measured: text 4.5:1, route, selected, hop and station colours 3:1 against the tiles of their theme
