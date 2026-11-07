import tempfile
import unittest
from pathlib import Path

from acr_evidence.model import APPLICABILITY
from acr_evidence.wcag import APPLICABILITY_LABELS, criterion_info

ROOT = Path(__file__).resolve().parents[1]


class WcagCatalogueTests(unittest.TestCase):
    def test_criterion_metadata(self):
        info = criterion_info("1.4.11")
        self.assertEqual("Non-text Contrast", info["title"])
        self.assertEqual("AA", info["level"])
        self.assertTrue(info["url"].startswith("https://www.w3.org/TR/WCAG22/#"))
        unknown = criterion_info("99.99")
        self.assertEqual("unknown", unknown["level"])
        self.assertIn("99.99", unknown["title"])

    def test_every_applicability_state_has_a_label(self):
        self.assertLessEqual(set(APPLICABILITY), set(APPLICABILITY_LABELS))
