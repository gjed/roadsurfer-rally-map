# Design

## Context

The page computes `roadKm(from, to)` in the browser: great circle × 1.3, rounded to
10 km. It feeds the distance filter, the `km` column and sort, the popup and the
tooltip. A scan writes the offer records to `--json-out`; `release.yml` and
`--from-json` render from that file and must not scan or route.
`main` requires signed commits, so no workflow can commit a cache file.

## Goals / Non-Goals

**Goals:**

- Real driving distance per station pair, computed once and stored in the data.
- A second scan with no new pair sends no routing request.
- Routing problems never block a scan or weaken the roadsurfer rate rules.

**Non-Goals:**

- Durations, route geometry, a self-hosted router.

## Decisions

- **OSRM public demo server.** Free, no key, covers ferries and mountain roads in
  the `driving` profile. Its policy asks for at most one request per second, a
  descriptive User-Agent and no bulk use; routing sleeps 1 s before each request,
  runs sequentially and sends `roadsurfer-rally-map (+repo URL)`. `--routing-url`
  accepts any OSRM server.
- **`/table`, not `/route`.** About 780 pairs would be 780 `/route` requests, 13
  minutes and a lot of demo-server load, on the first run. A `/table` request with one
  source and up to 50 destinations returns the same distances (checked against
  `/route`: 1321075 m against 1321074.9 m for Munich to Bordeaux) in one request per
  pick-up station, about 60 in total. 50 destinations keep the request under the demo
  server's table size limit (100 coordinates) and the URL short. The cost is that a
  failed request affects a chunk of pairs; those fall back to the estimate and are
  retried by the next scan.
- **Cache key: pick-up and return coordinates, in that order**, formatted to 5
  decimals (about 1 m), e.g. `48.20400,11.58600>44.82100,-0.69300`. The records carry
  no station ids, and the coordinates are what the router uses, so a station that
  moves is routed again by itself, and two stations with the same name stay apart.
  Direction matters because one-way roads make `A>B` and `B>A` differ. The file is
  `{"pairs": {key: km}}` with km rounded to whole kilometres.
- **Routing after the scan check, only when a file is written.** A blocked scan
  writes nothing and must not route or save a cache; a scan that only prints the offers
  needs no distances. Routing is one more step in `main`, outside the roadsurfer
  `get()` and its counters, so `MAX_FAILED` and the `--delay` pacing are untouched.
- **Fallback in the scanner and in the page.** On a failed or empty answer the
  scanner writes the × 1.3 estimate itself with `km_estimated: true`, so the data
  file is complete. The page keeps its own `roadKm` for records without `km` (old
  artifacts, the fixture). Both round alike, and a test pins that.
- **Circuit breaker.** A 429 answer, or three failed routing requests in a row, stops
  routing for the run, so a down service costs seconds, not hundreds of timeouts. The
  remaining pairs are estimated.
- **Actions cache with a key per run.** Cache keys are immutable, so
  `scan.yml` saves under `road-distances-${{ github.run_id }}` and restores with
  `restore-keys: road-distances-`, which picks the newest earlier entry. Restore runs
  before the Scan step and save right after it, so a failed scan (step skipped) or a
  crash saves nothing. `contents: read` is enough for `actions/cache`; the `pages`
  concurrency group stays on the deploy job. There is no artifact carry-over and no
  committed file. A cache evicted after 7 days of disuse only means one full routing
  pass.
- **Labels and credit.** Routed values read `N km by road`; estimates read
  `~N km (estimated)` in the popup, tooltip and list (`~N`). A footer, visible in map
  and list view, explains `~` and credits OSRM and OpenStreetMap contributors; each
  sentence appears only when the page has such a distance. The map's attribution
  control has no OpenStreetMap credit today (the tiles are Esri), so the footer adds it.

## Risks / Trade-offs

- The demo server has no uptime promise. A failure only costs accuracy, and the next
  scan tries again.
- The demo server's data is not versioned, so a cached distance can differ slightly
  from a fresh answer. Acceptable: station pairs rarely change.
