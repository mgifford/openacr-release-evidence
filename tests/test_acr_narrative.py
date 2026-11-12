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
            "release_line": "11.4.x",
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
    def test_renders_three_column_component_tables(self):
        with tempfile.TemporaryDirectory() as folder:
            result = render_acr_narrative(analysis(), folder)
            md = Path(result["markdown"]).read_text(encoding="utf-8")
            html = Path(result["html"]).read_text(encoding="utf-8")
        self.assertIn("# Drupal Core 11.4.12", md)
        self.assertIn("## WCAG 2.2 Level A criteria", md)
        self.assertIn("Not Evaluated", md)
        self.assertIn("Partially Supports", md)
        self.assertIn("Authoring Tool", md)
        self.assertIn("Electronic Documents", md)
        self.assertIn("1.2.4", md)
        self.assertIn("1.2.5", md)
        self.assertIn("Supports is based on the declared Drupal surface assessment", md)
        self.assertIn("Table 1: Success Criteria, Level A", md)
        self.assertIn("Table 2: Success Criteria, Level AA", md)
        self.assertIn("Table 3: Success Criteria, Level AAA", md)
        self.assertIn("Criteria | Conformance Level | Remarks and Explanations", md)
        self.assertIn("**Web:**", md)
        self.assertIn("**Electronic Documents:**", md)
        self.assertIn("**Authoring Tool:**", md)
        self.assertIn("Not Evaluated", md)
        self.assertIn("N/A", md)
        self.assertIn("Not Applicable claim review", md)
        self.assertIn("Functional Performance Criteria (mapped)", md)
        self.assertIn("People who may be affected:", md)
        self.assertIn("Introduced in WCAG 2.1", md)
        self.assertIn("Introduced in WCAG 2.2", md)
        self.assertIn("Potential barrier:", md)
        self.assertIn("W3C Understanding", md)
        self.assertNotIn("not mapped", md)
        self.assertIn("Support Documentation and Services", md)
        self.assertIn("A mapped functional-performance summary is provided above", md)
        self.assertIn("Beyond WCAG: non-WCAG accessibility considerations", md)
        self.assertIn("EN 301 549 user preferences", md)
        self.assertIn("Visually induced motion sickness", md)
        self.assertIn("These are review prompts, not findings", md)
        self.assertIn("Without Hearing", md)
        self.assertIn("authoring support for captions and transcripts", md)
        self.assertIn("No standalone electronic-document product", md)
        self.assertIn("No native audio/video", md)
        self.assertIn("N/A is never used merely because no active issue is tagged", md)
        self.assertEqual(1, md.count("Drupal Core does not ship a standalone electronic-document product or packaged non-web software"))
        self.assertIn("Evidence state:", md)
        self.assertIn("Automated coverage: partial", md)
        self.assertIn("**Web:**   Partially Supports", md)
        self.assertIn("**Authoring Tool:**   Supports", md)
        self.assertNotIn("**Web:**   Does Not Support", md)
        self.assertNotIn("**Authoring Tool:**   Does Not Support", md)
        self.assertIn("**Example:**", md)
        self.assertNotIn("All issue references:", md)
        self.assertIn("https://www.drupal.org/project/ableplayer", md)
        self.assertIn("metadata-only", md)
        self.assertIn("ATAG 2.0", md)
        self.assertIn('href="./report.css"', html)
        self.assertIn('<main id="main" tabindex="-1">', html)
        self.assertEqual(1, html.count("<h1>"))
        self.assertNotIn("<script", html)
        self.assertIn("ACR result terms", html)
        self.assertIn("reviewer", html)
        self.assertIn("Drupal.org Accessibility issue queue", html)
        self.assertIn("Why this ACR is different", md)
        self.assertIn("Conventional vendor ACR and this issue-queue attestation", md)
        self.assertIn("https://github.com/GSA/openacr/issues/180", md)
        self.assertIn("Theme availability for 11.4.x", md)

    def test_inventory_and_detailed_evidence_are_distinguished(self):
        with tempfile.TemporaryDirectory() as folder:
            result = render_acr_narrative(analysis(), folder)
            md = Path(result["markdown"]).read_text(encoding="utf-8")
        self.assertIn("1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory", md)
        self.assertIn("1 active issue tagged to this criterion: 1 detailed, 0 metadata-only inventory", md)


    def test_accepted_criterion_summary_is_used(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "target"
            (root / "acr-summaries.json").write_text(json.dumps({
                "prompt_version": "acr-criterion-v2",
                "criteria": {
                    "1.1.1": {
                        "status": "accepted",
                        "web": "AI web barrier summary.",
                        "authoring": "AI authoring barrier summary.",
                    }
                }
            }), encoding="utf-8")
            result = render_acr_narrative(analysis(), target)
            md = Path(result["markdown"]).read_text(encoding="utf-8")
        self.assertIn("AI web barrier summary.", md)
        self.assertIn("AI authoring barrier summary.", md)
        self.assertIn("model-assisted draft summaries", md)

    def test_between_release_fix_note_is_separate_from_active_counts(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = {
                "artifact_type": "drupal-release-transition-ledger",
                "target_order": [
                    "drupal-core-10.6.21",
                    "drupal-core-11.4.12",
                    "drupal-core-12.0.0-alpha1",
                ],
                "issues": [{
                    "issue_id": "drupal:99",
                    "title": "A fix landed only in Drupal 12",
                    "source_url": "https://www.drupal.org/node/99",
                    "targets": {
                        "drupal-core-10.6.21": "not-included",
                        "drupal-core-11.4.12": "not-included",
                        "drupal-core-12.0.0-alpha1": "included",
                    },
                    "commits": [{
                        "sha": "abcdef1234567890",
                        "targets": {
                            "drupal-core-10.6.21": False,
                            "drupal-core-11.4.12": False,
                            "drupal-core-12.0.0-alpha1": True,
                        },
                    }],
                }],
            }
            Path(folder, "release-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
            result = render_acr_narrative(analysis(), folder)
            md = Path(result["markdown"]).read_text(encoding="utf-8")
        self.assertIn("Between-release fix notes", md)
        self.assertIn("A fix landed only in Drupal 12", md)
        self.assertIn("drupal-core-12.0.0-alpha1", md)
        self.assertIn("not included in this target", md)

    def test_no_fabricated_reviewer(self):
        with tempfile.TemporaryDirectory() as folder:
            result = render_acr_narrative(analysis(), folder)
            md = Path(result["markdown"]).read_text(encoding="utf-8")
        self.assertIn("Unassigned reviewer (draft)", md)
        self.assertNotRegex(md.split("## Sources")[0], r"[\w.]+@[\w.-]+\.[A-Za-z]{2,}")


if __name__ == "__main__":
    unittest.main()
