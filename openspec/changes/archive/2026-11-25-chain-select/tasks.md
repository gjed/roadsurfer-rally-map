# Tasks

## 1. Pick a chain on the map

- [x] 1.1 Wide transparent hit lines for legs and connections; the thin lines stay as they are
- [x] 1.2 `In N chains` popup on a leg or a connection: up to 8 chains in list order, each a button that shows the chain
- [x] 1.3 `Show all N in the list` past 8: the list filtered to the chains that use the leg or connection
- [x] 1.4 The leg filter counts in `Filters (n)`, shows in the bar and over the list, and `Reset` and `Clear` remove it
- [x] 1.5 The tooltip count matches the popup; phone: a tap closes the filter panel

## 2. The selected chain stays

- [x] 2.1 Every red leg, connection and station opens the chain popup and keeps the click from the map
- [x] 2.2 Only Escape, a click on empty map or a filter change clears the selection; the first Escape closes a leg popup

## 3. List rows

- [x] 3.1 A click on a chain row outside its links and buttons shows the chain
- [x] 3.2 Pointer cursor; the row of the chain on the map is highlighted with `aria-current`

## 4. Copy, docs and tests

- [x] 4.1 Station tooltip and legend: `Click to only show ... here`
- [x] 4.2 README describes the chain popups, the row click and the leg filter
- [x] 4.3 Test that the rendered page has the new markup
- [x] 4.4 Check on a real scan at 1280 px and 375 px with mouse and taps, and with the keyboard
