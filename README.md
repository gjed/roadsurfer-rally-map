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

The page is in English, German, French, Spanish, Italian, Dutch and Portuguese. It opens
in the language of the browser, falling back to English, and the `Display` button at the
end of the top bar changes it. The choice is kept in the browser and in the page address
(`#map?lang=de`), so a shared link keeps it. Dates, numbers, distances, country names
and station names follow the language; a station that roadsurfer names the same in a
language, or a data file from before station names, shows the English name. Favourites,
the page address and the feeds keep the English names, so they do not change with the
language.

The page has two views, `Map` and `Trips`, and shows either `Single rallies` or
`Chains` (see "Chains"); both switches are in the bar at the top, next to
`Updated 18 Nov, 03:12 UTC`, the time the data was scanned. Hovering that time shows
the offer, request and failed-request counts of that scan. A page rendered from a data
file without scan metadata shows no time.

Below it, one chip per filter shows its value: `Dates`, `Distance`, `Pick-up` and
`Return`. A chip opens a small panel with the filter's controls: the start date range,
the `Any`, `This week` and `Next week` shortcuts and a week slider; the minimum and maximum
km by road; a country and a station for the pick-up and for the return. Each dropdown only
offers stations and countries that still have trips under the other filters. An active
chip turns blue and gets an `×` that clears it, and `Clear all`, next to the trip and
route counts, clears every filter; it only shows while a filter is active.

