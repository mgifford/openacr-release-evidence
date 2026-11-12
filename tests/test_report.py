import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from acr_evidence.normalize import normalize_drupal_issue
from acr_evidence.release import classify_issue
from acr_evidence.report import render_report

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "drupal"
MANIFEST = json.loads((ROOT / "config" / "drupal-core-11.4.12.json").read_text(encoding="utf-8"))
TARGET = {
    "assessment_id": MANIFEST["id"], "product": "Drupal Core", "release": "11.4.12",
    "ref": "11.4.12", "tag": "11.4.12", "tag_commit": "aa556ff13046baca57d5f69fac25c96fc30b4f43",
    "tag_commit_short": "aa556ff1", "tag_date": "2026-11-06T16:05:10.000-06:00",
}


def fixture(nid):
    return json.loads((FIXTURES / f"issue-{nid}.json").read_text(encoding="utf-8"))


def normalized(nid):
    data = fixture(nid)
    return normalize_drupal_issue(
        data["issue"], data["node"], data["merge_requests"], data["term_names"],
        data["_fixture"]["retrieved_at"], f"private-evidence/raw/{nid}.json",
    )


def commits_for(nid):
    refs = json.loads((FIXTURES / "commit-refs.json").read_text(encoding="utf-8"))
    commits = json.loads((FIXTURES / "commits.json").read_text(encoding="utf-8"))["commits"]
    result = []
    for commit in commits:
        if f"#{nid}" not in (commit.get("title") or ""):
            continue
        record = dict(commit)
        record["tags"] = refs.get(record["sha"], {}).get("tags") or []
        record["in_release"] = "11.4.12" in record["tags"]
        record["branches"] = refs.get(record["sha"], {}).get("branches") or record.get("branches") or []
        result.append(record)
    return result


def synthetic_issue():
    return {
        "id": "drupal:9999", "source_id": "9999", "url": "https://www.drupal.org/node/9999",
        "title": "<script>alert(1)</script> Unsafe title",
        "description_text": "Summary <img src=x onerror=alert(1)> and a <script>alert(3)</script> block.",
        "comments": [{
            "author": "<b>Attacker</b>", "created_at": "2026-01-01T00:00:00Z",
            "url": "javascript:alert(1)", "body_text": "<script>alert(2)</script>",
            "machine_generated": False,
        }],
        "status": {"label": "Active", "workflow_state": "open"},
        "component": "Admin theme", "version": "main",
        "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-02T00:00:00Z",
        "wcag_candidates": ["1.4.3"], "merge_requests": [],
        "provenance": {"retrieved_at": "2026-11-07T00:00:00Z"}, "synthetic": True,
    }


def synthetic_finding(issue):
    return {
        "assessment_id": MANIFEST["id"], "target": {"product": "Drupal Core", "release": "11.4.12", "tag": "11.4.12", "ref": "11.4.12"},
        "issue_id": "drupal:9999", "source_url": issue["url"], "title": issue["title"],
        "component": "Admin theme", "tracker_status": 1, "tracker_status_label": "Active",
        "tracker_version": "main", "created_at": "2026-01-01T00:00:00Z",
        "observed_at": "2026-11-07T00:00:00Z", "wcag_candidates": ["1.4.3"],
        "applicability": "likely-affected", "basis": "tracker-report",
        "reason": "Synthetic report used to verify escaping; not real Drupal evidence.",
        "fix_included_in_release": False, "commits": [], "merge_requests": [],
        "evidence_urls": [issue["url"]], "review_status": "unreviewed", "synthetic": True,
    }


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self.ids = set()
        self.anchors = []
        self.tables = 0
        self.captions = 0
        self.th_scopes = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href", "").startswith("#"):
            self.anchors.append(attrs["href"])
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(int(tag[1]))
        if tag == "table":
            self.tables += 1
        if tag == "caption":
            self.captions += 1
        if tag == "th":
            self.th_scopes.append(attrs.get("scope"))


