import json
import unittest
from pathlib import Path

from acr_evidence.normalize import (
    html_to_text,
    iso_utc,
    normalize_comment,
    normalize_drupal_issue,
    wcag_from_labels,
)
from acr_evidence.model import status_label, status_workflow

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "drupal"


def fixture(nid):
    return json.loads((FIXTURES / f"issue-{nid}.json").read_text(encoding="utf-8"))


def normalized(nid):
    data = fixture(nid)
    return normalize_drupal_issue(
        data["issue"],
        data["node"],
        data["merge_requests"],
        data["term_names"],
        data["_fixture"]["retrieved_at"],
        f"private-evidence/raw/{nid}.json",
        cli_version=data["_fixture"]["cli_version"],
    )


class NormalizeTests(unittest.TestCase):
    def test_verified_drupal_status_mapping(self):
        self.assertEqual("Closed (fixed)", status_label(7))
        self.assertEqual("Needs review", status_label(8))
        self.assertEqual("Fixed", status_label(2))
        self.assertEqual("Closed (outdated)", status_label(17))
        self.assertEqual("closed-fixed", status_workflow(7))
        self.assertEqual("needs-review", status_workflow(8))
        self.assertEqual("unknown", status_workflow(99))
        self.assertEqual("Unknown status (99)", status_label(99))

    def test_wcag_tags_are_parsed_not_text_mined(self):
        self.assertEqual(["1.4.3"], wcag_from_labels(["Accessibility", "wcag143"]))
        self.assertEqual(["1.4.11"], wcag_from_labels(["wcag1411"]))
        self.assertEqual(["2.5.3"], wcag_from_labels(["wcag253"]))
        self.assertEqual(["4.1.3"], wcag_from_labels(["wcag413"]))
        self.assertEqual([], wcag_from_labels(["wcag999", "Accessibility"]))
        self.assertEqual([], wcag_from_labels(None))

    def test_html_to_text_strips_markup_and_script(self):
        text = html_to_text("<p>Hello <strong>world</strong></p><script>alert(1)</script>")
        self.assertIn("Hello world", text)
        self.assertNotIn("alert(1)", text)
        self.assertNotIn("<", text)

    def test_normalized_migrated_candidate(self):
        issue = normalized("3621109")
        self.assertEqual("drupal:3621109", issue["id"])
        self.assertEqual("drupal:drupal:3621109", issue["project_scoped_id"])
        self.assertEqual("Closed (fixed)", issue["status"]["label"])
        self.assertEqual("closed-fixed", issue["status"]["workflow_state"])
        self.assertEqual(["1.4.3"], issue["wcag_candidates"])
        self.assertEqual("Admin theme", issue["component"])
        self.assertEqual("11.4.x-dev", issue["version"])
        self.assertEqual(3, len(issue["comments"]))
        self.assertEqual(1, len(issue["merge_requests"]))
        self.assertEqual(64, len(issue["provenance"]["content_hash"]))
        self.assertTrue(issue["provenance"]["retrieved_at"].endswith("Z"))

    def test_wcag_1411_fixture(self):
        issue = normalized("3618140")
        self.assertEqual(["1.4.11"], issue["wcag_candidates"])
        self.assertEqual(2, len(issue["merge_requests"]))
        self.assertEqual("closed-fixed", issue["status"]["workflow_state"])

    def test_open_after_release_fixture(self):
        issue = normalized("3636028")
        self.assertEqual("Needs review", issue["status"]["label"])
        self.assertEqual("needs-review", issue["status"]["workflow_state"])
        self.assertEqual(["1.4.11"], issue["wcag_candidates"])

    def test_comments_preserve_provenance_and_machine_flag(self):
        raw = {
            "cid": "16746778",
            "body_value": "<p>A real comment</p>",
            "created": "1787691960",
            "author_id": "456718",
            "author_name": "kentr",
        }
        comment = normalize_comment(raw, "3619127")
        self.assertEqual("16746778", comment["id"])
        self.assertEqual("https://www.drupal.org/node/3619127#comment-16746778", comment["url"])
        self.assertEqual("kentr", comment["author"])
        self.assertTrue(comment["created_at"].endswith("Z"))
        self.assertFalse(comment["machine_generated"])
        self.assertEqual("A real comment", comment["body_text"])

        machine = normalize_comment(
            {"cid": "1", "body_value": "rkoller created an issue. See original summary.", "created": "1"},
            "1",
        )
        self.assertTrue(machine["machine_generated"])

    def test_epoch_conversion_is_utc(self):
        self.assertEqual("2026-10-01T12:25:04Z", iso_utc(1790857504))
        self.assertEqual("2026-10-01T12:25:04Z", iso_utc("2026-10-01T12:25:04+00:00"))

    def test_missing_nid_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_drupal_issue({}, {}, {}, {}, "2026-11-07T00:00:00Z", "raw.json")

    def test_content_hash_is_stable(self):
        first = normalized("3621109")["provenance"]["content_hash"]
        second = normalized("3621109")["provenance"]["content_hash"]
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
