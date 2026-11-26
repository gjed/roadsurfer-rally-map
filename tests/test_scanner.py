"""Offline unit tests for roadsurfer-rally.py (stdlib unittest, no network)."""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "roadsurfer-rally.py"
FIXTURE = ROOT / "tests" / "fixtures" / "offers.json"

# the file name has a hyphen, so it cannot be imported by name
_spec = importlib.util.spec_from_file_location("roadsurfer_rally", SCRIPT)
rally = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rally)


ROAD_TABLE = rally.road_table


def station(id, name, city, country):
    return {"id": id, "name": name, "city": {"name": city, "country": country}}


STATIONS = {
    s["id"]: s
    for s in (
        station(1, "Munich", "Munich", "DE"),
        station(2, "Frankfurt Airport", "Frankfurt am Main", "DE"),
        station(3, "Brussels", "Brussels", "BE"),
        station(4, "Lisbon", "Lisboa", "PT"),
    )
}


SCAN = {
    "finished_at": "2026-11-18T03:12:05Z",
    "offers": 3,
    "requests": 850,
    "failed": 2,
    "rate_limited": 1,
    "start": "2026-11-18",
    "end": "2099-12-31",
    "from": ["</script>"],
    "to": None,
}


def page_data(html, name="DATA"):
    """Return the JSON text embedded in the page's `const NAME = ...;` line."""
    prefix = f"const {name} = "
    line = next(x for x in html.splitlines() if x.startswith(prefix))
    return line[len(prefix) :].rstrip(";")


class ResolveTest(unittest.TestCase):
    def test_id(self):
        self.assertEqual(rally.resolve(STATIONS, ["3"]), {3})

    def test_country_code(self):
        self.assertEqual(rally.resolve(STATIONS, ["DE"]), {1, 2})

    def test_name_substring_case_insensitive(self):
        self.assertEqual(rally.resolve(STATIONS, ["airport"]), {2})

    def test_city_substring(self):
        self.assertEqual(rally.resolve(STATIONS, ["lisboa"]), {4})

    def test_union_of_terms(self):
        self.assertEqual(rally.resolve(STATIONS, ["1", "BE"]), {1, 3})

    def test_no_match_exits(self):
        with self.assertRaises(SystemExit) as cm:
            rally.resolve(STATIONS, ["nowhere"])
        self.assertIn("nowhere", str(cm.exception.code))


