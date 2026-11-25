# Design

## Decisions

- **N counts the chains on the map.** The overview is built from the first 200 chains, so
  a leg's weight, its tooltip and the popup all count the same chains, and every chain the
  popup lists is also on the map and in the list. While the toolbar reads `Showing 200 of N chains`, the heading and the tooltip add `on the map`. `Show all N in the list` counts
  every chain that passes the filters, so it is shown only when that total is more than the
  popup lists (more than 8, or more than are on the map).
- **The popup lists chains in list order** (`chains` after the sort), so the first rows
  are the ones the list and the map show first. It is built when it opens, so it follows
  the current sort and filters. Each row has two lines, the stations of the chain and its
  dates, days and km, because eight rows of dates cannot be told apart. The selected chain,
  if listed, is marked `aria-current` and tinted like its list row. Only the rows scroll.
- **The leg filter is one more filter.** `Show all N in the list` sets `legFilter` and
  shows the list. It is part of `endsPass`, next to the pick-up and return filters, so the
  chain list, the map and the station dropdown counts all follow it. It sits in the filter
  bar as a `Chain uses` group with a `×` button (counted in `Filters (n)`) and as a line
  with `Show all chains` over the list, which is what a phone shows, its panel being
  closed. `Reset`, `×`, `Show all chains` and switching between chains and trips clear it;
  station clicks and the other filters keep it. When no chain is left, `remove the leg filter` is the first hint. Focus goes to the list caption.
- **One key for a leg and for a connection.** A leg is `from>to`; a connection is
  `hop from>to` (the station the chain returns at and the next pick-up). A chain uses a
  connection only when its hand-over is by another station.
- **A wide invisible line carries the click.** The thin lines are 1 to 4 px wide and a
  dotted connection only reacts on its dots, so nobody hits them with a finger. Each leg
  and connection gets a transparent line 16 px wide (22 px with a coarse pointer) on top
  that holds the popup, the tooltip and the click, with `bubblingMouseEvents` off so a
  click does not also reach the map. The visible lines are not interactive and are dimmed
  through a class. Busy legs are drawn last, so they are on top where legs cross. While a
  popup is open its line is raised.
- **A tap on a line closes the phone's filter panel.** In chain mode on a phone the
  panel opens by itself and leaves a map 189 px tall; a popup does not fit in it.
- **The selected chain opens its popup everywhere.** Its legs, connections and stations
  each bind the chain popup, with a tooltip, instead of being non-interactive: a
  non-interactive part would let the click through to the dimmed blue line or station
  below, which opens an unrelated popup or sets a filter and clears the chain. Clicks on
  them never reach the map, so only Escape, a click on empty map or a filter change clears
  the chain. A blue leg clicked while a chain is selected opens its `In N chains` popup
  and keeps the selection until a chain is chosen.
- **The popup is bound to each part, not once to the group,** so every part keeps its own
  tooltip; the behaviour is the same.
- **Escape closes the leg popup first.** Escape in an `In N chains` popup, or anywhere on
  the page while one is open, only closes it; the next Escape clears the chain. Escape in
  the chain popup still clears the chain. After a mouse choice in a leg popup, focus goes
  to the map so that Escape works; after a keyboard choice it goes to the first `Book`
  link, and Escape then focuses the map, since there is no list row to return to.
- **Row click ignores links, buttons, rows without chains and a text selection.** Dragging
  to select text in a row must not jump to the map. Trip rows are left as they are: the
  issue is about chains. The pointer cursor is set in chain mode only.
- **Row highlight:** a tint and a 3 px bar on the left, so it does not rely on colour
  alone, and `aria-current="true"` on the row's `Map` button, not on the `tr`, which
  screen readers often skip. Switching to the list scrolls the row into view.
- **Copy:** the station tooltip and the legend say that a click filters, and what a
  second click does: `Click to show chains starting anywhere`, `Click to show trips from every station`.
- **No keyboard route to the leg popups or the leg filter.** Map lines stay out of the tab
  order, as the list view is the keyboard route to every chain; the leg filter is reached
  with a pointer only.
