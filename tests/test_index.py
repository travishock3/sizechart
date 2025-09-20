import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"


class SizeTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capture_table = False
        self.capture_header = False
        self.capture_cell = False
        self.headers = []
        self._buffer = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "table" and attrs_dict.get("id") == "sizeTable":
            self.capture_table = True
        elif self.capture_table and tag == "thead":
            self.capture_header = True
        elif self.capture_table and self.capture_header and tag == "th":
            self.capture_cell = True
            self._buffer = []

    def handle_endtag(self, tag):
        if tag == "table" and self.capture_table:
            self.capture_table = False
        elif tag == "thead" and self.capture_table:
            self.capture_header = False
        elif tag == "th" and self.capture_table and self.capture_header and self.capture_cell:
            text = "".join(self._buffer).strip()
            if text:
                self.headers.append(text)
            self.capture_cell = False
            self._buffer = []

    def handle_data(self, data):
        if self.capture_table and self.capture_header and self.capture_cell:
            self._buffer.append(data)


class IndexHtmlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html_text = HTML_PATH.read_text(encoding="utf-8")

    def test_table_has_expected_headers(self):
        parser = SizeTableParser()
        parser.feed(self.html_text)
        expected_headers = ["Size", "LP", "L.Paha", "Hip", "PC", "FR"]
        self.assertEqual(parser.headers, expected_headers)

    def test_default_seed_data_present(self):
        expected_entries = [
            {"size": "XS", "lp": 68, "lph": 54, "hip": 82, "pc": 100, "fr": 30},
            {"size": "S", "lp": 70, "lph": 56, "hip": 84, "pc": 100, "fr": 31},
            {"size": "M", "lp": 76, "lph": 59, "hip": 86, "pc": 100, "fr": 32},
            {"size": "L", "lp": 78, "lph": 60, "hip": 90, "pc": 100, "fr": 32},
            {"size": "XL", "lp": 80, "lph": 60, "hip": 92, "pc": 100, "fr": 32},
            {"size": "XXL", "lp": 82, "lph": 62, "hip": 96, "pc": 100, "fr": 33},
        ]
        for entry in expected_entries:
            pattern = r"\{[^}]*size:\s*\"" + re.escape(entry["size"]) + r"\"[^}]*\}"
            match = re.search(pattern, self.html_text)
            self.assertIsNotNone(match, f"Entry for size {entry['size']} not found")
            block = match.group(0)
            for key, value in entry.items():
                if key == "size":
                    continue
                self.assertRegex(
                    block,
                    rf"{re.escape(key)}\s*:\s*{value}",
                    msg=f"Field {key} for size {entry['size']} missing or incorrect",
                )

    def test_unit_toggle_buttons_present(self):
        for unit in ("cm", "in"):
            self.assertRegex(
                self.html_text,
                rf"<button[^>]*class=\"[^\"]*unit-toggle[^\"]*\"[^>]*data-unit=\"{unit}\"",
                msg=f"Unit toggle button for {unit.upper()} missing",
            )

    def test_measurement_guides_count(self):
        guides = re.findall(
            r"<article[^>]*class=\"[^\"]*guide-item[^\"]*\"",
            self.html_text,
            re.IGNORECASE,
        )
        self.assertEqual(len(guides), 5)

    def test_html2canvas_cdn_reference(self):
        self.assertIn("html2canvas", self.html_text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
