# Design

## Decisions

- **Same controls underneath.** `findChains()` already takes the next pick-up distance
  in km (`o.conn`) and compares each pair with it, so steps of 25 km need no change to
  the search. The ids `cn`, `cs`, `cg`, `ck`, `cdmin`, `cdmax`, `cdrive` and `cr` stay
  and keep their values: `cn` becomes a hidden input that the segmented buttons set,
  `cs` and `cr` are checkboxes with `role="switch"` drawn as switches, `cg` a number
  field between `−` and `+`, `ck` a range input. `chainOptions()`, `setChainOptions()`,
  `markActive()`, the URL and `Clear all` read them as before.
- **#46's rest-day semantics stay, not the brief's.** The brief's `Same day` switch forces
  0 rest days and its stepper defaults to 2. #46 shipped `Same day` on with 0 rest days
  as the default, and `Same day` off meaning 1 to N rest days; links and specs depend on
  it. So the switch stays on by default, the stepper reads `Rest days, up to N` with it
  on and `Rest days, 1 to N` with it off, and its `−` stops at 1 then.
- **Slider pause.** A slider fires `input` on every step and a wide search takes a few
  hundred ms, so it waits 150 ms (the brief), and searches at once on `change`. Typed
  numbers keep #46's 250 ms. While a search waits, the count and `Show N chains` read
  `Finding chains…`.
- **Switch track contrast.** The artboards draw the off track `#B8BEC7`, under 3:1 on
  white; the page uses `#8A929E`.
- **Phone sheet, no snap points.** Below 700 px the panel is fixed to the bottom, up to
  the filter bar, with its own scrolling body and a sticky footer. It is not modal:
  a tap on the bars above closes it, as for any popover. The general bottom sheet with
  snap points is part 4.
