"""Offline checks of the map page's message catalog (stdlib unittest, no network)."""

import contextlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "roadsurfer-rally.py"
TEMPLATE = ROOT / "rally-map.template.html"
FIXTURE = ROOT / "tests" / "fixtures" / "offers.json"

LANGUAGES = ["en", "de", "fr", "es", "it", "nl", "pt"]
PLURAL = re.compile(r"^(.+)\.(zero|one|two|few|many|other)$")
KEY = re.compile(r"^[a-z][A-Za-z0-9]*(\.[A-Za-z0-9]+)+$")
PLACEHOLDER = re.compile(r"\{(\w+)\}")

_spec = importlib.util.spec_from_file_location("roadsurfer_rally", SCRIPT)
rally = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rally)


def render_fixture():
    offers = json.loads(FIXTURE.read_text(encoding="utf-8"))["offers"]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "index.html"
        with contextlib.redirect_stdout(io.StringIO()):
            rally.render(offers, out)
        return out.read_text(encoding="utf-8")


def catalog_of(html):
    """The STRINGS object of a page, parsed as JSON."""
    m = re.search(
        r"/\*STRINGS\*/\s*const STRINGS = (.*?);\s*/\*END STRINGS\*/", html, re.DOTALL
    )
    if not m:
        raise AssertionError("no /*STRINGS*/ ... /*END STRINGS*/ block in the page")
    return json.loads(m.group(1))


def placeholders(text):
    return set(PLACEHOLDER.findall(text))


def families(messages):
    """The plural families of a language: base key -> the categories it has."""
    found = {}
    for key in messages:
        m = PLURAL.match(key)
        if m:
            found.setdefault(m.group(1), set()).add(m.group(2))
    return found


class CatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = render_fixture()
        cls.strings = catalog_of(cls.html)
        cls.en = cls.strings.get("en", {})

    def reference(self, key):
        """English's message for a key; a plural form of another language reads English's `other`."""
        if key in self.en:
            return self.en[key]
        m = PLURAL.match(key)
        return self.en.get(m.group(1) + ".other") if m else None

    def test_languages(self):
        self.assertEqual(list(self.strings), LANGUAGES)
        for lang, messages in self.strings.items():
            self.assertIsInstance(messages, dict, lang)

    def test_english_is_well_formed(self):
        self.assertTrue(self.en, "English has no messages")
        for key, text in self.en.items():
            with self.subTest(key=key):
                self.assertRegex(key, KEY)
                self.assertIsInstance(text, str)
                self.assertTrue(text.strip(), "empty message")
                # every brace belongs to a {name} placeholder
                self.assertNotRegex(PLACEHOLDER.sub("", text), r"[{}]")
                # a message is text for the page to escape or put in an attribute: no quote and no tag
                self.assertNotRegex(text, r'["<>]')

    def test_english_plurals_are_complete(self):
        for base, forms in families(self.en).items():
            with self.subTest(key=base):
                self.assertIn("one", forms)
                self.assertIn("other", forms)
                self.assertNotIn(base, self.en, "a message and its plural forms")

    def test_keys_are_english_keys(self):
        for lang, messages in self.strings.items():
            for key in messages:
                with self.subTest(lang=lang, key=key):
                    self.assertIsNotNone(self.reference(key), "key English lacks")

    def test_placeholders_follow_english(self):
        for lang, messages in self.strings.items():
            for key, text in messages.items():
                with self.subTest(lang=lang, key=key):
                    self.assertIsInstance(text, str)
                    self.assertTrue(text.strip(), "empty message")
                    self.assertNotRegex(PLACEHOLDER.sub("", text), r"[{}]")
                    self.assertNotRegex(text, r'["<>]')
                    self.assertEqual(
                        placeholders(text), placeholders(self.reference(key))
                    )

    def test_plurals_have_one_and_other(self):
        for lang, messages in self.strings.items():
            for base, forms in families(messages).items():
                with self.subTest(lang=lang, key=base):
                    self.assertIn("one", forms)
                    self.assertIn("other", forms)

    def test_missing_keys_are_warnings(self):
        for lang, messages in self.strings.items():
            for key in sorted(set(self.en) - set(messages)):
                warnings.warn(f"{lang}: no translation of {key}, English is shown")

    def test_template_keys_exist(self):
        """A key the template names is a key English has (a typo would show the key)."""
        source = TEMPLATE.read_text(encoding="utf-8")
        source = re.sub(
            r"/\*STRINGS\*/.*?/\*END STRINGS\*/", "", source, flags=re.DOTALL
        )
        used = set(re.findall(r'data-t(?:-[a-z-]+)?="([^"]+)"', source))
        used |= set(re.findall(r"\bth?\('([^']+)'", source))
        prefixes = {key.split(".")[0] for key in self.en}
        for literal in re.findall(r"'([a-z][A-Za-z0-9]*(?:\.[A-Za-z0-9]+)+)'", source):
            if literal.split(".")[0] in prefixes:
                used.add(literal)
        used = {k for k in used if "$" not in k}
        self.assertTrue(used)
        for key in sorted(used):
            with self.subTest(key=key):
                self.assertTrue(
                    key in self.en or key + ".other" in self.en, "key English lacks"
                )


if __name__ == "__main__":
    unittest.main()
