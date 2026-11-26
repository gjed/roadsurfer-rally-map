#!/usr/bin/env python3
"""Query roadsurfer Rally (one-way relocation) offers.

Unofficial API used by booking.roadsurfer.com (stdlib only):
  GET /api/{lang}/rally/stations                 all stations
  GET /api/{lang}/rally/stations/{id}            station; "returns" = rally destinations
  GET /api/{lang}/rally/timeframes/{from}-{to}   [{startDate, endDate}, ...]
  GET /api/{lang}/rally/search?stations=[[from,to]]&range=[start,end]&currency=EUR
                                                 models + price for an exact timeframe
The X-Requested-Alias header must match the route alias or the API returns 404.

Road distances come from an OSRM server (the public demo server by default), one
table request per pick-up station, and are cached per station pair in a JSON file.
"""

import argparse
import http.client
import json
import math
import random
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

BASE = "https://booking.roadsurfer.com/api/en"
DELAY = 0.5  # seconds between requests (sequential, ~2 req/s); see --delay
JITTER = 0.2  # up to this share of DELAY is added at random to each wait
REQUESTS = FAILED = RATE_LIMITED = 0  # get() calls, calls given up, 429 answers
MAX_FAILED = 0.10  # a scan with a larger failed share is blocked: no files written

# Road distances: OSRM, a different service from roadsurfer. Its demo server allows
# at most 1 request per second and asks for a descriptive User-Agent.
ROUTING_URL = "https://router.project-osrm.org"
ROUTING_DELAY = 1.0  # seconds before each routing request (sequential)
ROUTING_CHUNK = 50  # destinations per table request (the demo server allows 99)
ROUTING_STOP = 3  # consecutive failed routing requests that end routing for the run
ROAD_CACHE = "road-distances.json"
USER_AGENT = "roadsurfer-rally-map (+https://github.com/gjed/roadsurfer-rally-map)"

# Atom feeds (--feeds): the page they are published with, and the fixed tag: URI
# authority and date of the entry ids. Changing either changes every id.
SITE_URL = "https://gjed.github.io/roadsurfer-rally-map/"
FEEDS_URL = SITE_URL + "feeds/"
TAG_PREFIX = "tag:gjed.github.io,2026-11-26:rally:"
ATOM = "http://www.w3.org/2005/Atom"
DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")  # not strftime: locale-free
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun")
MONTHS += ("Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
FOLD = str.maketrans({"ß": "ss", "æ": "ae", "œ": "oe", "ø": "o", "ł": "l", "đ": "d"})
SCAN_TIME = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")


def get(path, alias, params=None):
    global REQUESTS, FAILED, RATE_LIMITED
    REQUESTS += 1
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "X-Requested-Alias": alias}
    )
    time.sleep(DELAY + random.uniform(0, JITTER * DELAY))
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except (OSError, ValueError, http.client.HTTPException) as e:
            code = getattr(e, "code", None)
            if code == 429:
                RATE_LIMITED += 1
            # a 4xx other than 429 (e.g. 404 from a wrong alias) won't fix itself
            if attempt == 4 or (code and 400 <= code < 500 and code != 429):
                print(f"ERROR {url}: {e}", file=sys.stderr)
                FAILED += 1
                return None
            # on a 429 back off for minutes (~1, 2, 3, 4) with jitter
            time.sleep(60 * (attempt + 1) + random.uniform(0, 30) if code == 429 else 2)


def resolve(stations, terms):
    """Match station ids, uppercase country codes (BE) or name/city substrings."""
    out = set()
    for t in terms:
        tl = t.lower()
        hit = {
            s["id"]
            for s in stations.values()
            if t == str(s["id"])
            or (len(t) == 2 and t.isupper() and t == s["city"]["country"])
            or (
                not t.isupper()
                and (tl in s["name"].lower() or tl in s["city"]["name"].lower())
            )
        }
        if not hit:
            sys.exit(f"No station matches '{t}' (use --list)")
        out |= hit
    return out


def origin_ids(args, stations):
    return resolve(stations, args.origin) if args.origin else set(stations)


