import json
import os
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from pathlib import Path

from acr_evidence.collect import collect_issues
from acr_evidence.adapters.drupalorg_cli import DrupalOrgCliError

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "drupal"
MANIFEST = json.loads((ROOT / "config" / "drupal-core-11.4.12.json").read_text(encoding="utf-8"))


def fixture(nid):
    return json.loads((FIXTURES / f"issue-{nid}.json").read_text(encoding="utf-8"))


class FakeRest:
    def __init__(self, data, fail=()):
        self.data = data
        self.fail = set(fail)
        self.discovery_calls = []
        self.node_calls = []

    def get_node(self, nid):
        self.node_calls.append(str(nid))
        if str(nid) in self.fail:
            raise RuntimeError("node unavailable")
        return self.data[str(nid)]["node"]

    def resolve_terms(self, node, cache):
        nid = str(node.get("nid"))
        return self.data[nid]["term_names"]

    def find_issues(self, **kwargs):
        self.discovery_calls.append(kwargs)
        return [self.data[nid]["node"] for nid in list(self.data)[: kwargs.get("limit", 20)]]


class FakeCli:
    def __init__(self, data, fail_issue=(), fail_mrs=()):
        self.data = data
        self.fail_issue = set(fail_issue)
        self.fail_mrs = set(fail_mrs)
        self.issue_calls = []
        self.mr_calls = []

    def version(self):
        return "Drupal.org CLI 0.15.0"

    def issue_show(self, nid, with_comments=True):
        self.issue_calls.append(str(nid))
        if str(nid) in self.fail_issue:
            raise DrupalOrgCliError("issue unavailable")
        return self.data[str(nid)]["issue"]

    def mr_list(self, nid, state="all"):
        self.mr_calls.append(str(nid))
        if str(nid) in self.fail_mrs:
            raise DrupalOrgCliError("MR listing unavailable")
        return self.data[str(nid)]["merge_requests"]



class PagedRest(FakeRest):
    def find_issues(self, **kwargs):
        self.discovery_calls.append(kwargs)
        nodes = [self.data[nid]["node"] for nid in self.data]
        page = kwargs.get("page", 0)
        limit = kwargs.get("limit", 50)
        return nodes[page * limit:(page + 1) * limit]


