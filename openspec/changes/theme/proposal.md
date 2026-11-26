# Proposal

## Why

The map page has a single light look. At night, or with a dark system setting, it is a
white page over a bright map. Issue #57 asks for a dark theme that follows the system
by default, can be switched by hand, and keeps WCAG AA contrast (part `theme` of the
redesign brief, section 10).

## What Changes

- Two themes, light and dark. Every colour of the page comes from a CSS custom property
  under `:root[data-theme=light]` or `:root[data-theme=dark]`. No colour is written in a
  component rule, a Leaflet path option or an inline SVG any more; the map's colours are
  read from the properties and restyled in place when the theme changes.
- A `Display` button at the far right of the app bar, showing the current theme as an
  icon, opens a panel with a `Theme` control: `System` (default), `Light`, `Dark`. On a
  phone the same control is in a sheet opened by a `⋯` button at the end of the app bar.
  The panel is built from one section per setting, so a language section can be added
  above `Theme` later.
- `System` follows `prefers-color-scheme` and changes live. A choice is kept in
  `localStorage` and is not in the URL. The theme is set before the first paint, so a
  saved dark page never flashes light.
- The base map switches with the theme: Esri's Light Gray canvas in light, Dark Gray
  canvas in dark, base and reference layers swapped in place. The view, the open route
  or chain, the filters, the sort and the scroll positions stay.
- Zoom, fit, attribution and tooltips follow the theme. In dark, shadows become 1 px
  borders.
- Contrast is measured against the real tiles of both sets; the dark route, selected and
  hop colours are kept because they pass 3:1.

Out of scope: a language selector and the extraction of strings (the later `i18n` part),
changes to the tile provider or to the route weight and opacity ramp.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the map page's colours, tiles and the Display menu.
