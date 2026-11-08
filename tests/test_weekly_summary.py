import json
import tempfile
import unittest
from pathlib import Path

from acr_evidence.weekly_summary import (
    build_facts,
    generate_weekly,
    summarize_with_huggingface,
    validate_ai_output,
)


def issue(issue_id, status, code, evidence="inventory", criteria=(), title=None):
    return {
        "id": f"drupal:{issue_id}",
        "title": title or f"Issue {issue_id}",
        "status": {"code": code, "label": status},
        "component": "core",
        "version": "main",
        "evidence_status": evidence,
        "wcag_candidates": list(criteria),
    }


def collection(issues, retrieved="2026-11-07T00:00:00Z"):
    return {
        "assessment": {"product": "Drupal Core", "standards": ["WCAG 2.2 AA", "Section 508"]},
        "summary": {"retrieved_at": retrieved, "statuses": [1, 8, 13, 14, 15]},
        "issues": issues,
    }


class WeeklySummaryTests(unittest.TestCase):
    def test_facts_track_changes_without_calling_them_fixed(self):
        current = collection([
            issue(1, "Active", 1, criteria=("1.1.1",)),
            issue(2, "Reviewed & tested by the community", 14, "full", ("1.3.1",)),
            issue(3, "Needs work", 13, criteria=("1.1.1",)),
        ])
        previous = collection([
            issue(1, "Active", 1, criteria=("1.1.1",)),
            issue(2, "Needs work", 13, "full", ("1.3.1",)),
            issue(4, "Active", 1, criteria=("2.4.4",)),
        ], retrieved="2026-10-31T00:00:00Z")
        facts = build_facts(current, previous, None, None, "2026-11-07")
        self.assertEqual(3, facts["counts"]["active"])
        self.assertEqual(1, facts["counts"]["detailed"])
        self.assertEqual(2, facts["counts"]["inventory"])
        self.assertEqual(1, facts["new_active_count"])
        self.assertEqual(1, facts["no_longer_active_count"])
        self.assertEqual(1, facts["status_change_count"])
        self.assertEqual(1, facts["new_rtbc_count"])
        self.assertEqual("drupal:4", facts["no_longer_active"][0]["id"])
        self.assertEqual(2, facts["activity"]["changed_count"])
        self.assertEqual(1, facts["activity"]["unchanged_count"])
        changed_ids = {item["id"] for item in facts["activity"]["changed"]}
        self.assertEqual({"drupal:2", "drupal:3"}, changed_ids)
        self.assertNotIn("fixed", json.dumps(facts["no_longer_active"]).casefold())


    def test_activity_detects_new_comments_and_merge_requests(self):
        current_issue = issue(1, "Active", 1)
        current_issue["comments"] = [{"id": "c1", "content_hash": "new"}]
        current_issue["merge_requests"] = [{"iid": 9, "state": "opened", "head_sha": "abc", "updated_at": "2026-11-07T00:00:00Z"}]
        previous_issue = issue(1, "Active", 1)
        previous_issue["comments"] = []
        previous_issue["merge_requests"] = [{"iid": 9, "state": "opened", "head_sha": "old", "updated_at": "2026-10-31T00:00:00Z"}]
        facts = build_facts(
            collection([current_issue]), collection([previous_issue]), None, None, "2026-11-07"
        )
        changed = facts["activity"]["changed"][0]
        self.assertIn("new-comments", changed["change_reasons"])
        self.assertIn("merge-request-activity", changed["change_reasons"])
        self.assertEqual(1, changed["new_comments"])
        self.assertEqual(1, changed["new_merge_requests"])

    def test_generate_weekly_writes_archive_and_index_without_ai(self):
        current = collection([issue(1, "Active", 1, criteria=("1.1.1",))])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            reports = root / "reports"
            (reports / "drupal-core-main").mkdir(parents=True)
            (reports / "drupal-core-main" / "summary.json").write_text(json.dumps({
                "target": {"assessment_id": "drupal-core-main", "release": "main"},
                "summary": {"findings": 1, "by_applicability": {"likely-affected": 1}, "by_evidence_status": {"inventory": 1}},
            }))
            (reports / "drupal-core-main" / "openacr.yaml").write_text("title: test\n")
            (reports / "drupal-core-main" / "acr.md").write_text("# test\n")
            current_path = root / "current.json"
            current_path.write_text(json.dumps(current))
            result = generate_weekly(
                current_path, None, reports=reports, output=root / "weekly", date="2026-11-07",
            )
            md = Path(result["markdown"]).read_text()
            facts = json.loads(Path(result["facts"]).read_text())
            provenance = json.loads(Path(result["provenance"]).read_text())
            self.assertTrue((root / "weekly" / "index.md").exists())
            self.assertIn("Weekly ACR evidence digest", md)
            self.assertIn("Baseline snapshot", md)
            self.assertEqual("disabled", result["status"])
            self.assertEqual("disabled", provenance["status"])
            self.assertNotIn("comments", facts)
            self.assertNotIn("description", facts)

    def test_ai_validation_rejects_conformance_and_unknown_facts(self):
        facts = {
            "counts": {"active": 3},
            "new_active": [{"id": "drupal:1"}],
            "no_longer_active": [], "rtbc": [], "status_changes": [],
        }
        valid, _ = validate_ai_output("Three active issues. See drupal:1. A human must review this digest.", facts)
        self.assertTrue(valid)
        for text in (
            "This supports WCAG.",
            "The issue was fixed.",
            "There are 999 active issues.",
            "See drupal:999.",
        ):
            ok, _ = validate_ai_output(text, facts)
            self.assertFalse(ok, text)

    def test_huggingface_client_is_called_with_facts_only(self):
        facts = {"counts": {"active": 1}, "new_active": [], "no_longer_active": [], "rtbc": [], "status_changes": []}
        seen = {}

        class Message:
            content = "One active issue. A human must review this digest."

        class Choice:
            message = Message()

        class Response:
            choices = [Choice()]

        class Client:
            def chat_completion(self, **kwargs):
                seen.update(kwargs)
                return Response()

        def factory(**kwargs):
            seen["client"] = kwargs
            return Client()

        text = summarize_with_huggingface(
            facts, model="org/model", provider="auto", token="test", client_factory=factory
        )
        self.assertEqual("One active issue. A human must review this digest.", text)
        self.assertEqual("org/model", seen["client"]["model"])
        self.assertIn("messages", seen)
        self.assertNotIn("Issue 1", seen["messages"][1]["content"])


    def test_no_activity_skips_huggingface(self):
        current = collection([issue(1, "Active", 1)])
        previous = collection([issue(1, "Active", 1)])
        called = []

        def factory(**kwargs):
            called.append(True)
            raise AssertionError("model should not be called")

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            current_path = root / "current.json"
            previous_path = root / "previous.json"
            current_path.write_text(json.dumps(current))
            previous_path.write_text(json.dumps(previous))
            result = generate_weekly(
                current_path, previous_path, reports=root / "reports", output=root / "weekly",
                provider="huggingface", model="org/model", token="test",
                date="2026-11-07", client_factory=factory,
            )
        self.assertEqual("skipped", result["status"])
        self.assertEqual([], called)

    def test_huggingface_output_falls_back_when_invalid(self):
        current = collection([issue(1, "Active", 1)])
        previous = collection([issue(2, "Active", 1)])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            current_path = root / "current.json"
            previous_path = root / "previous.json"
            current_path.write_text(json.dumps(current))
            previous_path.write_text(json.dumps(previous))
            result = generate_weekly(
                current_path, previous_path, reports=root / "reports", output=root / "weekly",
                provider="huggingface", model="org/model", token="test",
                date="2026-11-07", client_factory=lambda **kwargs: type("C", (), {
                    "chat_completion": lambda self, **kw: type("R", (), {
                        "choices": [type("Ch", (), {"message": type("M", (), {"content": "This supports WCAG."})()})()]
                    })()
                })(),
            )
            md = Path(result["markdown"]).read_text()
            self.assertEqual("rejected", result["status"])
            self.assertIn("Fallback reason", md)
            self.assertNotIn("This supports WCAG.", md)


if __name__ == "__main__":
    unittest.main()
