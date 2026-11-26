# Proposal

## Why

Someone who wants a rally from one pick-up station has to open the map after every
scan. The site is static, so push or e-mail would need a server; a feed reader already
does the notifying. Issue #61 asks for Atom feeds published next to the page.

## What Changes

- A new scanner option `--feeds DIR` writes `DIR/all.xml`, with every offer, and one
  `DIR/from-<slug>.xml` per pick-up station, with that station's offers. It works with
  a scan and with `--from-json`, and uses the standard library only.
- One entry is one offer window. Its `<id>` is a `tag:` URI built from the route and the
  window, so a reader shows only windows it has not seen: "new offer" needs no state
  from the previous scan. `<updated>` is the scan time.
- The slug of a station is defined once (ASCII, lowercase, hyphens, deterministic on
  accents and duplicates) so that the map's per-station Feed link (issue #60) builds
  the same file names.
- `scan.yml` and `release.yml` render the feeds with the page and publish `feeds/`
  next to `index.html`. Neither sends a request. The PR check renders the fixture feeds
  and fails when one does not parse.
- The page links `feeds/all.xml` with `<link rel="alternate" type="application/atom+xml">`
  in `<head>`. This is the only template change and shows nothing.

Out of scope: the per-station Feed link and the favourites UI (issue #60), per-route
feeds, any history of earlier scans, and a language choice for the feed text.

## Capabilities

### Modified Capabilities

- `rally-scanner`: the `--feeds` option and the feed format; `--from-json` takes
  `--feeds` as well as `--map`; routing and the blocked-scan rule cover `--feeds`.
- `site-publishing`: the Pages artifact and the release deploy carry `feeds/`.
- `pr-check`: the fixture render also writes the feeds, and the page check parses them.

## Impact

`roadsurfer-rally.py`, `rally-map.template.html` (one `<link>`), `scan.yml`,
`release.yml`, `pr-check.yml`, `tests/test_scanner.py`, `.gitignore`, README.md,
AGENTS.md. No new request, secret or permission. `releases` is unchanged: the release
deploy requirement lives in `site-publishing`.