class LinkTest(unittest.TestCase):
    def test_query_params(self):
        url = urllib.parse.urlsplit(rally.link(1, 116, "2027-01-09", "2027-01-16"))
        self.assertEqual(
            (url.scheme, url.netloc, url.path),
            ("https", "booking.roadsurfer.com", "/en/rally/pick"),
        )
        self.assertEqual(
            urllib.parse.parse_qs(url.query),
            {
                "station": ["1"],
                "end_station": ["116"],
                "start-date": ["2027-01-09"],
                "end-date": ["2027-01-16"],
                "currency": ["EUR"],
            },
        )


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.offers = json.loads(FIXTURE.read_text(encoding="utf-8"))["offers"]
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.out = Path(tmp.name) / "index.html"
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            rally.render(self.offers, self.out)
        self.stdout = stdout.getvalue()
        self.html = self.out.read_text(encoding="utf-8")

    def test_placeholder_replaced(self):
        self.assertNotIn("/*DATA*/[]", self.html)

    def test_offer_count(self):
        self.assertEqual(len(json.loads(page_data(self.html))), len(self.offers))
        self.assertIn(f"({len(self.offers)} offers)", self.stdout)

    def test_script_close_is_escaped(self):
        names = [r["to"]["name"] for r in self.offers]
        self.assertTrue(any("</script>" in n for n in names), "fixture lacks `</`")
        data = page_data(self.html)
        self.assertNotIn("</", data)
        self.assertIn("<\\/script>", data)
        # the escaped JSON still decodes to the original records
        self.assertEqual(json.loads(data), self.offers)

    def test_no_scan_metadata(self):
        self.assertNotIn("/*SCAN*/null", self.html)
        self.assertIsNone(json.loads(page_data(self.html, "SCAN")))

    def test_scan_metadata(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rally.render(self.offers, self.out, SCAN)
        html = self.out.read_text(encoding="utf-8")
        scan = page_data(html, "SCAN")
        self.assertNotIn("</", scan)
        self.assertEqual(json.loads(scan), SCAN)
        self.assertEqual(json.loads(page_data(html)), self.offers)

    def test_no_release(self):
        self.assertNotIn("/*RELEASE*/null", self.html)
        self.assertIsNone(json.loads(page_data(self.html, "RELEASE")))

    def test_release(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rally.render(self.offers, self.out, SCAN, "v1.3.0</script>")
        html = self.out.read_text(encoding="utf-8")
        release = page_data(html, "RELEASE")
        self.assertNotIn("</", release)
        self.assertEqual(json.loads(release), "v1.3.0</script>")
        self.assertEqual(json.loads(page_data(html, "SCAN")), SCAN)
        self.assertEqual(json.loads(page_data(html)), self.offers)


class FindOffersTest(unittest.TestCase):
    ROUTES: ClassVar = {1: {"returns": [3, 4]}, 2: {"returns": [3]}}
    FRAMES: ClassVar = {
        "1-3": [("2026-11-20", "2026-11-27"), ("2026-12-10", "2026-12-17")],
        "1-4": [("2026-12-01", "2026-12-05"), ("2026-11-25", "2026-12-01")],
        "2-3": [("2026-12-31", "2027-01-07"), ("2026-11-28", "2026-11-30")],
    }

    def fake_get(self, path, alias, params=None):
        kind, _, key = path.rpartition("/")
        if kind == "/rally/stations":
            return self.ROUTES.get(int(key))
        if kind == "/rally/timeframes":
            return [
                {"startDate": s + "T00:00:00+00:00", "endDate": e + "T00:00:00+00:00"}
                for s, e in self.FRAMES.get(key, [])
            ]
        raise AssertionError(f"unexpected request {path}")

    def find(self, start, end, origin=None, to=None):
        args = SimpleNamespace(start=start, end=end, origin=origin, to=to)
        with mock.patch.object(rally, "get", side_effect=self.fake_get):
            return rally.find_offers(args, STATIONS)

    def test_window_overlap_and_order(self):
        self.assertEqual(
            self.find("2026-11-27", "2026-12-01"),
            [
                (1, 3, "2026-11-20", "2026-11-27"),  # ends on window start
                (1, 4, "2026-11-25", "2026-12-01"),
                (2, 3, "2026-11-28", "2026-11-30"),
                (1, 4, "2026-12-01", "2026-12-05"),  # starts on window end
            ],
        )

    def test_frames_outside_window_dropped(self):
        self.assertEqual(self.find("2027-02-01", "2027-03-01"), [])

    def test_origin_and_destination_filter(self):
        self.assertEqual(
            self.find("2026-01-01", "2099-12-31", origin=["1"], to=["PT"]),
            [
                (1, 4, "2026-11-25", "2026-12-01"),
                (1, 4, "2026-12-01", "2026-12-05"),
            ],
        )


class ScanMetadataTest(unittest.TestCase):
    """A scan writes its metadata next to the offers and into the page."""

    def fake_get(self, path, alias, params=None):
        if path == "/rally/stations":
            return [
                {**s, "coordinate": {"latitude": 50.0, "longitude": 9.0}}
                for s in STATIONS.values()
            ]
        if path == "/rally/stations/1":
            return {"returns": [3]}
        if path == "/rally/timeframes/1-3":
            return [{"startDate": "2026-12-01T00:00", "endDate": "2026-12-05T00:00"}]
        raise AssertionError(f"unexpected request {path}")

    def test_json_out_and_map(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out, page = Path(tmp.name) / "offers.json", Path(tmp.name) / "index.html"
        argv = ["x", "--from", "1", "--start", "2026-11-01"]
        argv += ["--json-out", str(out), "--map", str(page)]
        fake_get = mock.patch.object(rally, "get", side_effect=self.fake_get)
        fake_road = mock.patch.object(rally, "road_table", return_value=[0])
        counters = mock.patch.multiple(rally, REQUESTS=40, FAILED=3, RATE_LIMITED=2)
        args, quiet = mock.patch.object(sys, "argv", argv), io.StringIO()
        argv += ["--road-cache", str(Path(tmp.name) / "road.json")]
        fake_sleep = mock.patch.object(rally.time, "sleep")
        out_cm = contextlib.redirect_stdout(quiet)
        with fake_get, fake_road, fake_sleep, counters, args, out_cm:
            rally.main()
        data = json.loads(out.read_text(encoding="utf-8"))
        html = page.read_text(encoding="utf-8")
        self.assertEqual(json.loads(page_data(html, "SCAN")), data["scan"])
        scan = data["scan"]
        self.assertRegex(scan.pop("finished_at"), r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertEqual(
            scan,
            {
                "offers": 1,
                "requests": 40,
                "failed": 3,
                "rate_limited": 2,
                "start": "2026-11-01",
                "end": "2099-12-31",
                "from": ["1"],
                "to": None,
                "stations": [{"name": "Munich", "cc": "DE"}],
            },
        )
        self.assertEqual(len(data["offers"]), 1)
        self.assertEqual(data["offers"][0]["km"], 0)
        self.assertIs(data["offers"][0]["km_estimated"], False)


class FromJsonTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def run_cli(self, src, *extra):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--from-json", str(src)]
            + ["--map", str(self.dir / "index.html"), *extra],
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_fails(self, src):
        r = self.run_cli(src)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Could not read --from-json", r.stderr)
        self.assertFalse((self.dir / "index.html").exists())

    def test_missing_file(self):
        self.assert_fails(self.dir / "missing.json")

    def test_bad_json(self):
        bad = self.dir / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        self.assert_fails(bad)

    def test_missing_offers_key(self):
        empty = self.dir / "empty.json"
        empty.write_text('{"data": []}', encoding="utf-8")
        self.assert_fails(empty)

    def page_scan(self):
        html = (self.dir / "index.html").read_text(encoding="utf-8")
        return json.loads(page_data(html, "SCAN"))

    def test_fixture_renders(self):
        # the fixture predates the scan metadata: the page gets SCAN = null
        r = self.run_cli(FIXTURE)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNone(self.page_scan())

    def test_scan_metadata_carried_over(self):
        offers = json.loads(FIXTURE.read_text(encoding="utf-8"))["offers"]
        src = self.dir / "scan.json"
        src.write_text(json.dumps({"scan": SCAN, "offers": offers}), encoding="utf-8")
        r = self.run_cli(src)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.page_scan(), SCAN)

    def page_release(self):
        html = (self.dir / "index.html").read_text(encoding="utf-8")
        return json.loads(page_data(html, "RELEASE"))

    def test_release_option(self):
        r = self.run_cli(FIXTURE, "--release", "v1.3.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.page_release(), "v1.3.0")

    def test_empty_release_is_no_release(self):
        # scan.yml passes --release "" before the first release
        r = self.run_cli(FIXTURE, "--release", "")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNone(self.page_release())

    def test_release_requires_map(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--release", "v1.3.0", "--list"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(r.returncode, 2)
        self.assertIn("--release requires --map", r.stderr)

    def test_malformed_scan_ignored(self):
        src = self.dir / "odd.json"
        src.write_text('{"scan": "yesterday", "offers": []}', encoding="utf-8")
        r = self.run_cli(src)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNone(self.page_scan())


A = {"name": "Munich", "cc": "DE", "latitude": 48.204, "longitude": 11.586}
B = {"name": "Bordeaux", "cc": "FR", "latitude": 44.821, "longitude": -0.693}
C = {"name": "Bilbao", "cc": "ES", "latitude": 43.2876667, "longitude": -2.878791}


def offer(a, b, start="2026-12-01"):
    return {
        "start": start,
        "end": "2026-12-08",
        "price": "",
        "link": "x",
        "from": a,
        "to": b,
    }


class RoadDistanceTest(unittest.TestCase):
    """Road km per station pair: cache, one routing request per pick-up, fallback."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.cache = Path(tmp.name) / "road.json"
        self.calls = []
        for p in (
            mock.patch.object(rally, "road_table", side_effect=self.table),
            mock.patch.object(rally.time, "sleep"),
            mock.patch.object(sys, "stderr", io.StringIO()),
        ):
            p.start()
            self.addCleanup(p.stop)
        self.sleep = rally.time.sleep
        self.fail_with = None

    def table(self, base, origin, dests):
        self.calls.append((base, origin["name"], [d["name"] for d in dests]))
        if self.fail_with:
            raise self.fail_with
        return [1_000_000 + 1000 * i for i, _ in enumerate(dests)]

    def run_roads(self, records):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rally.add_road_km(records, self.cache, "http://osrm.test")
        return out.getvalue()

    def cached(self):
        return json.loads(self.cache.read_text(encoding="utf-8"))["pairs"]

    def test_miss_routes_once_per_pickup_and_caches(self):
        records = [offer(A, B), offer(A, C), offer(A, B, "2026-12-09"), offer(B, A)]
        out = self.run_roads(records)
        self.assertEqual(
            self.calls,
            [
                ("http://osrm.test", "Munich", ["Bordeaux", "Bilbao"]),
                ("http://osrm.test", "Bordeaux", ["Munich"]),
            ],
        )
        self.assertEqual(
            [(r["km"], r["km_estimated"]) for r in records],
            [(1000, False), (1001, False), (1000, False), (1000, False)],
        )
        self.assertEqual(len(self.cached()), 3)
        self.assertIn("2 routing requests", out)
        self.assertEqual(self.sleep.call_count, 2)

    def test_hit_makes_no_request(self):
        self.run_roads([offer(A, B), offer(B, A)])
        self.calls.clear()
        records = [offer(A, B, "2027-01-01"), offer(B, A)]
        out = self.run_roads(records)
        self.assertEqual(self.calls, [])
        self.assertEqual([r["km"] for r in records], [1000, 1000])
        self.assertIn("0 routing requests", out)

    def test_only_new_pairs_are_requested(self):
        self.run_roads([offer(A, B)])
        self.calls.clear()
        self.run_roads([offer(A, B), offer(A, C)])
        self.assertEqual(self.calls, [("http://osrm.test", "Munich", ["Bilbao"])])

    def test_direction_is_part_of_the_key(self):
        self.assertNotEqual(rally.pair_key(A, B), rally.pair_key(B, A))
        self.run_roads([offer(A, B)])
        self.run_roads([offer(B, A)])
        self.assertEqual(len(self.calls), 2)

    def test_chunks(self):
        dests = [
            {**B, "latitude": 40 + i / 1000} for i in range(rally.ROUTING_CHUNK + 1)
        ]
        self.run_roads([offer(A, d) for d in dests])
        self.assertEqual([len(c[2]) for c in self.calls], [rally.ROUTING_CHUNK, 1])

    def test_failure_falls_back_to_estimate(self):
        self.fail_with = OSError("unreachable")
        records = [offer(A, B)]
        out = self.run_roads(records)
        self.assertEqual(records[0]["km"], rally.estimate_km(A, B))
        self.assertIs(records[0]["km_estimated"], True)
        self.assertFalse(self.cache.exists())
        self.assertIn("1 failed", out)
        self.assertIn("1 offers estimated", out)

    def test_failure_is_retried_next_run(self):
        self.fail_with = OSError("unreachable")
        self.run_roads([offer(A, B)])
        self.fail_with = None
        records = [offer(A, B)]
        self.run_roads(records)
        self.assertEqual(len(self.calls), 2)
        self.assertIs(records[0]["km_estimated"], False)

    def test_unroutable_pair_is_estimated_and_not_cached(self):
        with mock.patch.object(rally, "road_table", return_value=[None, 5000]):
            records = [offer(A, B), offer(A, C)]
            self.run_roads(records)
        self.assertEqual([r["km_estimated"] for r in records], [True, False])
        self.assertEqual(list(self.cached().values()), [5])

    def test_rate_limit_stops_routing(self):
        self.fail_with = urllib.error.HTTPError("u", 429, "slow down", {}, None)
        records = [offer(A, B), offer(B, A), offer(C, A)]
        self.run_roads(records)
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(all(r["km_estimated"] for r in records))

    def test_repeated_failures_stop_routing(self):
        self.fail_with = OSError("unreachable")
        origins = [{**A, "latitude": 40 + i} for i in range(10)]
        self.run_roads([offer(o, B) for o in origins])
        self.assertEqual(len(self.calls), rally.ROUTING_STOP)

    def test_short_answer_is_a_failure(self):
        with mock.patch.object(rally, "road_table", side_effect=ValueError("short")):
            records = [offer(A, B)]
            self.run_roads(records)
        self.assertIs(records[0]["km_estimated"], True)

    def test_unreadable_cache_is_ignored(self):
        self.cache.write_text("{not json", encoding="utf-8")
        records = [offer(A, B)]
        self.run_roads(records)
        self.assertIs(records[0]["km_estimated"], False)
        self.assertEqual(len(self.cached()), 1)

    def test_junk_cache_entries_are_dropped(self):
        key = rally.pair_key(A, B)
        junk = {"pairs": {key: "far", rally.pair_key(B, A): -5, "x": True}}
        self.cache.write_text(json.dumps(junk), encoding="utf-8")
        self.assertEqual(rally.load_road_cache(self.cache), {})

    def test_estimate_matches_page_fallback(self):
        # the page's roadKm() rounds the same way: x1.3 of the great circle, to 10 km
        self.assertEqual(rally.estimate_km(A, B), 1310)
        self.assertEqual(rally.estimate_km(A, A), 0)


class RoadTableTest(unittest.TestCase):
    """The one OSRM request: URL, User-Agent and answer checks."""

    def answer(self, body):
        resp = mock.MagicMock()
        resp.__enter__.return_value = io.BytesIO(json.dumps(body).encode())
        return mock.patch.object(rally.urllib.request, "urlopen", return_value=resp)

    def test_request(self):
        with self.answer({"code": "Ok", "distances": [[1500, None]]}) as op:
            row = ROAD_TABLE("http://osrm.test/", A, [B, C])
        self.assertEqual(row, [1500, None])
        req = op.call_args[0][0]
        self.assertEqual(
            req.full_url,
            "http://osrm.test/table/v1/driving/"
            "11.586,48.204;-0.693,44.821;-2.878791,43.2876667"
            "?sources=0&destinations=1;2&annotations=distance",
        )
        self.assertIn("roadsurfer-rally-map", req.get_header("User-agent"))
        self.assertIn(
            "github.com/gjed/roadsurfer-rally-map", req.get_header("User-agent")
        )

    def test_error_code_or_short_row_raises(self):
        for body in (
            {"code": "NoTable", "distances": [[1, 2]]},
            {"code": "Ok", "distances": [[1]]},
        ):
            with self.answer(body), self.assertRaises(ValueError):
                ROAD_TABLE("http://osrm.test", A, [B, C])


class RoadScanTest(unittest.TestCase):
    """main(): routing happens after the scan check, never when rendering a file."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def main(self, *argv):
        args = mock.patch.object(sys, "argv", ["x", *argv])
        with args, contextlib.redirect_stdout(io.StringIO()):
            rally.main()

    def test_from_json_sends_no_request(self):
        urlopen = mock.patch.object(rally.urllib.request, "urlopen")
        table = mock.patch.object(rally, "road_table")
        with urlopen as net, table as roads:
            self.main("--from-json", str(FIXTURE), "--map", str(self.dir / "i.html"))
        net.assert_not_called()
        roads.assert_not_called()
        self.assertFalse((self.dir / "road-distances.json").exists())

    def test_fixture_records_have_no_km(self):
        offers = json.loads(FIXTURE.read_text(encoding="utf-8"))["offers"]
        self.assertTrue(offers)
        self.assertFalse(any("km" in r for r in offers))

    def test_render_with_and_without_km(self):
        offers = json.loads(FIXTURE.read_text(encoding="utf-8"))["offers"]
        offers[0].update(km=1234, km_estimated=False)
        offers[1].update(km=1240, km_estimated=True)
        src = self.dir / "mixed.json"
        # an unknown top-level key is tolerated
        src.write_text(json.dumps({"offers": offers, "extra": 1}), encoding="utf-8")
        self.main("--from-json", str(src), "--map", str(self.dir / "i.html"))
        html = (self.dir / "i.html").read_text(encoding="utf-8")
        data = json.loads(page_data(html))
        self.assertEqual(data, offers)
        self.assertEqual(
            [(r.get("km"), r.get("km_estimated")) for r in data[:3]],
            [(1234, False), (1240, True), (None, None)],
        )

    def test_page_has_chain_options(self):
        self.main("--from-json", str(FIXTURE), "--map", str(self.dir / "i.html"))
        html = (self.dir / "i.html").read_text(encoding="utf-8")
        self.assertIn('<fieldset id="gchain" hidden>', html)
        for control in ("cn", "cs", "cg", "ck", "cdmin", "cdmax", "cdrive", "cr"):
            self.assertEqual(html.count(f'id="{control}"'), 1, control)
        # the option groups count as a filter and Reset restores them
        self.assertIn("gchain: CHAIN_IDS", html)
        self.assertIn("setChainOptions({", html)

    def test_page_has_chain_selection(self):
        self.main("--from-json", str(FIXTURE), "--map", str(self.dir / "i.html"))
        html = (self.dir / "i.html").read_text(encoding="utf-8")
        # a leg or connection filters the list to its chains, or opens the only one; Reset clears the filter
        self.assertIn('<fieldset id="gleg" class="on" hidden>', html)
        self.assertIn("function pickLeg(key)", html)
        self.assertIn("legFilter = null;", html)
        # the chain on the map marks its row's Map button
        self.assertIn("aria-current", html)
        # the tooltip and the legend say that a click filters
        self.assertIn("Click to only show", html)
        self.assertIn("Station \u2014 click to filter", html)

    def scan_get(self, path, alias, params=None):
        if path == "/rally/stations":
            return [
                {**s, "coordinate": {"latitude": 50.0, "longitude": 9.0}}
                for s in STATIONS.values()
            ]
        if path == "/rally/stations/1":
            return {"returns": [3]}
        return [{"startDate": "2026-12-01T00:00", "endDate": "2026-12-05T00:00"}]

    def scan(self, *argv, **counters):
        get = mock.patch.object(rally, "get", side_effect=self.scan_get)
        counts = mock.patch.multiple(rally, **counters)
        table = mock.patch.object(rally, "road_table", return_value=[0])
        sleep = mock.patch.object(rally.time, "sleep")
        cache = str(self.dir / "c.json")
        with get, counts, sleep, table as roads:
            self.main("--from", "1", "--road-cache", cache, *argv)
        return roads

    def test_blocked_scan_does_not_route(self):
        table = mock.patch.object(rally, "road_table")
        with table as roads, self.assertRaises(SystemExit):
            get = mock.patch.object(rally, "get", side_effect=self.scan_get)
            counts = mock.patch.multiple(rally, REQUESTS=100, FAILED=50)
            with get, counts:
                self.main("--from", "1", "--json-out", str(self.dir / "o.json"))
        roads.assert_not_called()
        self.assertFalse((self.dir / "o.json").exists())
        self.assertFalse((self.dir / "road-distances.json").exists())

    def test_blocked_scan_writes_no_feeds(self):
        table = mock.patch.object(rally, "road_table")
        with table as roads, self.assertRaises(SystemExit):
            get = mock.patch.object(rally, "get", side_effect=self.scan_get)
            counts = mock.patch.multiple(rally, REQUESTS=100, FAILED=50)
            with get, counts:
                self.main("--from", "1", "--feeds", str(self.dir / "feeds"))
        roads.assert_not_called()
        self.assertFalse((self.dir / "feeds").exists())

    def test_scan_with_feeds_routes_and_writes_them(self):
        roads = self.scan("--feeds", str(self.dir / "feeds"), REQUESTS=0, FAILED=0)
        roads.assert_called_once()
        feed = ET.parse(self.dir / "feeds" / "all.xml").getroot()
        entry = feed.find(f"{ATOM}entry")
        self.assertIn("Distance 0 km", entry.findtext(f"{ATOM}summary"))
        self.assertTrue((self.dir / "feeds" / "from-munich.xml").exists())

    def test_scan_without_output_does_not_route(self):
        self.scan(REQUESTS=0, FAILED=0).assert_not_called()

    def test_scan_with_output_routes(self):
        roads = self.scan("--json-out", str(self.dir / "o.json"), REQUESTS=0, FAILED=0)
        roads.assert_called_once()
        self.assertTrue((self.dir / "c.json").exists())


ATOM = "{http://www.w3.org/2005/Atom}"


def feed_offer(frm, to, start="2026-11-24", end="2026-12-01", **extra):
    """A record; frm and to are (name, cc) pairs."""
    a, b = (
        {"name": n, "cc": cc, "latitude": 50, "longitude": 9} for n, cc in (frm, to)
    )
    link = f"https://booking.example/?{frm[0]}-{to[0]}-{start}"
    return {
        "start": start,
        "end": end,
        "price": "",
        "link": link,
        "from": a,
        "to": b,
        **extra,
    }


class FeedsTest(unittest.TestCase):
    """--feeds: Atom files written from the records, offline."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.offers = json.loads(FIXTURE.read_text(encoding="utf-8"))["offers"]

    def write(self, records=None, scan=None, name="feeds"):
        with contextlib.redirect_stdout(io.StringIO()):
            rally.write_feeds(
                self.offers if records is None else records, self.dir / name, scan
            )
        return {
            f.name: ET.parse(f).getroot()
            for f in sorted((self.dir / name).glob("*.xml"))
        }

    def entries(self, feed):
        return feed.findall(f"{ATOM}entry")

    def ids(self, feeds):
        return {
            n: [e.findtext(f"{ATOM}id") for e in self.entries(f)]
            for n, f in feeds.items()
        }

    def test_fixture_feeds_parse_and_count(self):
        feeds = self.write()
        self.assertEqual(sorted(feeds), ["all.xml", "from-munich.xml"])
        for feed in feeds.values():
            self.assertEqual(feed.tag, f"{ATOM}feed")
            self.assertEqual(len(self.entries(feed)), len(self.offers))

    def test_entries_per_station(self):
        records = [
            feed_offer(("Munich", "DE"), ("Turin", "IT")),
            feed_offer(("Munich", "DE"), ("Bilbao", "ES")),
            feed_offer(("Berlin", "DE"), ("Turin", "IT")),
        ]
        feeds = self.write(records)
        self.assertEqual(
            sorted(feeds), ["all.xml", "from-berlin.xml", "from-munich.xml"]
        )
        self.assertEqual(
            {n: len(self.entries(f)) for n, f in feeds.items()},
            {"all.xml": 3, "from-berlin.xml": 1, "from-munich.xml": 2},
        )

    def test_required_atom_elements(self):
        feeds = self.write(scan=SCAN)
        for name, feed in feeds.items():
            url = rally.FEEDS_URL + name
            self.assertEqual(feed.findtext(f"{ATOM}id"), url)
            self.assertTrue(feed.findtext(f"{ATOM}title"))
            self.assertEqual(feed.findtext(f"{ATOM}updated"), SCAN["finished_at"])
            self.assertIsNotNone(feed.find(f"{ATOM}author/{ATOM}name"))
            links = {
                link.get("rel"): link.get("href")
                for link in feed.findall(f"{ATOM}link")
            }
            self.assertEqual(links, {"self": url, "alternate": rally.SITE_URL})
            for e in self.entries(feed):
                self.assertTrue(e.findtext(f"{ATOM}id").startswith("tag:"))
                self.assertTrue(e.findtext(f"{ATOM}title"))
                self.assertEqual(e.findtext(f"{ATOM}updated"), SCAN["finished_at"])

    def test_updated_without_scan_is_the_render_time(self):
        for scan in (None, {}, {"finished_at": "yesterday"}, {"finished_at": 5}):
            feeds = self.write(scan=scan)
            self.assertRegex(
                feeds["all.xml"].findtext(f"{ATOM}updated"),
                r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$",
            )

    def test_ids_unique_and_stable_across_renders(self):
        records = self.offers + [feed_offer(("Berlin", "DE"), ("Turin", "IT"))]
        first = self.ids(self.write(records, name="one"))
        second = self.ids(self.write(records, SCAN, name="two"))
        self.assertEqual(first, second)
        for ids in first.values():
            self.assertEqual(len(ids), len(set(ids)))

    def test_id_follows_route_and_window(self):
        a = feed_offer(("Munich", "DE"), ("Turin", "IT"))
        b = feed_offer(("Munich", "DE"), ("Turin", "IT"), "2026-11-25", "2026-12-02")
        c = feed_offer(("Munich", "DE"), ("Bilbao", "ES"))
        ids = self.ids(self.write([a, b, c]))["all.xml"]
        self.assertEqual(len(set(ids)), 3)
        self.assertEqual(
            ids[0],
            "tag:gjed.github.io,2026-11-26:rally:Munich%2CDE:Turin%2CIT:2026-11-24:2026-12-01",
        )

    def test_links_are_the_booking_links(self):
        entries = self.entries(self.write()["all.xml"])
        links = [e.find(f"{ATOM}link") for e in entries]
        self.assertEqual(
            [x.get("href") for x in links], [o["link"] for o in self.offers]
        )
        self.assertEqual({x.get("rel") for x in links}, {"alternate"})

    def test_title_and_summary(self):
        entry = self.entries(self.write()["all.xml"])[0]
        self.assertEqual(
            entry.findtext(f"{ATOM}title"),
            "Munich, DE → Bordeaux, FR · Tue 24 Nov – Tue 1 Dec",
        )

    def summary(self, **extra):
        record = {**feed_offer(("A", "DE"), ("B", "FR")), **extra}
        return self.entries(self.write([record])["all.xml"])[0].findtext(
            f"{ATOM}summary"
        )

    def test_summary_distance_and_price(self):
        self.assertEqual(
            self.summary(km=1230, km_estimated=True, price="Camper €129.01"),
            "2026-11-24 to 2026-12-01 · Distance ~1,230 km · Price Camper €129.01",
        )
        self.assertIn("Distance 980 km", self.summary(km=980, km_estimated=False))
        for none in ("", "n/a"):
            self.assertNotIn(
                "Price", self.summary(km=1, km_estimated=False, price=none)
            )

    def test_record_without_km_gets_the_page_estimate(self):
        record = feed_offer(("A", "DE"), ("B", "FR"))
        want = rally.estimate_km(record["from"], record["to"])
        self.assertIn(f"Distance ~{want:,} km", self.summary())

    def test_escaping(self):
        name = 'Ben & Jerry\'s "Hub" <North>'
        records = [
            feed_offer((name, "DE"), ("Turin", "IT")),
            feed_offer(("Turin", "IT"), (name, "DE")),
        ]
        feeds = self.write(records)
        for feed in feeds.values():
            titles = [e.findtext(f"{ATOM}title") for e in self.entries(feed)]
            self.assertTrue(any(name in t for t in titles))
        station = feeds["from-ben-jerry-s-hub-north.xml"]
        self.assertEqual(
            station.findtext(f"{ATOM}title"), f"roadsurfer Rally offers from {name}, DE"
        )
        raw = (self.dir / "feeds" / "all.xml").read_text(encoding="utf-8")
        self.assertNotIn("<North>", raw)

    def test_slugify(self):
        for name, slug in (
            ("Munich", "munich"),
            ("Zürich Flughafen", "zurich-flughafen"),
            ("Málaga", "malaga"),
            ("Frankfurt (Main) Airport", "frankfurt-main-airport"),
            ("Straße Øst Łódź", "strasse-ost-lodz"),
            ("  St. Pölten  ", "st-polten"),
            ("Café du Nord / Gare", "cafe-du-nord-gare"),
            ("ÆØ", "aeo"),
            ("東京", "station"),
            ("!!!", "station"),
        ):
            self.assertEqual(rally.slugify(name), slug, name)

    def test_slugs_of_duplicate_names(self):
        slugs = rally.station_slugs(
            {
                ("Neustadt", "DE"),
                ("Neustadt", "AT"),
                ("Foo", "DE"),
                ("Foo!", "DE"),
                ("Rome", "IT"),
            }
        )
        self.assertEqual(
            slugs,
            {
                ("Neustadt", "DE"): "neustadt-de",
                ("Neustadt", "AT"): "neustadt-at",
                ("Foo", "DE"): "foo-de",
                ("Foo!", "DE"): "foo-de-2",
                ("Rome", "IT"): "rome",
            },
        )

    def test_slugs_do_not_depend_on_order(self):
        stations = [("Café", "FR"), ("Cafe", "FR"), ("Cafe", "ES"), ("Cafe!", "ES")]
        want = rally.station_slugs(stations)
        self.assertEqual(rally.station_slugs(stations[::-1]), want)
        self.assertEqual(len(set(want.values())), len(stations))

    def test_station_without_offers_gets_an_empty_feed(self):
        scan = {
            "stations": [{"name": "Munich", "cc": "DE"}, {"name": "Nice", "cc": "FR"}]
        }
        feeds = self.write(scan=scan)
        self.assertEqual(sorted(feeds), ["all.xml", "from-munich.xml", "from-nice.xml"])
        self.assertEqual(len(self.entries(feeds["from-nice.xml"])), 0)
        self.assertEqual(len(self.entries(feeds["from-munich.xml"])), len(self.offers))
        self.assertEqual(
            feeds["from-nice.xml"].findtext(f"{ATOM}title"),
            "roadsurfer Rally offers from Nice, FR",
        )

    def test_slug_does_not_change_when_another_station_gets_offers(self):
        scan = {
            "stations": [{"name": "Nice", "cc": "FR"}, {"name": "Nice", "cc": "IT"}]
        }
        before = self.write([feed_offer(("Nice", "FR"), ("Turin", "IT"))], scan, "one")
        after = self.write(
            [
                feed_offer(("Nice", "FR"), ("Turin", "IT")),
                feed_offer(("Nice", "IT"), ("Turin", "IT")),
            ],
            scan,
            "two",
        )
        self.assertEqual(
            sorted(before), ["all.xml", "from-nice-fr.xml", "from-nice-it.xml"]
        )
        self.assertEqual(sorted(before), sorted(after))

    def test_stations_of_the_offers_are_added_to_the_scan_list(self):
        scan = {"stations": [{"name": "Nice", "cc": "FR"}]}
        feeds = self.write([feed_offer(("Berlin", "DE"), ("Turin", "IT"))], scan)
        self.assertEqual(sorted(feeds), ["all.xml", "from-berlin.xml", "from-nice.xml"])

    def test_junk_station_list_is_ignored(self):
        for junk in (
            None,
            "Nice",
            5,
            [None, 3, {"name": "x"}, {"name": 1, "cc": "DE"}],
        ):
            feeds = self.write(scan={"stations": junk})
            self.assertEqual(sorted(feeds), ["all.xml", "from-munich.xml"])

    def test_slugs_are_unique_files(self):
        records = [
            feed_offer((n, "DE"), ("Turin", "IT"))
            for n in ("Foo", "Foo!", "Zürich", "Zurich")
        ]
        feeds = self.write(records)
        self.assertEqual(len(feeds), 5)
        self.assertEqual(
            sum(len(self.entries(f)) for n, f in feeds.items() if n != "all.xml"), 4
        )

    def run_cli(self, *argv):
        cmd = [sys.executable, str(SCRIPT), "--from-json", str(FIXTURE), *argv]
        return subprocess.run(cmd, capture_output=True, text=True, check=False)

    def test_cli_feeds_without_map(self):
        out = self.dir / "feeds"
        r = self.run_cli("--feeds", str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("feeds (2 files, 6 offers)", r.stdout)
        self.assertEqual(
            sorted(p.name for p in out.iterdir()), ["all.xml", "from-munich.xml"]
        )
        self.assertFalse((self.dir / "index.html").exists())

    def test_cli_feeds_with_map(self):
        r = self.run_cli(
            "--feeds", str(self.dir / "f"), "--map", str(self.dir / "i.html")
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.dir / "i.html").exists())
        self.assertTrue((self.dir / "f" / "all.xml").exists())

    def test_cli_release_still_needs_map(self):
        r = self.run_cli("--feeds", str(self.dir / "f"), "--release", "v1.0.0")
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.dir / "f").exists())

    def test_from_json_without_map_or_feeds_is_rejected(self):
        r = self.run_cli()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--map or --feeds", r.stderr)

    def test_template_links_the_feed(self):
        tpl = (ROOT / "rally-map.template.html").read_text(encoding="utf-8")
        self.assertIn(
            '<link rel="alternate" type="application/atom+xml" '
            'title="roadsurfer Rally offers" href="feeds/all.xml">',
            tpl,
        )


if __name__ == "__main__":
    unittest.main()
