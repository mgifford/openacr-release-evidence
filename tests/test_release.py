import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from acr_evidence.model import digest_artifact
from acr_evidence.normalize import normalize_drupal_issue
from acr_evidence.release import (
    _index_from_commits,
    analyze_collection,
    branch_for_release,
    classify_issue,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "drupal"
MANIFEST = json.loads((ROOT / "config" / "drupal-core-11.4.12.json").read_text(encoding="utf-8"))
TARGET = {
    "assessment_id": MANIFEST["id"],
    "product": "Drupal Core",
    "release": "11.4.12",
    "ref": "11.4.12",
    "tag": "11.4.12",
    "tag_commit": "aa556ff13046baca57d5f69fac25c96fc30b4f43",
    "tag_commit_short": "aa556ff1",
    "tag_date": "2026-11-06T16:05:10.000-06:00",
}


def fixture(nid):
    return json.loads((FIXTURES / f"issue-{nid}.json").read_text(encoding="utf-8"))


def normalized(nid):
    data = fixture(nid)
    return normalize_drupal_issue(
        data["issue"], data["node"], data["merge_requests"], data["term_names"],
        data["_fixture"]["retrieved_at"], f"private-evidence/raw/{nid}.json",
    )


def annotated_commits():
    refs = json.loads((FIXTURES / "commit-refs.json").read_text(encoding="utf-8"))
    commits = json.loads((FIXTURES / "commits.json").read_text(encoding="utf-8"))["commits"]
    out = []
    for commit in commits:
        record = dict(commit)
        ref = refs.get(record["sha"], {})
        record["tags"] = ref.get("tags") or []
        record["branches"] = ref.get("branches") or record.get("branches") or []
        record["in_release"] = "11.4.12" in record["tags"]
        out.append(record)
    return out


def commits_for(nid):
    return [commit for commit in annotated_commits() if f"#{nid}" in (commit.get("title") or "")]


class ReleaseClassificationTests(unittest.TestCase):
    def test_branch_from_release(self):
        self.assertEqual("11.4.x", branch_for_release("11.4.12"))
        self.assertEqual("10.6.x", branch_for_release("10.6.21"))
        with self.assertRaises(ValueError):
            branch_for_release("main")

    def test_fix_included_becomes_confirmed_fixed_with_caveat(self):
        finding = classify_issue(normalized("3621109"), MANIFEST, TARGET, commits_for("3621109"))
        self.assertEqual("confirmed-fixed", finding["applicability"])
        self.assertEqual("git-inclusion", finding["basis"])
        self.assertTrue(finding["fix_included_in_release"])
        self.assertIn("not behavioural verification", finding["reason"])
        self.assertEqual("unreviewed", finding["review_status"])
        self.assertTrue(all(url.startswith("https://") for url in finding["evidence_urls"]))

    def test_fix_only_on_newer_branch_is_likely_affected(self):
        finding = classify_issue(normalized("3618140"), MANIFEST, TARGET, commits_for("3618140"))
        self.assertEqual("likely-affected", finding["applicability"])
        self.assertEqual("git-non-inclusion", finding["basis"])
        self.assertFalse(finding["fix_included_in_release"])
        self.assertTrue(all(not commit["in_release"] for commit in finding["commits"]))
        self.assertIn("not contained", finding["reason"])

    def test_open_report_before_release_is_likely_affected(self):
        finding = classify_issue(normalized("3619154"), MANIFEST, TARGET, [])
        self.assertEqual("likely-affected", finding["applicability"])
        self.assertEqual("tracker-report", finding["basis"])

    def test_open_report_after_release_is_unknown(self):
        finding = classify_issue(normalized("3636028"), MANIFEST, TARGET, [])
        self.assertEqual("unknown", finding["applicability"])
        self.assertEqual("report-after-release", finding["basis"])

    def test_closed_fixed_without_commit_is_unknown(self):
        finding = classify_issue(normalized("3621109"), MANIFEST, TARGET, [])
        self.assertEqual("unknown", finding["applicability"])
        self.assertEqual("tracker-closed-without-commit", finding["basis"])

    def test_closed_non_fix_without_commit_is_unknown(self):
        issue = normalized("3618140")
        issue["status"] = {"code": 5, "label": "Closed (won't fix)", "workflow_state": "closed-other"}
        finding = classify_issue(issue, MANIFEST, TARGET, [])
        self.assertEqual("unknown", finding["applicability"])
        self.assertEqual("closed-non-fix", finding["basis"])

    def test_feature_absent_is_not_introduced(self):
        finding = classify_issue(normalized("3618140"), MANIFEST, TARGET, [], feature_present=False)
        self.assertEqual("not-introduced", finding["applicability"])
        self.assertEqual("code-presence", finding["basis"])

    def test_feature_unknown_is_unknown(self):
        finding = classify_issue(normalized("3618140"), MANIFEST, TARGET, [], feature_present=None)
        self.assertEqual("unknown", finding["applicability"])
        self.assertEqual("insufficient-evidence", finding["basis"])

    def test_component_outside_manifest_is_not_in_scope(self):
        manifest = json.loads(json.dumps(MANIFEST))
        manifest["components"] = ["core"]
        finding = classify_issue(normalized("3618140"), manifest, TARGET, [])
        self.assertEqual("not-in-scope", finding["applicability"])
        self.assertEqual("manifest-scope", finding["basis"])

    def test_commit_deduplication_merges_branches(self):
        sha = "a" * 40
        index = _index_from_commits([
            {"sha": sha, "short_id": "aaaaaaa", "branch": "11.x", "title": "fix: #123 ...", "created_at": "2026-01-01T00:00:00Z"},
            {"sha": sha, "short_id": "aaaaaaa", "branch": "main", "title": "fix: #123 ...", "created_at": "2026-01-01T00:00:00Z"},
        ], "2026-11-07T00:00:00Z")
        self.assertEqual(1, len(index["commits"]))
        self.assertEqual(["11.x", "main"], index["commits"][0]["branches"])
        self.assertEqual(1, len(index["by_issue"]["123"]))


class AnalyzeCollectionTests(unittest.TestCase):
    def collection(self):
        issues = [normalized("3621109"), normalized("3618140"), normalized("3636028"), normalized("3619154")]
        return {
            "assessment": MANIFEST,
            "issues": issues,
            "summary": {"collected": len(issues)},
            "collection": {"query": {}, "cli_version": "Drupal.org CLI 0.15.0", "summary": {}},
            "evidence_digest": "collection-digest",
        }

    def test_analysis_is_reproducible_and_offline(self):
        commits = annotated_commits()
        index = _index_from_commits(commits, "2026-11-07T00:00:00Z")
        refs = json.loads((FIXTURES / "commit-refs.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "analysis.json"
            with patch("acr_evidence.release.get_tag", return_value={
                "name": "11.4.12", "tag_commit": TARGET["tag_commit"],
                "tag_commit_short": "aa556ff1", "tag_date": TARGET["tag_date"],
            }), patch("acr_evidence.release.build_commit_index", return_value=index), patch(
                "acr_evidence.release.tags_containing", side_effect=lambda sha: refs[sha]["tags"]
            ), patch(
                "acr_evidence.release.branches_containing", side_effect=lambda sha: refs[sha]["branches"]
            ):
                artifact = analyze_collection(
                    self.collection(), MANIFEST, "11.4.12", output=output,
                    cache_dir=folder, now=datetime(2026, 11, 7, tzinfo=timezone.utc),
                )
            self.assertTrue(output.exists())
            self.assertEqual(4, len(artifact["findings"]))
            self.assertEqual(1, artifact["summary"]["fix_included_in_release"])
            self.assertEqual("collection-digest", artifact["collection"]["collection_digest"])
            self.assertEqual(artifact["evidence_digest"], digest_artifact(artifact))
            reloaded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(artifact["evidence_digest"], digest_artifact(reloaded))


if __name__ == "__main__":
    unittest.main()
