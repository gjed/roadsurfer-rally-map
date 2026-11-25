# Design

## Decisions

- **The sheet wraps the existing sidebar.** `#side` keeps its content, focus handling
  and events; on phones a `#sheet` wrapper with a grip button gives it a height, and on
  desktop the wrapper is `display: contents`, so the desktop layout is the same box tree
  as before. The 1440×900 screenshots of the map, Trips and chains views are
  pixel-identical to origin/main.
- **Snap heights from the view, not constants.** Peek is `min(330 px, 50 % of the map view)`, so a 360×740 phone still shows the map; half is about 62 %; full leaves 8 px.
  They are recomputed on resize. The sheet height is a CSS variable that also lifts the
  Leaflet bottom controls (attribution, legend) above the sheet.
- **Fits use the target height.** `fitAll()` and `fitPicked()` pad the bottom by the
  sheet's target height (the variable, not `offsetHeight`, which is mid-transition) plus
  the attribution, and `fitPicked()` pads the top for the floating title.
- **The filter sheet borrows the panels.** The phone filter sheet moves the bodies of
  the four chip panels (and the chain options) into its sections while it is open and
  gives them back when it closes. Every control keeps its id, handler, faceting and the
  typed-number pause of #46; nothing is duplicated.
- **Apply on Show by snapshot.** The page re-renders live behind the sheet (the counts
  in `Show N` need it), and the sheet stores the URL hash it opened with. Closing it any
  other way than `Show`/`Done` restores that hash through `readHash()`, the same path a
  reload or Back takes. The chain options sheet uses the same rule, so both phone sheets
  behave alike.
- **The grip is a disclosure button.** `aria-controls="side"`, `aria-expanded` true at
  full, and an `aria-label` of `Expand results` or `Collapse results`. Pointer capture
  makes the drag work from the grip only, so the list inside still scrolls.
- **Reduced motion** turns off the sheet's height transition and the fits' animation
  through the existing `prefers-reduced-motion` rules.
