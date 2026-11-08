import tempfile
import unittest
from pathlib import Path

from acr_evidence.report import render_landing


def analysis(target_id, release, line, support, findings):
    return {
        "assessment": {"product": "Drupal Core"},
        "target": {
            "assessment_id": target_id,
            "product": "Drupal Core",
            "release": release,
            "ref": release,
            "ref_type": "tag",
            "release_line": line,
            "support_status": support,
            "parent_project": None,
        },
        "generated_at": "2026-11-07T00:00:00Z",
        "collection": {"summary": {"detailed": 1, "inventory": 1, "with_merge_requests": 1}},
        "summary": {
            "findings": len(findings),
            "by_applicability": {"likely-affected": 1, "unknown": 1},
            "needs_verification": len(findings),
        },
        "findings": findings,
    }


def finding(issue_id, title, evidence="full"):
    return {
        "issue_id": issue_id,
        "title": title,
        "component": "core",
        "wcag_candidates": ["1.1.1"],
        "tracker_status_label": "Active",
        "applicability": "likely-affected" if evidence == "full" else "unknown",
        "evidence_status": evidence,
        "merge_requests": [] if evidence == "full" else [],
        "source_url": f"https://www.drupal.org/node/{issue_id.split(':')[1]}",
    }


class LandingUsabilityTests(unittest.TestCase):
    def test_finder_cards_and_matrix_page_preserve_data(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            analyses = [
                analysis("drupal-core-11.4.12", "11.4.12", "11.4.x", "supported", [
                    finding("drupal:1", "First active issue", "full"),
                    finding("drupal:2", "Second active issue", "inventory"),
                ]),
                analysis("drupal-core-12.0.x-dev", "main", "main", "development", [
                    finding("drupal:1", "First active issue", "full"),
                ]),
            ]
            result = render_landing(analyses, output)
            self.assertEqual(output / "index.html", result)
            html = result.read_text(encoding="utf-8")
            self.assertIn('id="finder-heading"', html)
            self.assertIn('id="filter-status-supported"', html)
            self.assertIn('id="filter-line-11-4-x"', html)
            self.assertIn('class="release-card"', html)
            self.assertIn('data-support="supported"', html)
            self.assertIn('href="./matrix.html"', html)
            self.assertIn('href="./drupal-core-11.4.12/evidence.json"', html)
            self.assertIn('href="./drupal-core-11.4.12/acr.html"', html)
            self.assertIn('href="./drupal-core-12.0.x-dev/"', html)
            self.assertNotIn("<script", html)
            matrix = (output / "matrix.html").read_text(encoding="utf-8")
            self.assertIn("First active issue", matrix)
            self.assertIn("Second active issue", matrix)
            self.assertIn("11.4.12", matrix)
            self.assertIn("main", matrix)
            self.assertNotIn("<script", matrix)


if __name__ == "__main__":
    unittest.main()