The map view opens fitted to the stations, on a grey Esri basemap (light or dark,
following the page's theme: `System`, `Light` or `Dark` in the `Display` menu), with the
routes listed beside it, one card per route with its distance, its trips and the next
start. Sort the cards by earliest start, shortest or longest drive or most trips.
Pointing at a card highlights its route on the map, and pointing at a route highlights
its card. Lines get thicker and more opaque with the number of trips. Click a card or a
route to open it: the route turns deep orange, the map zooms to it, and the list
shows its trip windows, each with a `Book` link, the rallies that leave from where it
ends (`Continue from`, a first step towards a chain) and the other routes from the
same pick-up. `← All routes`, Escape or the browser's Back goes back to the list.
Each station is one marker: click it to filter the pick-ups to that station (click it
again to clear the filter), or hover it for its departures and arrivals. The legend in
the corner of the map explains the line weights, the highlighted route, the station
marker and, when the page has an estimate, the `~`. When no trip matches the filters
the page says so and offers `Reset filters`.

The `Trips` view lists the trips that pass the current filters, one row per trip with
its dates, nights, stations, road distance, price when scanned with `--prices`, and
booking link. Rows are sorted by start date; click the `Start` or `Distance` header to
re-sort, and group the rows by route or by pick-up. `Map` on a row opens that route in
the map view. On a phone each trip is a card with its `Map` and `Book` buttons.

On a phone the top bar holds only the logo, the title and `Map | Trips`; the map fills
the screen and the routes or chains are in a sheet over it, whose header has the count
and the `Rallies | Chains` switch. Drag its grip, or tap it, to move the sheet between a
peek at the first cards, half the screen and the full screen. Opening a route or a chain
puts the sheet at half and gives the map the rest of the screen, with a back button and
the title floating over it. The map keeps only its `Fit` button; pinch to zoom. The chip
row starts with `Filters · n`, which opens every filter (and the chain options in chain
mode) on one sheet: changes apply with `Show N trips`, closing it otherwise leaves the
filters as they were, `Reset (n)` clears them all, and the sheet ends with the time of
the scan. The `Trips` view starts with the count, the switch, and `Sort` and `Group`.

The address bar keeps the view, the filters, the open route or chain and the sort
order (for example `#trips?from=Munich&sort=km`), so a reload or a shared link shows
the same page. Opening a route or switching views adds a history entry; changing a
filter does not.

Mark a route, a pick-up station or a chain as a favourite with the star on its card, its
detail or a Trips row, or with `Favourite` under `From <station>`. The `Favourites` chip
then shows only those (a route also counts when it leaves a favourite station) and
floats them to the top of the lists. Favourites live in this browser's `localStorage`,
never in the address bar, and a station that the API renames loses its star. A window
that appeared on a favourite since you last looked gets a `New` badge, and the chip
counts them; opening the item clears them.

Distances are road distances in km. A distance that could not be routed is an
estimate, shown with a leading `~` that the legend explains; see "Road distances".

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
| `stations`     | the pick-up stations asked about, as `{"name", "cc"}`       |

Each station in a record (`from` and `to`) has the English `name`, which is the key of
the page, and may have `names`: the name per page language (`de`, `fr`, `es`, `it`, `nl`,
`pt`), only for the languages where it differs from English, for example
`{"it": "Anversa", "pt": "Antuérpia"}`. A file without `names` is still rendered.

`--from-json` builds the page from that file without any network request:

```sh
python3 roadsurfer-rally.py --json-out offers.json        # scan only
python3 roadsurfer-rally.py --from-json offers.json --map index.html  # render offline
```

`--from-json` needs `--map` or `--feeds` and does not accept `--list`, `--json-out`,
`--from`, `--to` or `--prices`. `--map` and `--feeds` without `--from-json` scan and
render in one run.
`--from-json` embeds the file's `scan` object as is; a file without one, written
before the metadata existed, still renders, with no scan time on the page.
`--release TAG` (with `--map`) shows the tag in the map's attribution, linked to its
GitHub release; without it, or with an empty tag, the page shows no release.

### Road distances

A scan looks up the driving distance of every pick-up and return pair once and
stores it in each offer record as `km`, with `km_estimated` set to `false`. The
page's distance filter, the distance column and sort, the route details and the
tooltips all use that value.

- **Service.** The public [OSRM](https://project-osrm.org/) demo server
  (`router.project-osrm.org`, `--routing-url` points to another OSRM server). Its
  routes are built on [OpenStreetMap](https://www.openstreetmap.org/copyright) data,
  credited in the map's attribution. The scanner follows the demo server's usage
  policy: requests are sequential, one per second at most, with a User-Agent that
  names this project. It asks for one `/table` request per pick-up station (50
  return stations at most), about 60 requests for a first full scan. Routing is
  separate from the roadsurfer API and does not change its rate rules.
- **Cache.** Results are kept in `road-distances.json` (`--road-cache FILE.json`
  changes the path, git ignores the default), keyed by the pick-up and return
  coordinates, in that order, since a road can be one-way. Only pairs missing from it
  are routed, so a second scan with no new station pair sends no routing request.
  `scan.yml` keeps the file in an S3 bucket and in the GitHub Actions cache between
  runs and stores it only after a scan that succeeded; see "Road distance cache in
  S3" below.
- **Fallback.** When routing fails, or OSRM finds no route, the pair gets the
  straight-line distance × 1.3 rounded to 10 km, with `km_estimated` set to `true`.
  It is not cached, so the next scan tries it again, and it never fails the scan. After
  a 429 answer or three failed requests in a row the scanner stops routing for that
  run. Routing runs only when the scan writes `--json-out`, `--map` or `--feeds`,
  after the scan check.
- **Old data.** `--from-json` never routes. A record without `km`, such as a file
  written before this existed, gets the same × 1.3 estimate in the page, labelled
  as an estimate.

### Chains

A rally lasts at most 7 days, so a longer trip means booking rallies one after
another, each as its own trip. The `Chains` switch in the top bar finds those
sequences in the offers already on the page, with no request and no scanner change, and
shows them on the map and in the `Trips` view.

- **Chain options.** In chain mode a `Chain options` chip joins the filter chips and
  shows the current options. On a desktop it opens a panel under it; on a phone the
  panel is a sheet from the bottom, over the darkened page, that opens as soon as `Chains` is pressed; it keeps
  its changes with `Show N chains` and drops them when closed with its `×`, Escape or a
  tap above it. `Show N chains` counts the
  chains as you change the options. The chip turns blue when an option is not at its
  default, `Reset` in the panel restores them, and `Clear all` restores them with the
  filters. The widest settings (2 or 3 legs, 7 rest days, 250 km) match over 200,000
  chains on a real scan and take a few hundred milliseconds to search, so typed numbers
  and the slider search again after a short pause, and the count reads
  `Finding chains…` meanwhile; 4 legs is not offered.
  - Legs: `2` (default), `3`, or `2 or 3`.
  - Between legs: a `Same day` switch (on by default) and a rest days stepper from 0
    (default) to 7. With `Same day` on, leg N+1 starts on the day leg N ends or up to
    that many days later (`Rest days, up to N`); with it off, 1 to that many days later
    (`Rest days, 1 to N`).
  - Next pick-up within: a slider from the same station (default) to a station within
    about 250 km of where leg N ended, in steps of 25 km. The connection is a hop you make yourself,
    and its distance is the straight line × 1.3, so it carries `~`.
  - Whole trip: min and max days, from the first pick-up to the last return, and max
    km, a limit on the km of the legs. All are empty (any) by default.
  - Round trip (a switch): the last return is within the next pick-up distance of the first
    pick-up.
- **Dates.** An offer is a window: the booking page also accepts a shorter stay or a
  later start inside it. A chain uses the dates that put the most nights on the road,
  then the fewest rest days, then the earliest start, and every `Book` link carries
  those dates. Only days on which some offer starts or ends are used, which skips
  Sundays and holidays.
- **List and map.** One card per sequence of routes, with its dates, total days, km
  driven (the legs, not the connections) and rest days, in the map view's list and in
  the `Trips` view, where each card also has a `Book` link per leg and the hand-overs.
  Both sort by most days (the default), start, end or km driven. The map draws the legs
  solid and the connections dotted. Click a card, a `Trips` card outside its links, or
  `Map` on a `Trips` card to open the chain: its legs turn orange and are numbered on the
  map, and the list shows each leg with its dates and `Book` link and each hand-over in
  between. `← All chains`, Escape or Back closes it; a click on the map does not.
- **Pick from the map.** Click or tap a blue leg or a dotted connection: the list shows
  the chains that use it (`N chains use this leg`), with the leg in orange on the map, and
  opens the chain at once when only one does. The leg filter shows once, as a `Chain uses`
  chip after the other filter chips; its `×`, Escape, `Clear all` or switching to single
  rallies removes it. Clicking a leg or connection of the open chain keeps the chain and marks
  that leg in the list. A click on a station filters to the chains starting there.
- **Filters.** The chips read `Dates`, `Distance`, `Chain starts at` and `Return`, and a
  screen reader hears what they filter: the start date and the week slider limit the
  first pick-up day, the distance filter limits every leg, the pick-up filters apply to
  where the chain starts and the return filters to where it ends.

Limits: the list and the map show the first 200 chains of the current sort order, and
the filter bar counts all of them (`N chains from M trips`). A chain shows only the best dates for its sequence of
routes; narrow the dates to see others. The dates are inferred from the offers, so the
booking page can still refuse a leg, for example on a day a station is closed, and the
page proposes chains from the offers as of the last scan; the booking pages have the
last word. A station is never a pick-up twice in one chain.

### Usage

Output of `python3 roadsurfer-rally.py --help` on Python 3.14. Python 3.8 and 3.9
label the options section `optional arguments:`.

```text
usage: roadsurfer-rally.py [-h] [--to [TO ...]] [--from [ORIGIN ...]]
                           [--start START] [--end END] [--prices]
                           [--map FILE.html] [--json-out FILE.json]
                           [--feeds DIR] [--from-json FILE.json]
                           [--delay DELAY] [--release TAG]
                           [--road-cache FILE.json] [--routing-url URL]
                           [--list]

Query roadsurfer Rally (one-way relocation) offers.

Unofficial API used by booking.roadsurfer.com (stdlib only):
  GET /api/{lang}/rally/stations                 all stations; "name" is in {lang}
  GET /api/{lang}/rally/stations/{id}            station; "returns" = rally destinations
  GET /api/{lang}/rally/timeframes/{from}-{to}   [{startDate, endDate}, ...]
  GET /api/{lang}/rally/search?stations=[[from,to]]&range=[start,end]&currency=EUR
                                                 models + price for an exact timeframe
The X-Requested-Alias header must match the route alias or the API returns 404.

Everything is read from /api/en, except that the station list is also read once for each
page language (LANGS): the localised names go into each record's from/to as "names".

Road distances come from an OSRM server (the public demo server by default), one
table request per pick-up station, and are cached per station pair in a JSON file.

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
  --feeds DIR           write Atom feeds of the offers: all.xml and one
                        from-<station>.xml each
  --from-json FILE.json
                        render --map and --feeds from a --json-out file,
                        without network access
  --delay DELAY         seconds between requests (default 0.5)
  --release TAG         release tag to show in the --map attribution, e.g.
                        v1.2.0
  --road-cache FILE.json
                        cache of road distances per station pair (default
                        road-distances.json)
  --routing-url URL     OSRM server for road distances (default
                        https://router.project-osrm.org)
  --list                list stations and exit
```

## Published map

The workflow [`scan.yml`](.github/workflows/scan.yml) scans on Monday and Thursday at
03:17 UTC, and on manual dispatch, with `--delay 5`. It renders the page from the scan
with the latest release tag (none before the first release) and publishes
`index.html`, `vendor/` and the `feeds/` directory (see "Feeds") to
<https://gjed.github.io/roadsurfer-rally-map/>. The run
also keeps the scanned `offers.json` as the workflow artifact `offers`. When the scan fails, nothing
is deployed and the published page stays at the last good scan. GitHub pauses
scheduled workflows after 60 days without repository activity; a maintainer then
re-enables the scan with `gh workflow enable scan.yml` (or Actions → Enable).

The scan keeps `road-distances.json` between runs, so only new station pairs are
routed (see below).

### Feeds

Each scan also publishes [Atom](https://www.rfc-editor.org/rfc/rfc4287) feeds next to
the page, so a feed reader can tell you about a rally without opening the map:

- <https://gjed.github.io/roadsurfer-rally-map/feeds/all.xml> lists every offer.
- `feeds/from-<slug>.xml` lists the offers of one pick-up station, for example
  `feeds/from-munich.xml`. A station without offers has a feed with no entries, so
  its URL does not disappear.

An entry is one offer window: the title reads
`Munich, DE → Bordeaux, FR · Tue 24 Nov – Tue 1 Dec`, its link is the booking page, and
the summary has the distance (a leading `~` marks an estimate) and the price when the
scan fetched one. The entry's `id` is built from the route and the window, so a reader
shows only the windows it has not seen before; that is what makes an offer "new" with no
state kept between scans. A window that disappears from the next scan disappears from
the feed. `updated` is the time the scan finished. The text is English.

The slug is the station name in lowercase ASCII with hyphens: accents and `ß`, `æ`, `œ`,
`ø`, `ł`, `đ` are folded, every other run of characters becomes one hyphen
(`Zürich Flughafen` is `zurich-flughafen`). When two pick-up stations would share a
slug, both get their country code appended (`neustadt-de`, `neustadt-at`), and a slug
that is still taken gets `-2`, `-3`, in the order of the sorted names. The stations are
the scan's `stations` list plus those of the offers (a data file from before the list
existed has only the latter), so a slug does not change when another station gets an
offer. The map links `all.xml` from its `<head>` and shows an `RSS feed` link to the file of
the chosen pick-up station, from the station table `--map` embeds.

`--feeds DIR` writes the same files locally, from a scan or from a data file, and keeps
other files in `DIR`:

```sh
python3 roadsurfer-rally.py --from-json offers.json --feeds feeds   # no request
```

`feeds/` is git-ignored. A blocked scan writes no feed.

### Road distance cache in S3

The durable copy of `road-distances.json` is the object `road-distances.json` in an S3
bucket (`eu-central-1`, versioned, noncurrent versions expire after 30 days). The bucket
and the role the workflow assumes are managed in the maintainer's AWS account, not in
this repository. The build job of `scan.yml` signs in with GitHub OIDC (no stored
keys), downloads the object before the scan and uploads it after a scan that
succeeded. The role trusts only `main`, so the S3 steps work only on scheduled and
manually dispatched runs from `main`. `release.yml` never reads the bucket.

The workflow takes two Actions variables (Settings → Secrets and variables → Actions
→ Variables): `ROAD_DISTANCE_CACHE_BUCKET`, the bucket name, and
`ROAD_DISTANCE_CACHE_ROLE_ARN`, the ARN of the role. When either is unset, as in a
fork, the S3 steps are skipped.

The scan uses the first copy it finds, in this order:

1. the S3 object;
1. the GitHub Actions cache, restored under the key `road-distances-<run id>` with
   the prefix `road-distances-`; the workflow restores it first and the S3 download
   overwrites it, so the S3 copy wins when there is one;
1. none: the scanner routes every station pair it needs, at one request per second.

The build job runs in its own concurrency group, so two scans never overlap and
overwrite each other's upload. A problem with AWS (credentials, network, access denied, a failed upload) logs a
warning and never fails the scan; a missing object on the first run logs a notice. The
Actions cache is saved as before, so it stays the fallback.

To roll back a bad write, copy an older version of the object back (versions are kept
for 30 days after they are replaced):

```sh
aws s3api list-object-versions --bucket "$BUCKET" --prefix road-distances.json
aws s3api get-object --bucket "$BUCKET" --key road-distances.json \
  --version-id "$VERSION_ID" road-distances.json
aws s3 cp road-distances.json "s3://$BUCKET/road-distances.json"
```

The workflow scans without `--prices`, so the published page shows dates and the
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
newest unexpired `offers` artifact of a `scan.yml` run on `main`, with the new tag
in the map attribution, with the feeds, so code changes reach the map without waiting for the next scan
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
a 404 HTML page. The language in the path matters for one thing: see "Known behaviour".

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
  (`MAX_FAILED`), it exits with status 1 and writes neither the `--json-out` file,
  the `--map` file nor the `--feeds` files.
- `/api/{lang}/rally/stations` answers for `de`, `fr`, `es`, `it`, `nl` and `pt` with
  the same station ids as `en` and a localised `name`, for example `Antwerp` is
  `Antwerpen`, `Anvers`, `Amberes`, `Anversa`, `Antuérpia`. The `name` of 26 to 57 of
  the 112 stations differs from English, depending on the language. `city.name` is
  not localised. The scanner reads the list once for each of the six languages after
  the English one (6 more requests per scan) and joins the answers by station `id`,
  never by name. A language whose request fails falls back to English and counts as a
  failed request.
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
