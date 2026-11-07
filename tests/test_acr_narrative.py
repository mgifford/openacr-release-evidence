import json
import tempfile
import unittest
from pathlib import Path

from acr_evidence.acr_narrative import render_acr_narrative

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "config" / "drupal-core-11.4.12.json").read_text(encoding="utf-8"))


def analysis():
    return {
        "assessment": MANIFEST,
        "target": {
            "assessment_id": "drupal-core-11.4.12",
            "product": "Drupal Core",
            "release": "11.4.12",
            "ref": "11.4.12",
            "ref_type": "tag",
            "support_status": "supported",
        },
        "generated_at": "2026-11-07T00:00:00Z",
        "summary": {"findings": 3},
        "findings": [
            {
                "issue_id": "drupal:1",
                "title": "Inventory issue with a non-text alternative problem",
                "tracker_status_label": "Needs work",
                "component": "image system",
                "evidence_status": "inventory",
                "wcag_candidates": ["1.1.1"],
                "applicability": "unknown",
                "source_url": "https://www.drupal.org/project/drupal/issues/1",
            },
            {
                "issue_id": "drupal:2",
                "title": "Detailed issue about headings",
                "tracker_status_label": "Active",
                "component": "theme system",
                "evidence_status": "full",
                "wcag_candidates": ["1.3.1"],
                "applicability": "likely-affected",
                "source_url": "https://www.drupal.org/project/drupal/issues/2",
            },
            {
                "issue_id": "drupal:3",
                "title": "Unmapped issue",
                "tracker_status_label": "Active",
                "component": "core",
                "evidence_status": "inventory",
                "wcag_candidates": [],
                "applicability": "unknown",
                "source_url": "https://www.drupal.org/project/drupal/issues/3",
            },
        ],
        "issues": [],
    }


class AcrNarrativeTests(unittest.TestCase):
    def test_renders_markdown_and_html_without_conformance_values(self):
        with tempfile.TemporaryDirectory() as folder:
            result = render_acr_narrative(analysis(), folder)
            md = Path(result["markdown"]).read_text(encoding="utf-8")
            html = Path(result["html"]).read_text(encoding="utf-8")
        self.assertIn("# Drupal Core 11.4.12", md)
        self.assertIn("## WCAG 2.2 Level A criteria", md)
        self.assertIn("Not Evaluated", md)
        self.assertIn("No active issue in this snapshot", md)
        self.assertIn("metadata-only", md)
        self.assertIn("ATAG 2.0", md)
        self.assertIn('href="./report.css"', html)
        self.assertIn('<main id="main" tabindex="-1">', html)
        self.assertEqual(1, html.count("<h1>"))
        self.assertNotIn("<script", html)
        self.assertIn("ACR result terms", html)
        self.assertIn("reviewer", html)
        self.assertIn("Drupal.org Accessibility issue queue", html)

    def test_inventory_and_detailed_evidence_are_distinguished(self):
        with tempfile.TemporaryDirectory() as folder:
            result = render_acr_narrative(analysis(), folder)
            md = Path(result["markdown"]).read_text(encoding="utf-8")
        self.assertIn("1 active (0 detailed, 1 inventory)", md)
        self.assertIn("1 active (1 detailed, 0 inventory)", md)
        self.assertIn("1 detailed, 0 metadata-only inventory", md)
        self.assertIn("1 active issue tagged to this criterion", md)

    def test_no_fabricated_reviewer(self):
        with tempfile.TemporaryDirectory() as folder:
            result = render_acr_narrative(analysis(), folder)
            md = Path(result["markdown"]).read_text(encoding="utf-8")
        self.assertIn("Unassigned reviewer (draft)", md)
        self.assertNotIn("@", md.split("## Sources")[0])


if __name__ == "__main__":
    unittest.main()