class CollectTests(unittest.TestCase):
    def data(self):
        return {nid: fixture(nid) for nid in ("3621109", "3618140")}

    def run_collect(self, folder, *, cli=None, rest=None, include_ids=("3621109", "3618140"), now=None, max_issues=20, statuses=None, detail_limit=60, previous_collection=None, output_name="collection.json"):
        data = self.data()
        cli = cli or FakeCli(data)
        rest = rest or FakeRest(data)
        output = Path(folder) / output_name
        query = {
            "project": "drupal",
            "project_id": "3060",
            "tag": "Accessibility",
            "tag_tid": "1101",
            "max_issues": max_issues,
            "include_ids": list(include_ids),
            "statuses": statuses,
            "detail_limit": detail_limit,
        }
        artifact = collect_issues(
            MANIFEST, query, output,
            raw_dir=Path(folder) / "raw",
            cache_dir=Path(folder) / "cache",
            cli=cli, rest=rest,
            now=now or datetime.now(timezone.utc),
            previous_collection=previous_collection,
        )
        return artifact, output, cli, rest

    def test_collects_and_archives_raw_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            artifact, output, cli, rest = self.run_collect(folder)
            self.assertTrue(output.exists())
            self.assertEqual(2, artifact["summary"]["collected"])
            self.assertEqual(2, artifact["summary"]["fetched"])
            self.assertEqual(0, artifact["summary"]["failed"])
            self.assertEqual(2, len(artifact["issues"]))
            self.assertEqual(["3618140", "3621109"], sorted(cli.issue_calls))
            self.assertEqual(["3618140", "3621109"], sorted(cli.mr_calls))
            raw_files = list((Path(folder) / "raw").glob("*.json"))
            self.assertEqual(2, len(raw_files))
            for issue in artifact["issues"]:
                self.assertTrue(issue["provenance"]["raw_ref"].startswith(str(Path(folder) / "raw")))
            self.assertEqual(0o644, os.stat(output).st_mode & 0o777)
            cache_file = Path(folder) / "cache" / "issues" / "3621109.json"
            self.assertEqual(0o600, os.stat(cache_file).st_mode & 0o777)

    def test_cache_avoids_refetching(self):
        with tempfile.TemporaryDirectory() as folder:
            now = datetime.now(timezone.utc)
            first, _, cli, _ = self.run_collect(folder, now=now)
            calls_after_first = len(cli.issue_calls)
            second, _, cli2, _ = self.run_collect(folder, now=now)
            self.assertEqual(2, second["summary"]["cached"])
            self.assertEqual(0, second["summary"]["fetched"])
            self.assertEqual(0, len(cli2.issue_calls))
            self.assertEqual([i["id"] for i in first["issues"]], [i["id"] for i in second["issues"]])

    def test_one_failure_does_not_invalidate_the_run(self):
        with tempfile.TemporaryDirectory() as folder:
            data = self.data()
            cli = FakeCli(data, fail_issue={"3618140"})
            artifact, output, _, _ = self.run_collect(folder, cli=cli)
            self.assertEqual(1, artifact["summary"]["collected"])
            self.assertEqual(1, artifact["summary"]["failed"])
            self.assertEqual("issue", artifact["summary"]["errors"][0]["stage"])
            self.assertTrue(output.exists())

    def test_mr_failure_is_preserved_as_a_warning(self):
        with tempfile.TemporaryDirectory() as folder:
            data = self.data()
            cli = FakeCli(data, fail_mrs={"3621109"})
            artifact, _, _, _ = self.run_collect(folder, cli=cli)
            self.assertEqual(2, artifact["summary"]["collected"])
            self.assertEqual(1, artifact["summary"]["with_merge_requests"])
            self.assertEqual(0, artifact["summary"]["failed"])

    def test_discovery_query_is_used_when_ids_are_not_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            data = self.data()
            for record in data.values():
                record["node"]["field_issue_status"] = 1
            rest = FakeRest(data)
            artifact, _, _, rest = self.run_collect(folder, include_ids=(), max_issues=2, rest=rest)
            self.assertEqual(2, artifact["summary"]["collected"])
            self.assertEqual(1, len(rest.discovery_calls))
            call = rest.discovery_calls[0]
            self.assertEqual("3060", call["project_id"])
            self.assertEqual("1101", call["tag_tid"])
            self.assertEqual(2, call["limit"])
            self.assertEqual(2, artifact["summary"]["detailed"])


    def test_closed_issues_are_excluded_from_active_discovery(self):
        with tempfile.TemporaryDirectory() as folder:
            data = self.data()
            data["3621109"]["node"]["field_issue_status"] = 1
            artifact, _, _, _ = self.run_collect(
                folder, include_ids=(), max_issues=2, statuses=[1], detail_limit=0, rest=FakeRest(data)
            )
            self.assertEqual(1, artifact["summary"]["collected"])
            self.assertEqual(1, artifact["summary"]["excluded_by_status"])
            self.assertEqual("Active", artifact["issues"][0]["status"]["label"])

    def test_detail_limit_keeps_inventory_records(self):
        with tempfile.TemporaryDirectory() as folder:
            artifact, _, cli, _ = self.run_collect(folder, detail_limit=1)
            statuses = {issue["evidence_status"] for issue in artifact["issues"]}
            self.assertEqual({"full", "inventory"}, statuses)
            self.assertEqual(1, artifact["summary"]["detailed"])
            self.assertEqual(1, artifact["summary"]["inventory"])
            self.assertEqual(1, len(cli.issue_calls))
            inventory = next(issue for issue in artifact["issues"] if issue["evidence_status"] == "inventory")
            self.assertEqual([], inventory["comments"])
            self.assertEqual("drupal.org-api", inventory["provenance"]["adapter"])


    def test_discovery_pages_beyond_the_first_result_set(self):
        with tempfile.TemporaryDirectory() as folder:
            base = self.data()["3621109"]
            data = {}
            for index in range(51):
                nid = str(900000 + index)
                record = json.loads(json.dumps(base))
                record["node"]["nid"] = nid
                record["node"]["field_issue_status"] = 1
                record["issue"]["nid"] = nid
                record["issue"]["field_issue_status"] = 1
                data[nid] = record
            rest = PagedRest(data)
            artifact, _, _, rest = self.run_collect(
                folder, include_ids=(), max_issues=5000, statuses=[1],
                detail_limit=0, rest=rest,
            )
            self.assertEqual(51, artifact["summary"]["collected"])
            self.assertEqual(2, len(rest.discovery_calls))
            self.assertEqual(51, artifact["summary"]["inventory"])


    def test_incomplete_discovery_fails_instead_of_publishing_partial_queue(self):
        class FailingRest(FakeRest):
            def find_issues(self, **kwargs):
                raise TimeoutError("Drupal.org API timed out")

        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(RuntimeError):
                with patch("acr_evidence.collect.time.sleep"):
                    self.run_collect(
                        folder, include_ids=(), max_issues=2, statuses=[1],
                        detail_limit=0, rest=FailingRest(self.data()),
                    )


    def test_incremental_cache_reuses_unchanged_issues(self):
        class NoChangesRest(FakeRest):
            def find_issues(self, **kwargs):
                self.discovery_calls.append(kwargs)
                return []

        with tempfile.TemporaryDirectory() as folder:
            data = self.data()
            for record in data.values():
                record["node"]["field_issue_status"] = 1
                record["issue"]["field_issue_status"] = 1
            first, previous_path, first_cli, _ = self.run_collect(
                folder, include_ids=("3621109", "3618140"), rest=FakeRest(data),
                cli=FakeCli(data), output_name="previous.json",
            )
            second, _, second_cli, second_rest = self.run_collect(
                folder, include_ids=(), statuses=[1], rest=NoChangesRest(data),
                cli=FakeCli(data), previous_collection=previous_path,
            )
            self.assertEqual(2, second["summary"]["reused"])
            self.assertEqual(2, second["summary"]["collected"])
            self.assertEqual(0, second["summary"]["fetched"])
            self.assertEqual(0, len(second_cli.issue_calls))
            self.assertEqual(1, len(second_rest.discovery_calls))

    def test_issue_from_another_project_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            data = self.data()
            data["3621109"]["node"] = dict(data["3621109"]["node"])
            data["3621109"]["node"]["field_project"] = {"machine_name": "not_drupal"}
            artifact, _, _, _ = self.run_collect(folder, rest=FakeRest(data))
            self.assertEqual(1, artifact["summary"]["collected"])
            self.assertEqual("discovery", artifact["summary"]["errors"][0]["stage"])


if __name__ == "__main__":
    unittest.main()
