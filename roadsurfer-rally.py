#!/usr/bin/env python3
"""Query roadsurfer Rally (one-way relocation) offers.

Unofficial API used by booking.roadsurfer.com (stdlib only):
  GET /api/{lang}/rally/stations                 all stations
  GET /api/{lang}/rally/stations/{id}            station; "returns" = rally destinations
  GET /api/{lang}/rally/timeframes/{from}-{to}   [{startDate, endDate}, ...]
  GET /api/{lang}/rally/search?stations=[[from,to]]&range=[start,end]&currency=EUR
                                                 models + price for an exact timeframe
The X-Requested-Alias header must match the route alias or the API returns 404.
"""

import argparse
import http.client
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

BASE = "https://booking.roadsurfer.com/api/en"
DELAY = 0.5  # seconds between requests (sequential, ~2 req/s); see --delay


def get(path, alias, params=None):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "X-Requested-Alias": alias}
    )
    time.sleep(DELAY)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except (OSError, ValueError, http.client.HTTPException) as e:
            code = getattr(e, "code", None)
            # a 4xx other than 429 (e.g. 404 from a wrong alias) won't fix itself
            if attempt == 4 or (code and 400 <= code < 500 and code != 429):
                print(f"ERROR {url}: {e}", file=sys.stderr)
                return None
            time.sleep(5 * (attempt + 1) if code == 429 else 2)


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


def km(a, b):
    """Great-circle distance between two stations (straight line, roads are ~1.3x)."""
    la1, lo1, la2, lo2 = map(
        math.radians,
        (
            a["coordinate"]["latitude"],
            a["coordinate"]["longitude"],
            b["coordinate"]["latitude"],
            b["coordinate"]["longitude"],
        ),
    )
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 12742 * math.asin(math.sqrt(h))


def find_offers(args, stations):
    targets = resolve(stations, args.to) if args.to else None
    origins = resolve(stations, args.origin) if args.origin else set(stations)

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
    if args.map:
        tpl = Path(__file__).with_name("rally-map.template.html").read_text()
        data = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
        Path(args.map).write_text(tpl.replace("/*DATA*/[]", data))
        print(f"map ({len(records)} offers): {Path(args.map).resolve().as_uri()}")


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
        "--delay",
        type=float,
        default=DELAY,
        help="seconds between requests (default %(default)s)",
    )
    p.add_argument("--list", action="store_true", help="list stations and exit")
    args = p.parse_args()
    DELAY = args.delay

    stations = {s["id"]: s for s in get("/rally/stations", "rally.startStations") or []}
    if not stations:
        sys.exit("Could not fetch station list")
    if args.list:
        for s in sorted(
            stations.values(), key=lambda s: (s["city"]["country"], s["name"])
        ):
            print(
                f"{s['id']:>4}  {s['city']['country']}  {s['name']}  ({s['city']['name']})"
            )
        return
    run(args, stations)


if __name__ == "__main__":
    main()