def find_offers(args, stations):
    targets = resolve(stations, args.to) if args.to else None
    origins = origin_ids(args, stations)

    details = {i: get(f"/rally/stations/{i}", "rally.fetchRoutes") for i in origins}
    routes = [
        (o, d)
        for o, det in details.items()
        if det
        for d in det.get("returns") or []
        if targets is None or d in targets
    ]

    def frames(route):
        o, d = route
        tf = get(f"/rally/timeframes/{o}-{d}", "rally.timeframes") or []
        return [(o, d, f["startDate"][:10], f["endDate"][:10]) for f in tf]

    offers = [x for r in routes for x in frames(r)]
    # keep frames overlapping the requested window
    return sorted(
        {x for x in offers if x[2] <= args.end and x[3] >= args.start},
        key=lambda x: (x[2], x[0], x[1]),
    )


def link(o, d, start, end):
    q = {
        "station": o,
        "end_station": d,
        "start-date": start,
        "end-date": end,
        "currency": "EUR",
    }
    return "https://booking.roadsurfer.com/en/rally/pick?" + urllib.parse.urlencode(q)


def price(o, d, start, end):
    res = (
        get(
            "/rally/search",
            "rally.search",
            {
                "stations": json.dumps([[o, d]]),
                "range": json.dumps([start, end]),
                "currency": "EUR",
            },
        )
        or []
    )
    return (
        ", ".join(
            f"{r['name']} €{r['availability']['price_details']['final']}"
            for r in res
            if r.get("available") and r.get("availability")
        )
        or "n/a"
    )


def run(args, stations):
    offers = find_offers(args, stations)
    records = []
    print(
        f"[{datetime.now():%Y-%m-%d %H:%M}] {len(offers)} offer(s) in {args.start}..{args.end}"
    )
    for o, d, s, e in offers:
        line = f"{s} -> {e}  {stations[o]['name']} ({stations[o]['city']['country']}) -> {stations[d]['name']} ({stations[d]['city']['country']})"
        pr = price(o, d, s, e) if args.prices else ""
        if pr:
            line += f"  [{pr}]"
        records.append(
            {
                "start": s,
                "end": e,
                "price": pr,
                "link": link(o, d, s, e),
                "from": {
                    "name": stations[o]["name"],
                    "cc": stations[o]["city"]["country"],
                    **stations[o]["coordinate"],
                },
                "to": {
                    "name": stations[d]["name"],
                    "cc": stations[d]["city"]["country"],
                    **stations[d]["coordinate"],
                },
            }
        )
        print(line)
        print(f"      {link(o, d, s, e)}")
    return records


def estimate_km(a, b):
    """Great-circle distance x 1.3 in km, to 10 km: the fallback for a pair not routed."""
    r = math.pi / 180
    d_lat, d_lon = (
        (b["latitude"] - a["latitude"]) * r,
        (b["longitude"] - a["longitude"]) * r,
    )
    h = (
        math.sin(d_lat / 2) ** 2
        + math.cos(a["latitude"] * r)
        * math.cos(b["latitude"] * r)
        * math.sin(d_lon / 2) ** 2
    )
    return int(12742 * math.asin(math.sqrt(h)) * 1.3 / 10 + 0.5) * 10


def point_key(p):
    return f"{p['latitude']:.5f},{p['longitude']:.5f}"


def pair_key(a, b):
    """Cache key: the coordinates the router uses, pick-up first (roads are one-way)."""
    return f"{point_key(a)}>{point_key(b)}"


def load_road_cache(path):
    """Cached km per pair key; a missing or unreadable file is an empty cache."""
    try:
        pairs = json.loads(Path(path).read_text(encoding="utf-8"))["pairs"]
        return {
            k: v
            for k, v in pairs.items()
            if isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0
        }
    except FileNotFoundError:
        return {}
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        print(f"warning: ignoring road distance cache {path}: {e!r}", file=sys.stderr)
        return {}


def road_table(base, origin, dests):
    """Driving metres from origin to each of dests (None where no route): one OSRM request."""
    coords = ";".join(f"{p['longitude']},{p['latitude']}" for p in [origin, *dests])
    url = (
        f"{base.rstrip('/')}/table/v1/driving/{coords}?sources=0"
        f"&destinations={';'.join(str(i) for i in range(1, len(dests) + 1))}"
        "&annotations=distance"
    )
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    row = data["distances"][0]
    if data.get("code") != "Ok" or len(row) != len(dests):
        raise ValueError(f"unexpected routing answer: {data.get('code')}")
    return row


