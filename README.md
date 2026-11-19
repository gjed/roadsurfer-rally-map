# roadsurfer Rally map

Finds [roadsurfer Rally](https://booking.roadsurfer.com/en/rally) one-way campervan
relocation offers and shows them on a map.

`roadsurfer-rally.py` asks the roadsurfer booking API for every Rally route and its
timeframes, prints the offers with booking links and, with `--map`, writes a
self-contained HTML page. The page uses Leaflet and draws each offer as a line from
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

Then open `index.html` in a browser. The page loads Leaflet and the map tiles from
public CDNs, so viewing it needs an internet connection. A full scan makes about
850 sequential requests and takes several minutes.

Other useful options:

```sh
python3 roadsurfer-rally.py --list                       # list stations and exit
python3 roadsurfer-rally.py --from BE --to Lisbon        # filter by country code or name
python3 roadsurfer-rally.py --start 2026-06-01 --end 2026-06-30
python3 roadsurfer-rally.py --prices --map index.html    # add models and prices
python3 roadsurfer-rally.py --help
```

Each run stores the offers it has seen in `.roadsurfer-rally-seen.json` and marks
offers it has not seen before as `NEW`. Git ignores this file and the generated
`index.html`.

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
