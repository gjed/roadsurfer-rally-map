# Design

## Decisions

- **Rest days are a select of 0 to 7.** The issue allowed a number field or a stepper. A
  select has eight fixed values, uses the phone's own picker and has nothing to validate.
  With `Same day` off, option 0 is disabled and a 0 becomes 1.
- **One sentence.** The checkbox and the rest days read `Same day or up to N rest days`
  checked, and `Same day 1 to N rest days` unchecked; only the connecting phrase
  changes. The select keeps one accessible name, `Most rest days between legs`.
- **The group is first in the DOM,** not only on screen, so the tab order follows what
  the user sees. The accent border marks a changed group, as in the other groups; a
  changed checkbox colours its label.
- **Why the panel opens instead of an `Options` button.** The top row at 375 px is full
  (`Filters`, `Chains`, `List`, and `Reset` when it shows); a second toggle for the same
  panel would wrap it. On a phone `Chains` opens the panel and scrolls it to the top.
  Focus does not move.
- **Hints:** at most two, in a fixed order, so the empty state stays one short line.
- **Phone layout:** two columns, label and control; the `Same day` row and `Round trip`
  span both; the two trip-day fields share the second column. Selects, number fields
  and checkbox labels are 44 px tall.
- **Phone: open the filter panel.** Turning `Chains` on opens the panel (`body.filt`,
  `aria-expanded` on `Filters`) instead of adding an `Options` button. One disclosure
  mechanism stays, the options are the first group so they show without scrolling, and
  no second button or state is needed. Turning `Chains` off leaves the panel as it is:
  the user may have opened it for the filters. On a desktop the panel is always shown.
- **Break semantics.** `Same day` on with N rest days is a break of 0..N days; off it is
  1..N. Unchecking `Same day` with 0 rest days sets the field to 1, and the search never
  uses less than 1 in that state. The break applies to every hand-over, not to the chain
  in total.
- **Legs: 2, 3, 2 or 3; no 4.** On a real scan (781 offers), 3 legs with 250 km and 7
  rest days already finds about 210,000 chains. A fourth leg multiplies that and cannot
  stay near 300 ms.
- **Trip days and km are limits inside the search, not a filter afterwards.** The chain
  keeps the best itinerary that satisfies the days, so a chain is not hidden because its
  best itinerary is too long. A partial chain is dropped as soon as its days or km pass
  the maximum, since both only grow. The minimum days apply when a chain is kept.
  Known ceiling: the search keeps one itinerary per return day (the one with the most
  nights), so with a minimum a chain whose only long-enough itinerary has fewer nights
  is missed. Marked `SIMPLIFIED:` in the code.
- **Max total km** is the km of the legs, as the `km driven` column shows, not the
  connections.
- **Round trip** is the last return station being in the first pick-up station's
  `near` list: the same station, or within the selected next pick-up distance.
- **Options count only in chain mode.** In trip mode the group is hidden and means
  nothing, so a changed option does not count in `Filters (n)` or show `Reset` there.
  The values are kept, like the station selections, and count again in chain mode.
- **Distances carry `~`.** The next pick-up options read `~25 km` and so on, because the
  distance is always the straight line x 1.3; the hand-over text keeps its `~` too.
- **Speed.** Measured on a real scan, the old widest setting (3 legs, 2 rest days, 100 km)
  took 300 ms and the defaults 38 ms. The new search takes about 20 ms for the defaults and
  50 to 70 ms for those wider settings. The widest new setting (2 or 3 legs, 7 rest days,
  250 km, over 220,000 chains) takes 340 to 440 ms, above the 300 ms target but with eight
  times as many chains as the old widest.
  Debouncing typed numbers was not added: selects and checkboxes are one change each,
  and a few hundred milliseconds only happens at the extreme.
  The gains: pairs are indexed by pick-up day, so a leg looks at the days its break
  allows instead of every pair; an itinerary links back to its parent and its legs are
  built only for a kept chain; the last leg keeps one itinerary; routes whose days
  cannot follow are skipped; date labels are formatted once.
