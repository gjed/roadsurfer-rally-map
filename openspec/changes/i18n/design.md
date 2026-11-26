# Design

## Catalog

`const STRINGS = { en: {...}, de: {...}, … }` sits between the lines `/*STRINGS*/` and
`/*END STRINGS*/`, in a `<script>` of its own before the page script, as one JSON object: double-quoted keys and values, no comments and no
trailing commas. The test cuts the block out of the rendered page and parses it, so the
file needs no second copy of the strings.

- Keys are flat and semantic, by area: `filters.pickup`, `route.windows.help`,
  `chain.hop`, `count.trips`.
- A placeholder is `{name}`. A sentence is one key, never fragments put together in code;
  a list of facts (`a · b · c`) is joined with `·` in code, as the page did before.
- Plurals: when `vars.n` is a number, `t()` asks `Intl.PluralRules` for its category and
  reads `key.one`, `key.other`, … , then `key.other`, then the plain key. The `{n}`
  shown is `Intl.NumberFormat`-formatted, the category comes from the number.
- Fallback: a key the language lacks is read from English. English is complete (the test
  fails otherwise), so the key itself is never shown.
- `t()` returns plain text; `th()` is for HTML: it escapes the translation and inserts the
  variables as given, so a caller passes `esc(name)` or markup. No translation contains
  `"` or `<`, so a string is safe in an attribute.

## Static text

The HTML body keeps its English as the no-script fallback and marks every translated text
node with `data-t="key"` (text) or `data-t-aria-label`, `data-t-title`,
`data-t-placeholder` (attributes). `applyStatic()` writes them at startup and on every
language change. Text that the script builds (chips, lists, tooltips) is built by the
functions that built it and re-rendered by `render()`.

## Formatting locale

Every language formats as one regional locale, set in a table: `en-GB`, `de-DE`, `fr-FR`,
`es-ES`, `it-IT`, `nl-NL`, `pt-PT`. The brief's `Intl.DateTimeFormat(lang, …)` would turn
`Mon 24 Nov` into `Mon, Nov 24` for English and give Brazilian Portuguese. A distance is
`Intl.NumberFormat` with `style: 'unit', unit: 'kilometer'`, which puts a no-break space
before `km`; a range of kilometres names the unit once in its message.

A date range is the message `{a} – {b}` with each end formatted by `short()` or `dm()`. This
deviates from the brief, which asks for `formatRange`: its output differs by engine and
would make the Trips, chain and chip ranges look unlike each other. Dates in a list are
wrapped so that a line breaks only at the arrow or the dash.

The native date inputs of the Dates panel keep the format of the browser, whatever the
page language.

Country names: `Intl.DisplayNames([lang], { type: 'region' })`; if it throws, the code.
The value of the select stays the code.

## Display menu

`.dlang` (globe and code) and `.dsep` are shown on a desktop; below 700 px the button is
the `⋯`, as before. The Language section is a `role="group"` of buttons with
`aria-pressed`, the same pattern as the Theme control, not a listbox: the entries act
like segmented options and need no arrow-key model. Each entry has its own `lang`.

## Language in the URL

`lang` is written to the hash only after a choice (in the menu, or `lang` in the link),
so a plain visit keeps a clean URL. A language from storage or
from the browser is not written to the hash. A link with `lang` does not overwrite the
stored choice; picking in the menu does. The hash is read for `lang` once, at load: Back or a typed hash keeps the
language shown (a history entry made before a language change must not undo it), and
`render()` writes the current language into the entry. `replaceState` is used for it, as for filters.

## Re-render in place

`setLang()` swaps the formatters, `<html lang>` and the static text, then `render()`
rebuilds the text from the state that did not change. The scroll positions of the
sidebar, the Trips page and the chip row are put back, and the open panel stays open
(the Display panel is where the language is picked).

## Layout

German and French run about 30% longer. What broke, and how it is fixed:

- Phone app bar: the one-row bar with the title, the `Map | Trips` links and the Display
  button was wider than 360 px in German, Italian and Portuguese, which made the page
  scroll sideways. The title may now take two lines (`.brand` can shrink) before the bar
  outgrows the screen.
- The `Rallies | Chains` switch in the results sheet was shrunk below its labels by the
  rule that sizes the title next to it; it keeps its own width.
- The filter sheet's `Reset` and `Show` buttons wrap onto two rows when a long label needs
  it, instead of pushing the sheet wider than the screen.
- The Theme buttons in the Display panel grow in height and wrap their label under the icon;
  the panel is 300 px wide instead of 280.

## Complete languages

All seven are complete: English, German, French, Spanish, Italian, Dutch and Portuguese.
The unit test warns about any key a language still lacks.

## Not translated

Station names, the attribution credits (Esri, OSRM, OpenStreetMap, Leaflet), the release
tag, the booking links, the name `Rally map` and the page title (a brand, decided with the
maintainer), and the price text. The price is text the
scanner builds from the API (`<model> €<price>`); parsing it would be a scanner change.
