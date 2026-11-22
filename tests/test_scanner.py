"""Offline unit tests for roadsurfer-rally.py (stdlib unittest, no network)."""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
import urllib.parse
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
        counters = mock.patch.multiple(rally, REQUESTS=40, FAILED=3, RATE_LIMITED=2)
        args, quiet = mock.patch.object(sys, "argv", argv), io.StringIO()
        with fake_get, counters, args, contextlib.redirect_stdout(quiet):
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
            },
        )
        self.assertEqual(len(data["offers"]), 1)


class FromJsonTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def run_cli(self, src):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--from-json", str(src)]
            + ["--map", str(self.dir / "index.html")],
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

    def test_malformed_scan_ignored(self):
        src = self.dir / "odd.json"
        src.write_text('{"scan": "yesterday", "offers": []}', encoding="utf-8")
        r = self.run_cli(src)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNone(self.page_scan())


if __name__ == "__main__":
    unittest.main()
