import json
import tempfile
import unittest
from pathlib import Path

from acr_evidence.model import validate_manifest
from acr_evidence.report import render_landing

ROOT = Path(__file__).resolve().parents[1]
TARGETS = json.loads((ROOT / "config" / "drupal-core-targets.json").read_text(encoding="utf-8"))


def analysis(target_id, release, ref, ref_type, support_status, applicability="likely-affected"):
    target = {
        "assessment_id": target_id,
        "product": "Drupal Core",
        "release": release,
        "ref": ref,
        "ref_type": ref_type,
        "support_status": support_status,
        "release_line": "main" if ref_type == "branch" else release.rsplit(".", 1)[0] + ".x",
        "parent_project": None,
        "scope_note": "Synthetic scope note for a rendering test.",
    }
    finding = {
        "issue_id": "drupal:3621109",
        "title": "Skip link in dark mode has low color contrast",
        "applicability": applicability,
        "wcag_candidates": ["1.4.3"],
    }
    return {
        "target": target,
        "generated_at": "2026-11-07T00:00:00Z",
        "findings": [finding],
        "summary": {
            "findings": 1,
            "by_applicability": {applicability: 1},
            "fix_included_in_target": 1 if applicability == "confirmed-fixed" else 0,
            "unknown_count": 0,
        },
    }


class MultiTargetTests(unittest.TestCase):
    def test_policy_has_two_supported_lines_and_development_targets(self):
        self.assertEqual(2, TARGETS["policy"]["supported_release_lines"])
        statuses = [target["support_status"] for target in TARGETS["targets"]]
        self.assertEqual(2, statuses.count("supported"))
        self.assertEqual(2, statuses.count("pre-release"))
        self.assertEqual(1, statuses.count("development"))
        self.assertEqual(5, len(TARGETS["targets"]))

    def test_every_target_manifest_is_valid(self):
        for target in TARGETS["targets"]:
            manifest = json.loads((ROOT / target["manifest"]).read_text(encoding="utf-8"))
            validate_manifest(manifest)
            self.assertTrue(manifest["id"].startswith(target["id"]))

    def test_landing_contains_target_cards_and_matrix(self):
        first = analysis("drupal-core-11.4.12", "11.4.12", "11.4.12", "tag", "supported", "confirmed-fixed")
        second = analysis("drupal-core-main", "12.0.x-dev", "main", "branch", "development", "likely-affected")
        with tempfile.TemporaryDirectory() as folder:
            output = render_landing([first, second], folder, TARGETS)
            html = output.read_text(encoding="utf-8")
        self.assertIn('<a class="skip" href="#main">', html)
        self.assertIn('<main id="main" tabindex="-1">', html)
        self.assertNotIn("<script", html)
        self.assertIn('class="matrix-table"', html)
        self.assertIn("<caption>", html)
        self.assertIn('scope="col"', html)
        self.assertIn('scope="row"', html)
        self.assertIn('tabindex="0"', html)
        self.assertIn('role="region"', html)
        self.assertIn("drupal-core-11.4.12/", html)
        self.assertIn("drupal-core-main/", html)
        self.assertIn("Supported release line", html)
        self.assertIn("Development branch", html)
        self.assertIn("Cross-release applicability matrix", html)
        self.assertNotIn("supports", html.casefold())


if __name__ == "__main__":
    unittest.main()
