## Why

The map publishes `feeds/all.xml`, but a visitor cannot find it. The file is linked only
from `<head>`, which browsers do not show and only some feed readers discover, and a
per-station feed link appears only after a pick-up station is chosen
([#69](https://github.com/gjed/roadsurfer-rally-map/issues/69)).

## What changes

- The app bar gets a 36 px square button with the RSS icon between the scan time and
  `Display`. It links `feeds/all.xml` in a new tab, has the accessible name `RSS feed` and
  a tooltip, both in the seven interface languages.
- Below 700 px the button is hidden and the `Display` sheet gets a last section with an
  `RSS feed` link and the same line of text.
- One new message key, `feed.all.tip`, in all seven catalogs; `fav.feed` is reused.
- The PR check and the unit tests require the app bar link.
- README "Feeds" says where the page links the feed.

The `<head>` link, the per-station feed links and the scanner stay as they are. No new
request.

## Impact

- Specs: `rally-scanner` (two added requirements), `pr-check` (one added requirement).
- Code: `rally-map.template.html`, `.github/workflows/pr-check.yml`, `tests/`,
  `README.md`.
