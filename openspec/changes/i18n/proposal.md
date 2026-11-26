# Proposal

## Why

roadsurfer customers come from several European countries and the map page is English
only. Issue #56 asks for the interface in their language, with dates, numbers and
distances formatted for it and no new dependency (part `i18n` of the redesign brief,
section 11).

## What Changes

- Seven interface languages: English (the source and the fallback), German, French,
  Spanish, Italian, Dutch and Portuguese. Every text the page shows comes from one
  message catalog, `STRINGS`, in its own marked block of the template: the visible text,
  counts, tooltips, the legend, empty states, the chain hand-over copy, the `Updated`
  line, and the accessible names that are not visible. A key a language lacks falls back
  to English, never to a blank or to the key.
- The language is chosen from `#…&lang=xx` in the URL hash, then
  `localStorage['rally-map:lang']`, then the browser's languages (by primary subtag),
  then English. `<html lang>` follows it.
- The `Display` menu gets a `Language` section above `Theme`, listing each language in
  its own language with its code. The `Display` button shows the current code beside its
  theme icon. On a phone the same section is in the `⋯` sheet. A choice goes into the
  hash and into `localStorage`.
- Changing the language re-renders the text in place: the filters, the open route or
  chain, the sort, the theme, the scroll positions and the map view stay.
- Dates, numbers, distances and plurals come from `Intl` for the chosen language (`1,240 km` or `1.240 km`), country names in the pick-up and return menus come from
  `Intl.DisplayNames`, and names sort with `Intl.Collator`. Station names, the
  attribution credits, the release tag and the booking links are not translated.
- Chips, segmented controls, buttons and the app bar wrap or grow in the longer
  languages (German, French) instead of cutting a label.
- A unit test reads the catalog out of the rendered page and checks it against English:
  keys, placeholders and plural forms.

Out of scope: any theme change, translated booking pages or links (the scanner builds
them), translated station names, right-to-left languages.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the map page's language, text catalog and formatting, the Display menu,
  the `Updated` line and the Trips date format.