class ReportTests(unittest.TestCase):
    def build_analysis(self):
        issues = [normalized("3621109"), normalized("3618140"), normalized("3636028")]
        findings = [
            classify_issue(issues[0], MANIFEST, TARGET, commits_for("3621109")),
            classify_issue(issues[1], MANIFEST, TARGET, commits_for("3618140")),
            classify_issue(issues[2], MANIFEST, TARGET, []),
        ]
        synthetic = synthetic_issue()
        issues.append(synthetic)
        findings.append(synthetic_finding(synthetic))
        return {
            "schema_version": "0.2.0",
            "artifact_type": "drupal-release-applicability-draft",
            "assessment": MANIFEST,
            "target": TARGET,
            "generated_at": "2026-11-07T00:00:00Z",
            "collection": {
                "query": {"project": "drupal"},
                "collection_digest": "collection-digest",
                "summary": {"retrieved_at": "2026-11-07T00:00:00Z"},
                "cli_version": "Drupal.org CLI 0.15.0",
            },
            "issues": issues,
            "findings": findings,
            "summary": {
                "findings": len(findings),
                "by_applicability": {"confirmed-fixed": 1, "likely-affected": 2, "unknown": 1},
                "by_workflow": {"closed-fixed": 1, "needs-review": 1, "open": 2},
                "fix_included_in_release": 1,
                "needs_verification": 4,
                "unmapped_criteria": 1,
                "criteria": ["1.4.3", "1.4.11"],
                "commit_index": {"branches": ["11.4.x"], "since": "2026-05-10T00:00:00Z", "retrieved_at": "2026-11-07T00:00:00Z"},
            },
            "sources": {"gitlab_project": "https://git.drupalcode.org/project/drupal"},
            "evidence_digest": "analysis-digest",
            "manifest_digest": "manifest-digest",
            "digest_scope": "sha256 over this artifact excluding generated_at and evidence_digest",
        }

    def render(self):
        folder = tempfile.mkdtemp()
        artifact = self.build_analysis()
        render_report(artifact, folder)
        return Path(folder), artifact

    def test_report_is_static_and_escapes_untrusted_text(self):
        folder, _ = self.render()
        html = (folder / "index.html").read_text(encoding="utf-8")
        issues_html = (folder / "issues.html").read_text(encoding="utf-8")
        self.assertNotIn("<script", html)
        self.assertNotIn("<script", issues_html)
        self.assertNotIn("<img", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", issues_html)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", issues_html)
        self.assertNotIn('href="javascript:', issues_html)
        self.assertIn("not an Accessibility Conformance Report", html)
        self.assertIn('<a class="skip" href="#main">Skip to main content</a>', html)
        self.assertIn('<main id="main" tabindex="-1">', html)
        self.assertIn('href="./report.css"', html)
        self.assertIn('href="./evidence.json"', html)
        self.assertIn('href="./summary.json"', html)
        self.assertNotIn("supports", html.casefold())

    def test_report_pages_are_split_and_navigable(self):
        folder, _ = self.render()
        pages = ["index.html", "issues.html", "criteria.html", "sources.html", "method.html"]
        for page in pages:
            self.assertTrue((folder / page).is_file(), page)
        index = (folder / "index.html").read_text(encoding="utf-8")
        for page in pages[1:]:
            self.assertIn(f'href="./{page}"', index)
        self.assertIn('aria-current="page">Overview</a>', index)
        self.assertIn("Reported issues", index)
        self.assertIn("Sources and data", index)
        self.assertIn("How this report works", index)
        for anchor in ("issues", "criteria", "components", "gaps", "scope", "method",
                       "provenance", "issue-drupal-3621109", "sc-1-4-3", "component-admin-theme"):
            self.assertIn(f'id="{anchor}"', index)

    def test_headings_tables_and_anchors(self):
        folder, _ = self.render()
        pages = ["index.html", "issues.html", "criteria.html", "sources.html", "method.html"]
        for page in pages:
            html = (folder / page).read_text(encoding="utf-8")
            collector = _Collector()
            collector.feed(html)
            self.assertEqual(1, collector.headings.count(1), page)
            for previous, current in zip(collector.headings, collector.headings[1:]):
                self.assertLessEqual(current - previous, 1, f"{page} heading jump {previous}->{current}")
            self.assertEqual(collector.tables, collector.captions, page)
            self.assertTrue(all(scope in {"col", "row"} for scope in collector.th_scopes if scope is not None), page)
            broken = [anchor for anchor in collector.anchors if anchor != "#" and anchor[1:] not in collector.ids]
            self.assertEqual([], broken, page)
        index = (folder / "index.html").read_text(encoding="utf-8")
        issues = (folder / "issues.html").read_text(encoding="utf-8")
        criteria = (folder / "criteria.html").read_text(encoding="utf-8")
        sources = (folder / "sources.html").read_text(encoding="utf-8")
        method = (folder / "method.html").read_text(encoding="utf-8")
        self.assertIn("page-header", index)
        self.assertIn("report-actions", index)
        self.assertIn("section-nav", index)
        self.assertIn("criterion-index", criteria)
        self.assertIn("issue-index", issues)
        self.assertIn("component-index", issues)
        self.assertIn("Component index", issues)
        self.assertIn("What to do next", issues)
        self.assertIn("Verification", issues)
        self.assertIn('id="component-', issues)
        self.assertIn("Complete assessment metadata", sources)
        self.assertIn('id="position-heading"', method)
        self.assertIn("Why this is different", method)
        self.assertIn("WCAG-EM", method)
        self.assertIn('href="criteria.html#sc-', issues)
        self.assertIn('href="issues.html#issue-', criteria)

    def test_summary_separates_status_from_release_applicability(self):
        folder, _ = self.render()
        html = (folder / "index.html").read_text(encoding="utf-8")
        self.assertIn("What this report says about Drupal Core 11.4.12", html)
        self.assertIn("How to read this report", html)
        self.assertIn("<th scope=\"col\">Drupal.org status</th>", html)
        self.assertIn("<th scope=\"col\">Applies to this release?</th>", html)
        self.assertIn("Not yet determined", html)
        self.assertIn("does not mean the release is accessible or inaccessible", html)
        self.assertIn("No reported problem has been reproduced against this release", html)
        issues = (folder / "issues.html").read_text(encoding="utf-8")
        self.assertIn("Drupal.org status</dt>", issues)
        self.assertNotIn("Unknown (insufficient target-specific evidence)", html)

    def test_summary_counts_are_derived_from_findings(self):
        folder, artifact = self.render()
        html = (folder / "index.html").read_text(encoding="utf-8")
        self.assertIn(f"We collected {len(artifact['findings'])} active accessibility issues", html)
        self.assertIn("1 finding has a matching fix included in the release", html)

    def test_all_unknown_release_does_not_claim_verified_findings(self):
        analysis = self.build_analysis()
        for finding in analysis["findings"]:
            finding["applicability"] = "unknown"
            finding["basis"] = "none"
            finding["reason"] = "No target-specific evidence supplied."
        analysis["summary"]["by_applicability"] = {"unknown": len(analysis["findings"])}
        with tempfile.TemporaryDirectory() as folder:
            render_report(analysis, folder)
            html = (Path(folder) / "index.html").read_text(encoding="utf-8")
        self.assertIn("0 issues are verified problems in this release", html)
        self.assertIn("No reported problem has been reproduced against this release", html)
        self.assertIn("not yet determined", html)

    def test_report_does_not_emit_conformance_terms_for_issue_evidence(self):
        folder, _ = self.render()
        for page in ["index.html", "issues.html", "criteria.html", "sources.html", "method.html"]:
            html = (folder / page).read_text(encoding="utf-8")
            self.assertNotIn("Partially Supports", html, page)
            self.assertNotIn(">Supports<", html, page)

    def test_outputs_are_written_and_digest_preserved(self):
        folder, artifact = self.render()
        evidence = json.loads((folder / "evidence.json").read_text(encoding="utf-8"))
        summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(artifact["evidence_digest"], evidence["evidence_digest"])
        self.assertEqual("Drupal Core", summary["target"]["product"])
        self.assertTrue((folder / "report.css").exists())
        self.assertIn("overflow-wrap", (folder / "report.css").read_text(encoding="utf-8"))
        criterion_evidence = json.loads((folder / "criterion-evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(0, criterion_evidence["summary"]["formal_conformance_results"])
        self.assertIn("criterion evidence", (folder / "index.html").read_text(encoding="utf-8"))
        reproduction = json.loads((folder / "reproduction-evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(0, reproduction["summary"]["target_verified"])
        self.assertIn("reproduction evidence", (folder / "index.html").read_text(encoding="utf-8"))

    def test_issue_index_groups_by_applicability_and_explains_unknowns(self):
        folder, artifact = self.render()
        html = (folder / "issues.html").read_text(encoding="utf-8")
        self.assertIn('id="issue-filter-all"', html)
        self.assertIn('id="issue-filter-likely"', html)
        self.assertIn('id="issue-filter-needs-checking"', html)
        self.assertIn('data-group="likely"', html)
        self.assertIn('data-group="needs-checking"', html)
        self.assertIn("Probably affects this release (2)", html)
        self.assertIn("Needs checking (1)", html)
        self.assertIn("Fix included, not behaviourally verified (1)", html)
        self.assertIn("Verified problems (0)", html)
        self.assertIn("No issue in this snapshot has this state", html)
        self.assertIn("Why are these not determined?", html)
        self.assertIn("Reported after this release was cut", html)
        self.assertEqual(
            len(artifact["findings"]),
            html.count('data-applicability="'),
        )

    def test_report_contains_every_issue(self):
        folder, artifact = self.render()
        html = (folder / "issues.html").read_text(encoding="utf-8")
        criteria = (folder / "criteria.html").read_text(encoding="utf-8")
        for finding in artifact["findings"]:
            self.assertIn("id=\"issue-", html)
        self.assertEqual(4, html.count("<article class=\"issue\""))
        self.assertIn("Issue index", html)
        self.assertIn("Criterion index", criteria)


if __name__ == "__main__":
    unittest.main()
