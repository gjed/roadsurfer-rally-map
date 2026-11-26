# Design

## Decisions

- **Tokens, not a second stylesheet.** One block per theme sets the custom properties;
  `:root` also takes the light block, so a page where the head script did not run is
  light. The brief's names are used (`--bg`, `--surface`, `--surface-2`, `--selected`,
  `--chip-on-bg`, `--note-bg`, …); the earlier `--s2`, `--sel`, `--accent-bg`, `--warn`
  and `--warn-bg` are renamed to them. Colours the brief does not list but the page
  needs get a token with a value in both themes: one hover fill, the segmented control's
  pressed and group fills, the table head, the switch track and knob, the scrims behind
  the phone sheets, the stronger control border `--ctl-line`, and the shadows. The page's
  sea and land tokens are the measured tile colours of the Dark Gray canvas
  (`#222327`, `#3F3F41`), not the brief's `#1B2027` and `#262B33`, so the map does not
  change shade while its tiles load; `--land` is not drawn by the page itself.
- **The head script and the page script agree by construction.** A tiny inline script
  sets `data-theme` from the same storage key and media query before the stylesheet is
  used for the first paint. The page script reads the choice again for the Display
  menu, and only touches the layers when the resolved theme differs from what is set.
  A stored value other than `system`, `light` or `dark`, or unavailable storage, means
  `system`.
- **`color-scheme` follows the page, not the device.** `color-scheme: light` or `dark`
  is set per theme block, so native inputs, date pickers and scrollbars match a chosen
  theme even when it differs from the device. The meta tag (`light dark`) only covers the
  moment before the styles apply.
- **Map colours: names on the layers, values from the CSS.** Leaflet takes colours,
  not `var()`. `T` holds the map's tokens read with `getComputedStyle`; `paint({ color: 'route' })` returns the colour and keeps `{ color: 'route' }` in the layer's options.
  On a theme change every path of the `layer`, `picked` and `hover` groups that has such
  names is restyled with `setStyle`, and a line also takes its opacity from its ramp
  again (below). Nothing is redrawn, so the selection, the hover, the keyboard focus,
  the filters, the sort, the scroll positions and the map view stay as they are. The
  inline marker SVGs use `var()` in a style attribute, so the CSS restyles them; the
  legend is built again, since its samples carry the ramp. The transparent hit lines use the keyword `transparent` at opacity
  0, which is not a theme colour.
- **Tiles swap with `setUrl`.** Both tile layers keep their pane (`labels` for the
  reference), their `maxZoom` and the attribution; `setUrl` redraws their tiles in
  place. The page's sea token shows behind the tiles while they load. The attribution
  text is the same for both sets.
- **Display menu: a section per setting.** The panel is a `.pop` like the chip panels,
  so it reuses their open, close, Esc, focus return, outside click and Tab trap. Each
  setting is a `.dsec` section in the `.copt` body; the `i18n` part adds a language section
  before `Theme` and fills the button's hidden `.dlang` and `.dsep` with the globe and
  code, without touching the rest; until then the button is a 36 px square. On a phone
  the panel is a bottom sheet like the chain options, and the button shows `⋯` instead
  of the theme icon; it is the same button, so it keeps the name
  `Display settings: theme <choice>`. While a route or chain is open on a phone the app
  bar is hidden (as before), so the menu is reached after going back.
- **Dark shadows.** Shadows barely show on dark. Off the map a shadow token becomes
  `0 0 0 1px var(--line)`, and `none` for a panel that already has a border (the
  popovers). Over the map (zoom and fit, legend, tooltips, the phone sheet and the route
  title) a bare line does not separate a control from the dark land, so the token is a
  `#2F3540` ring with a soft `0 2px 8px` shadow.
- **Selected colour invariant.** The selected colour has the luminance of the route
  colour in both themes (1.01:1 and 1.03:1, the brief's tokens), so whatever is drawn in
  it (the `picked` and `hover` layers) has `#rmap.dim` set, which drops the other lines
  to 0.18 opacity. A comment at `dimMap()` says so.
- **Controls whose border carries meaning.** Empty inputs, selects and the stepper use
  `--ctl-line` (3.24:1 on the dark surface); chips and pills keep `--field`.
- **Logo and markers.** The logo is the ink chip with the page colour for its strokes, so
  it follows the theme; the orange dot is `--brand`, the same in both. Hollow and filled
  markers in the cards are `currentColor` on `--surface`, or `var(--selected)`.
- **Favicon.** The `<link rel=icon>` data URI keeps its blue: it is outside the page and
  cannot read the page's properties.

## Contrast

Measured on the real Esri tiles (colours sampled over Europe at zoom 5, 7 and 9: light
land `#EFEFEF` and sea `#D0CFD4`; dark land `#3F3F41` to `#49494B` and sea `#222327`)
and on the rendered page, WCAG 2.x relative luminance, worst colour of each set.

| Colour       | Light on Light Gray | Dark on Dark Gray |
| ------------ | ------------------- | ----------------- |
| route        | 3.39                | 3.73              |
| selected     | 3.34                | 3.85              |
| hop          | 3.68                | 3.67              |
| station ring | 9.41                | 7.45              |

- **The dark route, selected and hop values pass 3:1 on the Dark Gray tiles, so the
  brief's values are kept.** The pairs of a theme with the other tile set never occur,
  because the tiles follow the theme.
- Text: every visible text in the list, route, chain, Trips, popover, sheet and Display
  views, of both themes and both viewports, was checked against its composited
  background. The lowest is 5.2:1 in light and 5.6:1 in dark (4.5:1 required); a disabled
  stepper is exempt. The attribution is checked over the tiles' colours.
- The selected line has the same luminance as an unselected one in both themes (the
  brief's tokens: 1.01:1 and 1.03:1), so it is told apart by the halo (5.2:1 light,
  8.1:1 dark against the line), its weight and full opacity, and by the other lines
  dropping to 0.18 opacity while one is open or hovered (they then differ from the
  selected line by 2.7 to 3.6:1 in light and 3.0 to 4.8:1 in dark, by tile colour).
  The brief's tokens are kept: moving either colour would change the light values
  of section 7.
- **Opacity floors.** A route line is faded by an opacity ramp. Its floor and ceiling are
  tokens (`--route-op-min` and `--route-op-max`: .8 and .95 in light, .75 and .9 in dark;
  `--chain-op-min`: .8 and .75), read like the colours; the trip count still sets the
  opacity (`min(floor + (trips - 1) * .1, ceiling)`, and `* .05` for chains). Measured on
  land, a one-trip line is 3.2:1 in light (land `#EDEDED` to `#EFEFEF`) and 3.1:1 in dark
  at zoom 5 to 7 (`#3F3F41`, `#414143`); the busiest is 4.1:1 and 3.7:1. On the lighter dark
  land of zoom 9 and beyond (`#49494B`) the one-trip line is 2.8:1, and on the sea of the
  light tiles (`#D0CFD4`) it is 2.6:1; both stay below 3:1. The control borders (`--field`)
  keep the brief's values (1.5:1 light, 1.7:1 dark) on chips and pills.
