"""Tests for the optional Drupal.org/GitLab integration; no live network required."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from acr_evidence.adapters.drupalorg_cli import (
    DrupalOrgCliError,
    collect_issue,
    collect_releases,
    run_read,
    save_private_snapshot,
)


class DrupalCliTests(unittest.TestCase):
    def setUp(self):
        self.calls = []

    def mock_runner(self, argv, **kwargs):
        self.calls.append(argv)
        if "--version" in argv:
            return subprocess.CompletedProcess(argv, 0, "Drupal.org CLI 0.15.0\n", "")
        if "issue:show" in argv:
            return subprocess.CompletedProcess(
                argv, 0,
                json.dumps({"nid": "3619127", "title": "Example", "field_issue_status": 7, "comments": []}),
                "",
            )
        if "mr:list" in argv:
            return subprocess.CompletedProcess(
                argv, 0,
                json.dumps({"merge_requests": [{"iid": 1, "state": "merged", "web_url": "https://example.org/mr/1"}]}),
                "",
            )
        return subprocess.CompletedProcess(
            argv, 0, json.dumps({"project_title": "Drupal core", "releases": []}), ""
        )

    def test_migrated_work_item_project_scoped(self):
        snapshot = collect_issue("ai_context#3586157", runner=self.mock_runner)
        self.assertEqual("unknown", snapshot["release_applicability"])
        self.assertEqual(2, len(snapshot["commands"]))
        issue_call = next(call for call in self.calls if "issue:show" in call)
        mr_call = next(call for call in self.calls if "mr:list" in call)
        self.assertEqual(["drupalorg", "issue:show", "ai_context#3586157", "--with-comments", "--format=json"], issue_call)
        self.assertIn("--state=all", mr_call)
        self.assertIn("--format=json", mr_call)
        self.assertEqual("3619127", snapshot["issue"]["nid"])

    def test_legacy_nid(self):
        record = collect_issue("3619127", include_mrs=False, runner=self.mock_runner)
        self.assertEqual(1, len(record["commands"]))

    def test_project_releases(self):
        result = collect_releases("drupal", runner=self.mock_runner)
        self.assertIn("releases", result)

    def test_reject_shell_argument_and_write_commands(self):
        with self.assertRaises(ValueError):
            collect_issue("123;rm -rf /", runner=self.mock_runner)
        with self.assertRaises(ValueError):
            run_read("issue:apply", ["123"], runner=self.mock_runner)
        with self.assertRaises(ValueError):
            run_read("issue:show", ["--danger"], runner=self.mock_runner)
        with self.assertRaises(ValueError):
            run_read("issue:show", ["123"], flags=["--exec=rm"], runner=self.mock_runner)

    def test_allowed_flags_and_json_shape(self):
        record = run_read(
            "mr:list", ["3619127"], flags=["--state=all"], format="json",
            runner=self.mock_runner,
        )
        self.assertEqual(["drupalorg", "mr:list", "3619127", "--state=all", "--format=json"], self.calls[-1])
        self.assertEqual("merged", record["json"]["merge_requests"][0]["state"])

    def test_invalid_json_is_a_failure(self):
        def bad(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 0, "not json", "")
        with self.assertRaises(DrupalOrgCliError):
            run_read("issue:show", ["123"], format="json", runner=bad)

    def test_raw_snapshot_never_overwritten_or_public(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "private-evidence" / "a.json"
            save_private_snapshot(p, {"source": "fixture"})
            self.assertTrue(p.exists())
            with self.assertRaises(FileExistsError):
                save_private_snapshot(p, {})
            with self.assertRaises(ValueError):
                save_private_snapshot(Path(folder) / "site" / "raw.json", {})
            with self.assertRaises(ValueError):
                save_private_snapshot(Path(folder) / "public-evidence" / "raw.json", {})
            # The guard is intentionally component-based; "mysite" is not a
            # published directory assertion.
            save_private_snapshot(Path(folder) / "mysite" / "raw.json", {"ok": True})

    def test_failure_is_not_a_success(self):
        def fail(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 1, "", "not available")
        with self.assertRaises(DrupalOrgCliError):
            collect_issue("123", runner=fail)


if __name__ == "__main__":
    unittest.main()
