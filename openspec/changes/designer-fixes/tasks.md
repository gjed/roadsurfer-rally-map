# Tasks

## 1. Map

- [x] 1.1 Draw one station marker per station in its own pane, after the route loop; click sets the pick-up filter; tooltip shows departures and arrivals
- [x] 1.2 Highlight a route on hover and while its popup is open, draw it on top, reset on mouseout and popupclose
- [x] 1.3 Route weight `min(1.5 + trips * .7, 5)`, opacity .4
- [x] 1.4 Fit the first view to the drawn layers
- [x] 1.5 Legend: matching line weights, one station entry, arc direction
- [x] 1.6 Move the release tag into the attribution control and drop the footer

## 2. List and touch

- [x] 2.1 Per-row `map` button with `aria-label`; drop row `tabindex`, pointer cursor and the Enter handler
- [x] 2.2 Escape in a popup opened from the list returns to the list with focus on its button
- [x] 2.3 Coarse-pointer padding and negative margins on booking links and the map button
- [x] 2.4 `MM-DD` dates under 700 px with the full date in `title`
- [x] 2.5 List width, right-aligned `km` header, sticky header edge

## 3. Toolbar

- [x] 3.1 Selects take a full row at 700 px and below
- [x] 3.2 Filters and Reset in one row at 1280 px
- [x] 3.3 Week slider resets when dates are typed
- [x] 3.4 Short title below 700 px

## 4. Documentation and specs

- [x] 4.1 README: legend, list rows, release tag, `--release` help
- [x] 4.2 `--release` help string and `scan.yml` comment

## 5. Validation

- [x] 5.1 `make lint test map`, `openspec validate --strict --all`, the pr-check page checks
- [x] 5.2 Browser check at 1280 px and 375 px against the acceptance items of #38
