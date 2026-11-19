# roadsurfer Rally map

Finds [roadsurfer Rally](https://booking.roadsurfer.com/en/rally) one-way campervan
relocation offers and shows them on a map.

`roadsurfer-rally.py` asks the roadsurfer booking API for every Rally route and its
timeframes, prints the offers with booking links and, with `--map`, writes an HTML
page. The page uses the vendored copy of Leaflet and draws each offer as a line from
its pick-up station to its return station.

This project uses an unofficial, undocumented API. It is not affiliated with,
endorsed by or supported by roadsurfer. The API can change or stop working at any
time.

## Run it locally

You need Python 3.8 or newer. Only the standard library is used. The script compiles
and runs `--help` on Python 3.8 through 3.14, and real scans were run on 3.8 and
3.14.

```sh
python3 roadsurfer-rally.py --map index.html
```

Then open `index.html` in a browser. The page loads Leaflet from `vendor/leaflet/`
by relative path, so write the `--map` file in the repo root, next to `vendor/`. The
map tiles still come from Esri, so viewing the page needs an internet connection. A
full scan makes about 850 sequential requests and takes several minutes.

Other useful options:

```sh
python3 roadsurfer-rally.py --list                       # list stations and exit
python3 roadsurfer-rally.py --from BE --to Lisbon        # filter by country code or name
python3 roadsurfer-rally.py --start 2026-06-01 --end 2026-06-30
python3 roadsurfer-rally.py --prices --map index.html    # add models and prices
python3 roadsurfer-rally.py --help
```

Git ignores the generated `index.html`.

### Scan and render separately

Scanning needs the API. Rendering the page does not. `--json-out` saves the scanned
offers as a JSON object with an `offers` list, the same records the page embeds.
`--from-json` builds the page from that file without any network request:

```sh
python3 roadsurfer-rally.py --json-out offers.json        # scan only
python3 roadsurfer-rally.py --from-json offers.json --map index.html  # render offline
```

`--from-json` needs `--map` and does not accept `--list`, `--json-out`, `--from`,
`--to` or `--prices`. `--map` without `--from-json` scans and renders in one run.

### Usage

Output of `python3 roadsurfer-rally.py --help` on Python 3.14. Python 3.8 and 3.9
label the options section `optional arguments:`.

```text
usage: roadsurfer-rally.py [-h] [--to [TO ...]] [--from [ORIGIN ...]]
                           [--start START] [--end END] [--prices]
                           [--map FILE.html] [--json-out FILE.json]
                           [--from-json FILE.json] [--delay DELAY] [--list]

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
  --json-out FILE.json  write the scanned offers as {"offers": [...]}
  --from-json FILE.json
                        render --map from a --json-out file, without network
                        access
  --delay DELAY         seconds between requests (default 0.5)
  --list                list stations and exit
```

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
  waits 0.5 s before each one (`--delay`). It retries with backoff on errors.
- Every rally lasts 7 days and costs a flat €129.01.
- Ranges longer than 7 days come back as unavailable.

## License

Apache License 2.0, see [LICENSE](LICENSE).
