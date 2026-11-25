# Proposal

## Why

[#44](https://github.com/gjed/roadsurfer-rally-map/issues/44): a chain can only be opened
from the list, with its `Map` button. On the map, a click on a blue leg or a dotted
connection does nothing, a click on a station filters the list although the tooltip reads
like a selection, a click on a chain row outside its buttons does nothing, and a click on
leg 2 of the selected chain clears the whole selection (only the first leg has a popup).

## What Changes

- In chain mode, a click or tap on a leg or a connection opens a popup `In N chains`. It
  lists up to 8 of the chains on the map that use it, in list order (route, dates, days,
  km); each is a button that shows the chain exactly as the list's `Map` button does.
  When more chains use it than the popup lists, `Show all N in the list` opens the list
  filtered to every chain that uses that leg or connection.
- That filter counts in `Filters (n)`, shows in the bar as `Chain uses` and over the list,
  narrows the station dropdown counts, and `Reset` clears it.
- Every part of the selected chain (its red legs, its connections and its stations)
  opens the chain popup instead of clearing the selection. Only Escape, a click on empty
  map or a change of the filters clears it.
- A click anywhere on a chain row outside its links and buttons shows the chain. Rows
  get a pointer cursor, and the row of the chain on the map is highlighted, with
  `aria-current` on its `Map` button. The `Map` button stays for keyboard users.
- The station tooltip and the legend say that a click filters: `Click to only show chains starting here`. The legend gains `click a line to pick a chain`.
- Legs and connections get a wider invisible hit area, so a finger can hit them; on a
  phone a tap on one closes the filter panel, which leaves the map a few lines tall.
- Escape closes a leg popup first and clears the chain on the second press.
- README describes it.