def add_road_km(records, cache_path, base):
    """Set km and km_estimated on every record from the cache, routing missing pairs.

    A pair that cannot be routed gets the estimate, marked km_estimated, and is not
    cached, so the next run tries it again. Routing never raises: it stops for the run
    after a 429 or ROUTING_STOP failed requests in a row.
    """
    cache = load_road_cache(cache_path)
    known = len(cache)
    todo = {}  # pick-up point key -> (point, {pair key: return point})
    for r in records:
        key = pair_key(r["from"], r["to"])
        if key not in cache:
            todo.setdefault(point_key(r["from"]), (r["from"], {}))[1][key] = r["to"]
    pairs = sum(len(d) for _, d in todo.values())
    requests = failed = streak = 0
    stopped = False
    for origin, dests in todo.values():
        items = list(dests.items())
        for i in range(0, len(items), ROUTING_CHUNK):
            if stopped:
                break
            chunk = items[i : i + ROUTING_CHUNK]
            time.sleep(ROUTING_DELAY)
            requests += 1
            try:
                row = road_table(base, origin, [d for _, d in chunk])
            except (
                OSError,
                ValueError,
                KeyError,
                TypeError,
                http.client.HTTPException,
            ) as e:
                failed += 1
                streak += 1
                stopped = streak >= ROUTING_STOP or getattr(e, "code", None) == 429
                print(f"warning: routing request failed: {e!r}", file=sys.stderr)
                continue
            streak = 0
            for (key, _), metres in zip(chunk, row):
                if isinstance(metres, (int, float)) and not isinstance(metres, bool):
                    cache[key] = round(metres / 1000)
    estimated = 0
    for r in records:
        km = cache.get(pair_key(r["from"], r["to"]))
        r["km"] = estimate_km(r["from"], r["to"]) if km is None else km
        r["km_estimated"] = km is None
        estimated += km is None
    if len(cache) > known:
        try:
            Path(cache_path).write_text(
                json.dumps({"pairs": cache}, indent=1, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except OSError as e:
            print(f"warning: could not write {cache_path}: {e!r}", file=sys.stderr)
    print(
        f"road distances: {len({pair_key(r['from'], r['to']) for r in records})} pairs, "
        f"{pairs} not cached, {requests} routing requests, {failed} failed, "
        f"{estimated} offers estimated"
    )


def embed(value):
    """JSON for an inline <script>: `</` is escaped so it can't close the tag."""
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def render(records, path, scan=None, release=None):
    """Write the map page with the records, scan metadata, the station feeds and the
    release tag (or null)."""
    tpl = (
        Path(__file__).with_name("rally-map.template.html").read_text(encoding="utf-8")
    )
    page = tpl.replace("/*DATA*/[]", embed(records))
    page = page.replace("/*SCAN*/null", embed(scan))
    # [name, cc, slug] of the stations write_feeds writes a feed for: the page links
    # feeds/from-<slug>.xml and never works out a slug itself
    slugs = station_slugs(feed_stations(records, scan))
    page = page.replace(
        "/*FEEDS*/null",
        embed([[n, cc, slug] for (n, cc), slug in sorted(slugs.items())]),
    )
    Path(path).write_text(
        page.replace("/*RELEASE*/null", embed(release)), encoding="utf-8"
    )
    print(f"map ({len(records)} offers): {Path(path).resolve().as_uri()}")


def slugify(name):
    """ASCII, lowercase, hyphens: `Zürich Flughafen` becomes `zurich-flughafen`."""
    text = unicodedata.normalize("NFKD", name.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", text.translate(FOLD)).strip("-") or "station"


def station_slugs(stations):
    """{(name, cc): slug}. Stations with the same base slug get `-<cc>`; a slug still
    taken gets `-2`, `-3`, ... in sorted order. Depends only on the set of stations.
    write_feeds passes every station the scan knows, not only those with offers."""
    base = {s: slugify(s[0]) for s in stations}
    shared = defaultdict(int)
    for slug in base.values():
        shared[slug] += 1
    slugs = {}
    for s in sorted(stations):
        slug = base[s] if shared[base[s]] == 1 else f"{base[s]}-{s[1].lower()}"
        free, n = slug, 2
        while free in slugs.values():
            free, n = f"{slug}-{n}", n + 1
        slugs[s] = free
    return slugs


def short_date(iso):
    d = date.fromisoformat(iso)
    return f"{DAYS[d.weekday()]} {d.day} {MONTHS[d.month - 1]}"


def place(station):
    return f"{station['name']}, {station['cc']}"


def km_text(r):
    km, estimated = r.get("km"), r.get("km_estimated")
    if km is None:  # a record from before road distances: the page's estimate
        km, estimated = estimate_km(r["from"], r["to"]), True
    return f"{'~' if estimated else ''}{km:,} km"


def atom_entry(feed, r, updated):
    entry = ET.SubElement(feed, "entry")
    enc = urllib.parse.quote
    ids = (enc(f"{r[k]['name']},{r[k]['cc']}", safe="") for k in ("from", "to"))
    ET.SubElement(entry, "id").text = TAG_PREFIX + ":".join(
        (*ids, r["start"], r["end"])
    )
    ET.SubElement(entry, "title").text = (
        f"{place(r['from'])} → {place(r['to'])} · "
        f"{short_date(r['start'])} – {short_date(r['end'])}"
    )
    ET.SubElement(entry, "link", rel="alternate", href=r["link"])
    ET.SubElement(entry, "updated").text = updated
    parts = [f"{r['start']} to {r['end']}", f"Distance {km_text(r)}"]
    if r.get("price") and r["price"] != "n/a":
        parts.append(f"Price {r['price']}")
    ET.SubElement(entry, "summary").text = " · ".join(parts)


def atom_feed(name, title, records, updated):
    url = FEEDS_URL + name
    feed = ET.Element("feed", xmlns=ATOM)
    ET.SubElement(feed, "id").text = url
    ET.SubElement(feed, "title").text = title
    ET.SubElement(feed, "link", rel="self", type="application/atom+xml", href=url)
    ET.SubElement(feed, "link", rel="alternate", type="text/html", href=SITE_URL)
    author = ET.SubElement(feed, "author")
    ET.SubElement(author, "name").text = "roadsurfer-rally-map"
    ET.SubElement(author, "uri").text = SITE_URL
    ET.SubElement(feed, "updated").text = updated
    for r in records:
        atom_entry(feed, r, updated)
    return ET.ElementTree(feed)


def scan_stations(scan):
    """(name, cc) of the pick-up stations a scan recorded; junk entries are ignored."""
    listed = (scan or {}).get("stations")
    return {
        (s["name"], s["cc"])
        for s in (listed if isinstance(listed, list) else [])
        if isinstance(s, dict)
        and isinstance(s.get("name"), str)
        and isinstance(s.get("cc"), str)
    }


def feed_stations(records, scan=None):
    """{(name, cc): its records} for every pick-up station that gets a feed: the scan's
    list and those of the records. A station without offers has an empty list."""
    by_station = defaultdict(list)
    for st in scan_stations(scan):
        by_station.setdefault(st, [])
    for r in records:
        by_station[(r["from"]["name"], r["from"]["cc"])].append(r)
    return by_station


def write_feeds(records, directory, scan=None):
    """Write all.xml and one from-<slug>.xml per pick-up station into the directory.
    The stations are the scan's list and those of the records: a station without
    offers gets a feed with no entries."""
    finished = (scan or {}).get("finished_at")
    if not (isinstance(finished, str) and SCAN_TIME.match(finished)):
        finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    by_station = feed_stations(records, scan)
    feeds = {"all.xml": ("roadsurfer Rally offers", records)}
    for st, slug in station_slugs(by_station).items():
        title = f"roadsurfer Rally offers from {st[0]}, {st[1]}"
        feeds[f"from-{slug}.xml"] = (title, by_station[st])
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    for name, (title, recs) in feeds.items():
        tree = atom_feed(name, title, recs, finished)
        tree.write(out / name, encoding="utf-8", xml_declaration=True)
    print(
        f"feeds ({len(feeds)} files, {len(records)} offers): {out.resolve().as_uri()}"
    )


def summary(started):
    """Print the request counts and duration; return True if the scan is blocked."""
    secs = round(time.monotonic() - started)
    share = FAILED / REQUESTS if REQUESTS else 0
    print(
        f"scan: {REQUESTS} requests, {FAILED} failed ({share:.1%}), "
        f"{RATE_LIMITED} rate-limited (429), duration {secs // 60}m{secs % 60:02d}s"
    )
    return share > MAX_FAILED


def main():
    global DELAY
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--to", nargs="*", help="destination stations (id, name, city or country code)"
    )
    p.add_argument(
        "--from", dest="origin", nargs="*", help="origin stations (default: all)"
    )
    p.add_argument(
        "--start", default=date.today().isoformat(), help="window start YYYY-MM-DD"
    )
    p.add_argument("--end", default="2099-12-31", help="window end YYYY-MM-DD")
    p.add_argument(
        "--prices", action="store_true", help="fetch models and price per offer"
    )
    p.add_argument(
        "--map",
        metavar="FILE.html",
        help="write a self-contained map of the offers (add --prices for models/price)",
    )
    p.add_argument(
        "--json-out",
        metavar="FILE.json",
        help='write the scan as {"scan": {...}, "offers": [...]}',
    )
    p.add_argument(
        "--feeds",
        metavar="DIR",
        help="write Atom feeds of the offers: all.xml and one from-<station>.xml each",
    )
    p.add_argument(
        "--from-json",
        metavar="FILE.json",
        help="render --map and --feeds from a --json-out file, without network access",
    )
    p.add_argument(
        "--delay",
        type=float,
        default=DELAY,
        help="seconds between requests (default %(default)s)",
    )
    p.add_argument(
        "--release",
        metavar="TAG",
        help="release tag to show in the --map attribution, e.g. v1.2.0",
    )
    p.add_argument(
        "--road-cache",
        metavar="FILE.json",
        default=ROAD_CACHE,
        help="cache of road distances per station pair (default %(default)s)",
    )
    p.add_argument(
        "--routing-url",
        metavar="URL",
        default=ROUTING_URL,
        help="OSRM server for road distances (default %(default)s)",
    )
    p.add_argument("--list", action="store_true", help="list stations and exit")
    args = p.parse_args()
    DELAY = args.delay
    args.release = args.release or None  # --release "" (no release yet) shows no tag
    if args.release and not args.map:
        p.error("--release requires --map")

    if args.from_json:
        if not (args.map or args.feeds):
            p.error("--from-json requires --map or --feeds")
        scan_opts = (args.list, args.json_out, args.prices)
        if any(scan_opts) or args.origin is not None or args.to is not None:
            p.error(
                "--from-json only renders: drop --list/--json-out/--from/--to/--prices"
            )
        try:
            data = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
            offers = data["offers"]
        except (OSError, ValueError, KeyError, TypeError) as e:
            sys.exit(f"Could not read --from-json {args.from_json}: {e!r}")
        # files written before the scan metadata existed have no "scan" key
        scan = data.get("scan")
        scan = scan if isinstance(scan, dict) else None
        if args.map:
            render(offers, args.map, scan, args.release)
        if args.feeds:
            write_feeds(offers, args.feeds, scan)
        return

    if args.list and (args.map or args.json_out or args.feeds):
        p.error("--list only lists stations: drop --map/--json-out/--feeds")

    started = time.monotonic()
    stations = {s["id"]: s for s in get("/rally/stations", "rally.startStations") or []}
    if not stations:
        if not args.list:
            summary(started)
        sys.exit("Could not fetch station list")
    if args.list:
        for s in sorted(
            stations.values(), key=lambda s: (s["city"]["country"], s["name"])
        ):
            print(
                f"{s['id']:>4}  {s['city']['country']}  {s['name']}  ({s['city']['name']})"
            )
        return
    records = run(args, stations)
    scan = {
        # timezone.utc, not datetime.UTC (3.11+): the script supports Python 3.8
        "finished_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "offers": len(records),
        "requests": REQUESTS,
        "failed": FAILED,
        "rate_limited": RATE_LIMITED,
        "start": args.start,
        "end": args.end,
        "from": args.origin,
        "to": args.to,
        # the pick-up stations asked about, so a station without offers keeps its feed
        "stations": [
            {"name": stations[i]["name"], "cc": stations[i]["city"]["country"]}
            for i in sorted(origin_ids(args, stations))
        ],
    }
    if summary(started):
        sys.exit(
            f"Scan blocked: {FAILED} of {REQUESTS} requests failed "
            f"(more than {MAX_FAILED:.0%}); not writing any file"
        )
    if args.json_out or args.map or args.feeds:
        add_road_km(records, args.road_cache, args.routing_url)
    if args.json_out:
        out = json.dumps(
            {"scan": scan, "offers": records}, ensure_ascii=False, indent=1
        )
        Path(args.json_out).write_text(out + "\n", encoding="utf-8")
        print(f"data ({len(records)} offers): {Path(args.json_out).resolve()}")
    if args.map:
        render(records, args.map, scan, args.release)
    if args.feeds:
        write_feeds(records, args.feeds, scan)


if __name__ == "__main__":
    main()
