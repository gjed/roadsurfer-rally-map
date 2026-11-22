# roadsurfer Rally map

Finds [roadsurfer Rally](https://booking.roadsurfer.com/en/rally) one-way campervan
relocation offers and shows them on a map.

Live map: <https://gjed.github.io/roadsurfer-rally-map/>, refreshed twice a week by
[`scan.yml`](.github/workflows/scan.yml).

`roadsurfer-rally.py` asks the roadsurfer booking API for every Rally route and its
timeframes, prints the offers with booking links and, with `--map`, writes an HTML
page. The page uses the vendored copy of Leaflet and draws each offer as a line from
its pick-up station to its return station.

This project uses an unofficial, undocumented API. It is not affiliated with,
endorsed by or supported by roadsurfer. The API can change or stop working at any
time.

## Run it locally

You need Python 3.8 or newer. Only the standard library is used. The PR check runs
the unit tests and renders the map on Python 3.8 and on the newest Python 3, and real
scans were run on 3.8 and 3.14.

```sh
python3 roadsurfer-rally.py --map index.html
```

Then open `index.html` in a browser. The page loads Leaflet from `vendor/leaflet/`
by relative path, so write the `--map` file in the repo root, next to `vendor/`. The
map tiles still come from Esri, so viewing the page needs an internet connection. A
full scan makes about 850 sequential requests and takes several minutes.

The toolbar shows when the data was scanned, in UTC, before the route and trip
counts, for example `updated 2026-11-18 03:12 UTC · 12 routes · 724 / 724 trips`.
Hovering it shows the offer, request and failed-request counts of that scan. A page
rendered from a data file without scan metadata shows no timestamp.

The `List` button swaps the map for a table of the trips that pass the current
filters, one row per trip with its dates, stations, estimated distance, price when
scanned with `--prices`, and booking link. The filters and the counts stay as they
are when you switch. Rows are sorted by start date; click the start, end or `km`
header to re-sort, and click a row to see that route on the map with its popup open.

Other useful options:

```sh
python3 roadsurfer-rally.py --list                       # list stations and exit
python3 roadsurfer-rally.py --from BE --to Lisbon        # filter by country code or name
python3 roadsurfer-rally.py --start 2026-06-01 --end 2026-06-30
python3 roadsurfer-rally.py --prices --map index.html    # add models and prices
python3 roadsurfer-rally.py --help
```

Git ignores the generated `index.html`.

### Make targets

The `Makefile` wraps the common commands. Run `make` alone to list them.

| Target       | Runs                                                                                            |
| ------------ | ----------------------------------------------------------------------------------------------- |
| `make scan`  | Full scan into `offers.json` (git-ignored), at the default delay                                |
| `make map`   | Renders `index.html` from `offers.json` offline, or from `tests/fixtures/offers.json` if absent |
| `make serve` | `python3 -m http.server` on `127.0.0.1:8000`, from the repo root                                |
| `make lint`  | `pre-commit run --all-files`                                                                    |
| `make test`  | `python3 -m unittest discover -s tests -v`                                                      |

### Scan and render separately

Scanning needs the API. Rendering the page does not. `--json-out` saves the scan as
a JSON object with an `offers` list, the same records the page embeds, and a `scan`
object with the scan metadata:

| Key            | Value                                                       |
| -------------- | ----------------------------------------------------------- |
| `finished_at`  | when the scan finished, UTC, e.g. `2026-11-18T03:12:05Z`    |
| `offers`       | number of offers found                                      |
| `requests`     | API requests sent                                           |
| `failed`       | requests the scanner gave up on                             |
| `rate_limited` | HTTP 429 answers received                                   |
| `start`, `end` | the `--start` and `--end` window                            |
| `from`, `to`   | the `--from` and `--to` terms as given, `null` when not set |

`--from-json` builds the page from that file without any network request:

```sh
python3 roadsurfer-rally.py --json-out offers.json        # scan only
python3 roadsurfer-rally.py --from-json offers.json --map index.html  # render offline
```

`--from-json` needs `--map` and does not accept `--list`, `--json-out`, `--from`,
`--to` or `--prices`. `--map` without `--from-json` scans and renders in one run.
`--from-json` embeds the file's `scan` object as is; a file without one, written
before the metadata existed, still renders, with no timestamp in the toolbar.
`--release TAG` (with `--map`) shows the tag in a footer linked to its GitHub
release; without it, or with an empty tag, the page has no footer.

### Usage

Output of `python3 roadsurfer-rally.py --help` on Python 3.14. Python 3.8 and 3.9
label the options section `optional arguments:`.

```text
usage: roadsurfer-rally.py [-h] [--to [TO ...]] [--from [ORIGIN ...]]
                           [--start START] [--end END] [--prices]
                           [--map FILE.html] [--json-out FILE.json]
                           [--from-json FILE.json] [--delay DELAY]
                           [--release TAG] [--list]

Query roadsurfer Rally (one-way relocation) offers.

Unofficial API used by booking.roadsurfer.com (stdlib only):
  GET /api/{lang}/rally/stations                 all stations
  GET /api/{lang}/rally/stations/{id}            station; "returns" = rally destinations
  GET /api/{lang}/rally/timeframes/{from}-{to}   [{startDate, endDate}, ...]
  GET /api/{lang}/rally/search?stations=[[from,to]]&range=[start,end]&currency=EUR
                                                 models + price for an exact timeframe
The X-Requested-Alias header must match the route alias or the API returns 404.

options:
  -h, --help            show this help message and exit
  --to [TO ...]         destination stations (id, name, city or country code)
  --from [ORIGIN ...]   origin stations (default: all)
  --start START         window start YYYY-MM-DD
  --end END             window end YYYY-MM-DD
  --prices              fetch models and price per offer
  --map FILE.html       write a self-contained map of the offers (add --prices
                        for models/price)
  --json-out FILE.json  write the scan as {"scan": {...}, "offers": [...]}
  --from-json FILE.json
                        render --map from a --json-out file, without network
                        access
  --delay DELAY         seconds between requests (default 0.5)
  --release TAG         release tag to show in the --map footer, e.g. v1.2.0
  --list                list stations and exit
```

## Published map

The workflow [`scan.yml`](.github/workflows/scan.yml) scans on Monday and Thursday at
03:17 UTC, and on manual dispatch, with `--delay 5`. It renders the page from the scan
with the latest release tag (none before the first release) and publishes
`index.html` and `vendor/` to <https://gjed.github.io/roadsurfer-rally-map/>. The run
also keeps the scanned `offers.json` as the workflow artifact `offers`. When the scan fails, nothing
is deployed and the published page stays at the last good scan. GitHub pauses
scheduled workflows after 60 days without repository activity; a maintainer then
re-enables the scan with `gh workflow enable scan.yml` (or Actions → Enable).

The workflow scans without `--prices`, so the published popups show dates and the
booking link but no models or prices. `--prices` would add one request per offer on
top of the scan, and every rally costs the same flat price anyway (see Known
behaviour).

### Releases

The workflow [`release.yml`](.github/workflows/release.yml) runs
[semantic-release](https://semantic-release.gitbook.io/) on every push to `main`.
A `feat` commit bumps the minor version, a `fix` or `perf` commit the patch; other
types cut no release. A release is a `vX.Y.Z` tag and a
[GitHub release](https://github.com/gjed/roadsurfer-rally-map/releases) with
generated notes; nothing is committed back to `main`.

A release also redeploys the page without scanning: the workflow renders it from the
`offers` artifact of the latest successful `scan.yml` run on `main`, with the new tag
in the page footer, so code changes reach the map without waiting for the next scan
and without any request to roadsurfer. If that artifact is missing or expired (after
90 days), the release job fails with an error and the page stays as it is; dispatch
`scan.yml` to publish a fresh page with the tag.

The deploy jobs of both workflows share the concurrency group `pages`, so two deploys
never overlap and a queued scan and a queued release do not cancel each other.

## Vendored Leaflet

`vendor/leaflet/` holds an unmodified copy of [Leaflet](https://leafletjs.com/)
1.9.4 (`leaflet.js`, `leaflet.css`, `images/`), taken from the npm package
[leaflet-1.9.4.tgz](https://registry.npmjs.org/leaflet/-/leaflet-1.9.4.tgz). Leaflet
is licensed under BSD-2-Clause, see
[vendor/leaflet/LICENSE](vendor/leaflet/LICENSE). The version is recorded in
[vendor/leaflet/VERSION](vendor/leaflet/VERSION).

The generated page finds Leaflet only when `vendor/` sits next to it. A published
page must ship the `vendor/` directory alongside `index.html`.

To update Leaflet to version `X.Y.Z`:

1. Download and unpack the package:

   ```sh
   npm pack leaflet@X.Y.Z
   tar xzf leaflet-X.Y.Z.tgz
   ```

1. Replace the vendored files with the ones from the package:

   ```sh
   rm vendor/leaflet/images/*.png
   cp package/dist/leaflet.js package/dist/leaflet.css package/LICENSE vendor/leaflet/
   cp package/dist/images/*.png vendor/leaflet/images/
   ```

   Do not edit them: pre-commit and git leave `vendor/` as is.

1. Write `X.Y.Z` to `vendor/leaflet/VERSION` and update the version and URL in this
   section.

1. Check the files against the `leaflet.zip` asset of the
   [GitHub release](https://github.com/Leaflet/Leaflet/releases) with `sha256sum`.
   The zip's `leaflet.js` differs only in its banner comment, which adds the build
   hash (for 1.9.4: `1.9.4+v1.d15112c`).

1. Generate a map in the repo root, serve the folder with `python3 -m http.server`
   and check that the map, the route lines and the markers render.

Renovate watches `vendor/leaflet/VERSION` and opens a PR when a new stable Leaflet
version is on npm. That PR changes only `VERSION`, so it is never automerged: check
out its branch, run the steps above for the new version, push, and merge once the
checks pass. Leaflet prereleases are ignored.

## API notes

These notes were reverse-engineered from booking.roadsurfer.com.

The base URL is `https://booking.roadsurfer.com/api/en`. Every request needs an
`X-Requested-Alias` header that matches the route. Without it, the API answers with
a 404 HTML page.

| Path                                                                                | Alias                 | Returns                                      |
| ----------------------------------------------------------------------------------- | --------------------- | -------------------------------------------- |
| `/rally/stations`                                                                   | `rally.startStations` | All stations with city, country, coordinates |
| `/rally/stations/{id}`                                                              | `rally.fetchRoutes`   | `returns`: destination station ids           |
| `/rally/timeframes/{from}-{to}`                                                     | `rally.timeframes`    | `[{startDate, endDate}]`                     |
| `/rally/search?stations=[[from,to]]&range=["YYYY-MM-DD","YYYY-MM-DD"]&currency=EUR` | `rally.search`        | Models and price for one exact slot          |

### Known behaviour

- Bursts of requests get HTTP 429. The scanner sends requests one at a time and
  waits before each one for the delay (`--delay`, 0.5 s by default, 5 s in the
  workflow) plus a random jitter of up to 20% of the delay.
- After an HTTP 429 the scanner waits about 1, 2, 3 and then 4 minutes, plus up to
  30 s of jitter, before each retry. Other errors are retried after 2 s. It gives up
  on a request after five attempts, and at once on any other 4xx answer.
- After a scan, the scanner prints the number of requests, failed requests and 429
  answers, and the duration. When more than 10% of the requests failed
  (`MAX_FAILED`), it exits with status 1 and writes neither the `--json-out` nor the
  `--map` file.
- A full scan makes about 850 requests. With `--delay 5` it takes about 70 to 90
  minutes; the workflow allows 150.
- Every rally lasts 7 days and costs a flat €129.01.
- Ranges longer than 7 days come back as unavailable.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and the pull request flow, and
[AGENTS.md](AGENTS.md) for the conventions. Every pull request runs
[`pr-check.yml`](.github/workflows/pr-check.yml): pre-commit, the unit tests and an
offline render of the test fixture.

## License

Apache License 2.0, see [LICENSE](LICENSE).
