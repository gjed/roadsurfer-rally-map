#!/usr/bin/env python3
"""Query/monitor roadsurfer Rally (one-way relocation) offers.

Unofficial API used by booking.roadsurfer.com (stdlib only):
  GET /api/{lang}/rally/stations                 all stations
  GET /api/{lang}/rally/stations/{id}            station; "returns" = rally destinations
  GET /api/{lang}/rally/timeframes/{from}-{to}   [{startDate, endDate}, ...]
  GET /api/{lang}/rally/search?stations=[[from,to]]&range=[start,end]&currency=EUR
                                                 models + price for an exact timeframe
The X-Requested-Alias header must match the route alias or the API returns 404.
"""

import argparse
import json
import math
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

BASE = "https://booking.roadsurfer.com/api/en"
DELAY = 0.5  # seconds between requests (sequential, ~2 req/s); see --delay
STATE = Path(__file__).with_name(".roadsurfer-rally-seen.json")


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
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 4:
                print(f"ERROR {url}: {e}", file=sys.stderr)
                return None
            time.sleep(5 * (attempt + 1) if getattr(e, "code", None) == 429 else 2)


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


def detour(stations, via, o, d):
    """Extra km to pass through `via` on the way from o to d."""
    so, sd, sv = stations[o], stations[d], stations[via]
    return km(so, sv) + km(sv, sd) - km(so, sd)


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
        if args.via is None or detour(stations, args.via, o, d) <= args.detour
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
    seen = set(json.loads(STATE.read_text())) if STATE.exists() else set()
    new = []
    records = []
    print(
        f"[{datetime.now():%Y-%m-%d %H:%M}] {len(offers)} offer(s) in {args.start}..{args.end}"
    )
    for o, d, s, e in offers:
        key = f"{o}-{d}-{s}-{e}"
        flag = "NEW " if key not in seen else "    "
        if key not in seen:
            new.append(key)
        via = f"  +{detour(stations, args.via, o, d):.0f}km" if args.via else ""
        line = f"{flag}{s} -> {e}{via}  {stations[o]['name']} ({stations[o]['city']['country']}) -> {stations[d]['name']} ({stations[d]['city']['country']})"
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
    if new and seen and args.notify:
        subprocess.run(
            ["notify-send", "roadsurfer Rally", f"{len(new)} new offer(s)"], check=False
        )
    STATE.write_text(json.dumps(sorted(seen | set(new))))
    if args.map:
        tpl = Path(__file__).with_name("rally-map.template.html").read_text()
        Path(args.map).write_text(
            tpl.replace("/*DATA*/[]", json.dumps(records, ensure_ascii=False))
        )
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
    p.add_argument("--via", help="only routes passing near this station (id or name)")
    p.add_argument(
        "--detour",
        type=int,
        default=150,
        help="max extra straight-line km to pass by --via (default 150)",
    )
    p.add_argument(
        "--start", default=date.today().isoformat(), help="window start YYYY-MM-DD"
    )
    p.add_argument("--end", default="2099-12-31", help="window end YYYY-MM-DD")
    p.add_argument(
        "--prices", action="store_true", help="fetch models and price per offer"
    )
    p.add_argument("--watch", type=int, metavar="MIN", help="repeat every MIN minutes")
    p.add_argument("--notify", action="store_true", help="notify-send on new offers")
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
    if args.via:
        via = resolve(stations, [args.via])
        if len(via) != 1:
            sys.exit(
                f"--via '{args.via}' matches {len(via)} stations, use an id (see --list)"
            )
        args.via = via.pop()
    while True:
        run(args, stations)
        if not args.watch:
            break
        time.sleep(args.watch * 60)


if __name__ == "__main__":
    main()
