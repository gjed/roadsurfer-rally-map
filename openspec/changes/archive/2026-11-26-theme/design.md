# Design

## Decisions

- **Tokens, not a second stylesheet.** One block per theme sets the custom properties;
  `:root` also takes the light block, so a page where the head script did not run is
  light. The brief's names are used (`--bg`, `--surface`, `--surface-2`, `--selected`,
  `--chip-on-bg`, `--note-bg`, …); the earlier `--s2`, `--sel`, `--accent-bg`, `--warn`
  and `--warn-bg` are renamed to them. Colours the brief does not list but the page
  needs get a token with a value in both themes: hover fills, the segmented control's
  pressed and group fills, the table head, the switch track, the grip, the attribution
  background and link, the scrims behind the phone sheets, the logo, and the shadows.
  `--land` is not defined: nothing draws it.
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
  not `var()`. `T` holds the map's tokens read with `getComputedStyle`; `paint({ color:
  'route' })` returns the colour and keeps `{ color: 'route' }` in the layer's options.
  On a theme change every path of the `layer`, `picked` and `hover` groups that has such
  names is restyled with `setStyle`. Nothing is redrawn, so the selection, the hover,
  the filters, the sort, the scroll positions and the map view stay as they are. The
  legend and the inline marker SVGs use `var()` in a style attribute or a class, so the
  CSS restyles them. The transparent hit lines use the keyword `transparent` at opacity
  0, which is not a theme colour.
- **Tiles swap with `setUrl`.** Both tile layers keep their pane (`labels` for the
  reference), their `maxZoom` and the attribution; `setUrl` redraws their tiles in
  place. The page's sea token shows behind the tiles while they load. The attribution
  text is the same for both sets.
- **Display menu: a section per setting.** The panel is a `.pop` like the chip panels,
  so it reuses their open, close, Esc, focus return, outside click and Tab trap. Each
  setting is a `.dsec` section in `.pb`; the `i18n` part adds a language section before
  `Theme` and the globe and code to the button, without touching the rest. On a phone
  the panel is a bottom sheet like the chain options, and the button shows `⋯` instead
  of the theme icon; it is the same button, so it keeps the name
  `Display settings: theme <choice>`. While a route or chain is open on a phone the app
  bar is hidden (as before), so the menu is reached after going back.
- **Dark shadows.** Shadows barely show on dark, so in dark a shadow token becomes
  `0 0 0 1px var(--line)`. A panel that already has a border (the popovers) gets
  `none`, so it does not get a double border.
- **Dark logo.** The logo's dark chip would vanish on a dark bar, so in dark it takes
  the raised surface with a field-coloured border and a light curve; the orange dot is
  the selected colour.
- **Favicon.** The `<link rel=icon>` data URI keeps its blue: it is outside the page and
  cannot read the page's properties.

## Contrast

Measured on the real Esri tiles (colours sampled over Europe at zoom 5, 7 and 9: light
land `#EFEFEF` and sea `#D0CFD4`; dark land `#3F3F41` to `#49494B` and sea `#222327`)
and on the rendered page, WCAG 2.x relative luminance, worst colour of each set.

| Colour | Light on Light Gray | Dark on Dark Gray |
|---|---|---|
| route | 3.39 | 3.73 |
| selected | 3.34 | 3.85 |
| hop | 3.68 | 3.67 |
| station ring | 9.41 | 7.45 |

- **The dark route, selected and hop values pass 3:1 on the Dark Gray tiles, so the
  brief's values are kept.** The pairs of a theme with the other tile set never occur,
  because the tiles follow the theme.
- Text: every visible text in the list, route, chain, Trips, popover, sheet and Display
  views, of both themes and both viewports, was checked against its composited
  background. The lowest is 5.2:1 in light and 5.9:1 in dark (4.5:1 required); a disabled
  stepper is exempt. The attribution is checked over the tiles' colours.
- The selected line has the same luminance as an unselected one in both themes (the
  brief's tokens: 1.01:1 and 1.03:1), so it is told apart by the halo (5.2:1 light,
  8.1:1 dark against the line), its weight and full opacity, and by the other lines
  dropping to 0.18 opacity while one is open or hovered (they then differ from the
  selected line by 2.7 to 3.6:1 in light and 3.0 to 4.8:1 in dark, by tile colour).
  The brief's tokens are kept: moving either colour would change the light values
  of section 7.
- **Known gap, unchanged by this part.** A route line is faded by the existing opacity
  ramp (`Route line weight`): a one-trip line at 0.5 opacity measures 1.8:1 in light and
  2.0:1 in dark; the busiest line (0.85) measures 2.8:1 in light and 3.1:1 in dark. The
  ramp is the data encoding, so it stays. The control borders (`--field`) keep the brief's values and are
  1.5:1 in light and 1.7:1 in dark; the controls are named by their text.
