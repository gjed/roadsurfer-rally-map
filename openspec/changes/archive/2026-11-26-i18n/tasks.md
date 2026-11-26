# Tasks

## 1. Catalog and formatting

- [x] 1.1 `STRINGS` in a marked block (`/*STRINGS*/` … `/*END STRINGS*/`) that parses as JSON; flat semantic keys; English complete
- [x] 1.2 `t(key, vars)` with `{name}` placeholders, `Intl.PluralRules` plurals (`.one`, `.other`, other categories where a language needs them) and the fallback to English; `th()` for HTML with escaped text
- [x] 1.3 Dates with `Intl.DateTimeFormat` (UTC) with each range one message, numbers and km with `Intl.NumberFormat`, country names with `Intl.DisplayNames`, name sorting with `Intl.Collator`; the `~` prefix stays
- [x] 1.4 Every literal the page builds moves to `STRINGS`: text, counts, tooltips, legend, empty states, chain copy, the `Updated` line, popups and accessible names; the static HTML is translated at startup and on every change

## 2. Language choice and menu

- [x] 2.1 Choice order: hash `lang`, `localStorage['rally-map:lang']`, `navigator.languages` by primary subtag, English; `<html lang>` on every change, `dir` stays `ltr`
- [x] 2.2 Display button shows the language code; `Language` section above `Theme` with each language in its own language, its code, a `lang` attribute and a checkmark on the current one; the same section in the phone sheet with 44 px targets
- [x] 2.3 A change is written to the hash (`replaceState`) and to storage, and re-renders the text in place: filters, selection, sort, theme, scroll and map view stay
- [x] 2.4 Layout: chips, segmented controls, buttons and the app bar wrap or grow in German and French at 390 and 360 px

## 3. Translations

- [x] 3.1 English, German, Italian complete
- [x] 3.2 French, Spanish, Dutch, Portuguese complete

## 4. Tests, documentation and validation

- [x] 4.1 Unit test: every locale's keys are a subset of English's, every placeholder of English appears in each translation, plural keys have `one` and `other`, English has no missing or malformed entry, a missing key elsewhere is a warning
- [x] 4.2 README wording about the language choice
- [x] 4.3 `make lint test map`, `openspec validate i18n --strict`
- [x] 4.4 Browser check at 1440×900 and 390×844: choice order with emulated locales, `<html lang>`, state kept across a language change (route, chain, popover, Trips, phone), no English left in `it` and `de`, German at 390 and 360 px without a cut label
