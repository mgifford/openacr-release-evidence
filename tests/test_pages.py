import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"


class _Headings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []

    def handle_starttag(self, tag, attrs):
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(int(tag[1]))


class PagesTests(unittest.TestCase):
    def test_landing_page_is_static_and_links_to_reports(self):
        html = (REPORTS / "index.html").read_text(encoding="utf-8")
        self.assertIn('lang="en"', html)
        self.assertIn('<a class="skip" href="#main">', html)
        self.assertIn('<main id="main" tabindex="-1">', html)
        self.assertNotIn("<script", html)
        self.assertIn("./drupal-core-11.4.12/", html)
        self.assertIn("./drupal-core-11.4.12/evidence.json", html)
        self.assertIn("./drupal-core-11.4.12/summary.json", html)
        self.assertIn("./drupal-core-11.4.12/openacr.yaml", html)
        self.assertIn("./drupal-core-11.4.12/openacr-validation.json", html)
        self.assertIn("./drupal-core-11.4.12/acr.html", html)
        self.assertIn("./drupal-core-atag/", html)
        self.assertIn("./drupal-core-atag/atag-report.json", html)
        self.assertIn('id="finder-heading"', html)
        self.assertIn('id="filter-status-supported"', html)
        self.assertIn('href="./matrix.html"', html)
        self.assertIn("release-card", html)
        self.assertIn('id="position-heading"', html)
        self.assertIn("Why this ACR is different", html)
        self.assertIn("GSA OpenACR issue #180", html)
        self.assertNotRegex(html, r'href="[^"]*(?:collection|analysis)\.json"')
        self.assertNotIn("supports", html.casefold())

        parser = _Headings()
        parser.feed(html)
        self.assertEqual(1, parser.headings.count(1))
        for previous, current in zip(parser.headings, parser.headings[1:]):
            self.assertLessEqual(current - previous, 1, f"heading jump {previous}->{current}")

    def test_relative_links_resolve(self):
        html = (REPORTS / "index.html").read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = (REPORTS / href.split("#")[0]).resolve()
            self.assertTrue(target.exists(), f"missing link target: {href}")




    def test_matrix_page_preserves_all_issues_and_targets(self):
        matrix = (REPORTS / "matrix.html").read_text(encoding="utf-8")
        self.assertIn("Cross-release", matrix)
        self.assertIn("Complete cross-target applicability matrix", matrix)
        self.assertNotIn("<script", matrix)
        html = (REPORTS / "index.html").read_text(encoding="utf-8")
        self.assertEqual(5, html.count('class="release-card"'))
        collection = json.loads((REPORTS / "collection.json").read_text(encoding="utf-8"))
        summary = collection["summary"]
        collected = summary["collected"]
        self.assertIn(f"<dt>Unique active issues</dt><dd>{collected}</dd>", html)
        self.assertEqual(collected, matrix.count('<th scope="row">'))
        self.assertGreater(summary["detailed"], 0)
        self.assertGreater(summary["inventory"], 0)
        self.assertGreater(summary["with_merge_requests"], 0)
        self.assertIn("cross-release applicability matrix", matrix)

    def test_each_target_report_links_validated_openacr(self):
        for directory in sorted(REPORTS.glob("drupal-core-*")):
            if not directory.is_dir() or not (directory / "evidence.json").exists():
                continue
            html = (directory / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="./openacr.yaml"', html)
            self.assertIn('href="./openacr-validation.json"', html)
            self.assertIn('href="./acr.html"', html)
            self.assertIn("report-actions", html)
            self.assertIn("section-nav", html)
            for page in ("issues.html", "criteria.html", "sources.html", "method.html"):
                self.assertTrue((directory / page).is_file(), f"{directory.name}/{page}")
                self.assertIn(f'href="./{page}"', html)
            self.assertTrue((directory / "wcag22_icons.svg").is_file())
            self.assertTrue((directory / "issue-provenance.json").is_file())
            self.assertIn("issue-provenance.json", (directory / "index.html").read_text(encoding="utf-8"))
            self.assertIn("wcag22_icons.svg", (directory / "criteria.html").read_text(encoding="utf-8"))
            issues = (directory / "issues.html").read_text(encoding="utf-8")
            criteria = (directory / "criteria.html").read_text(encoding="utf-8")
            self.assertIn("issue-index", issues)
            self.assertIn("component-index", issues)
            self.assertIn("criterion-index", criteria)
            self.assertTrue((directory / "openacr.yaml").is_file())
            self.assertTrue((directory / "acr.html").is_file())
            self.assertTrue((directory / "acr.md").is_file())
            acr = (directory / "acr.html").read_text(encoding="utf-8")
            self.assertIn("Not Evaluated", acr)
            self.assertIn('href="./report.css"', acr)
            self.assertIn('href="./index.html"', acr)
            self.assertIn('class="section-nav"', acr)
            self.assertNotIn("<script", acr)
            validation = json.loads((directory / "openacr-validation.json").read_text(encoding="utf-8"))
            self.assertTrue(validation["valid"])
            self.assertTrue(validation["draft"])
            self.assertEqual("openacr-0.1.0.json", validation["schema"])
            self.assertIn(validation["catalog"], (directory / "openacr.yaml").read_text(encoding="utf-8"))


    def test_atag_report_files_and_wai_json(self):
        directory = REPORTS / "drupal-core-atag"
        html = (directory / "index.html").read_text(encoding="utf-8")
        self.assertIn("ATAG 2.0", html)
        self.assertIn('href="./atag-report.json"', html)
        self.assertIn('href="./atag-evidence.json"', html)
        self.assertNotIn("<script", html)
        report = json.loads((directory / "atag-report.json").read_text(encoding="utf-8"))
        evidence = json.loads((directory / "atag-evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(63, len(report["evaluationData"]))
        self.assertEqual({"Not checked"}, {item["result"] for item in report["evaluationData"].values()})
        self.assertIn("evaluationId", report["meta"])
        self.assertEqual("2.0", evidence["atag_version"])
        self.assertGreaterEqual(evidence["summary"]["issues"], 1)
        for issue in evidence["issues"]:
            self.assertTrue(issue["atag"]["is_atag"])

    def test_split_report_links_and_fragments_resolve(self):
        for directory in sorted(REPORTS.glob("drupal-core-*")):
            if not directory.is_dir() or not (directory / "index.html").exists():
                continue
            pages = ["index.html", "issues.html", "criteria.html", "sources.html", "method.html", "acr.html"]
            ids = {
                page: set(re.findall(r'id="([^"]+)"', (directory / page).read_text(encoding="utf-8")))
                for page in pages if (directory / page).exists()
            }
            for page in pages:
                path = directory / page
                if not path.exists():
                    continue
                for href in re.findall(r'<a\b[^>]*href="([^"]+)"', path.read_text(encoding="utf-8")):
                    if href.startswith(("http://", "https://", "mailto:", "javascript:")):
                        continue
                    target, _, fragment = href.partition("#")
                    if not target:
                        continue
                    destination = directory / target
                    self.assertTrue(destination.exists(), f"{path}: missing {href}")
                    if fragment:
                        self.assertIn(fragment, ids.get(target, set()), f"{path}: missing fragment {href}")

    def test_pages_workflow_publishes_split_report_pages(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        for page in ("issues.html", "criteria.html", "sources.html", "method.html", "wcag22_icons.svg"):
            self.assertIn(page, workflow)

    def test_workflows_use_node24_actions(self):
        expected = {
            "actions/checkout@v7",
            "actions/setup-python@v7",
            "actions/upload-artifact@v7",
            "actions/configure-pages@v6",
            "actions/upload-pages-artifact@v5",
            "actions/deploy-pages@v5",
        }
        workflows = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / ".github" / "workflows").glob("*.yml"))
        )
        for action in expected:
            self.assertIn(action, workflows)
        self.assertNotIn("actions/checkout@v4", workflows)
        self.assertNotIn("actions/setup-python@v5", workflows)
        self.assertNotIn("actions/upload-artifact@v4", workflows)
        self.assertNotIn("actions/configure-pages@v5", workflows)
        self.assertNotIn("actions/upload-pages-artifact@v3", workflows)
        self.assertNotIn("actions/deploy-pages@v4", workflows)

    def test_weekly_workflow_is_review_gated(self):
        weekly = (ROOT / ".github" / "workflows" / "weekly.yml").read_text(encoding="utf-8")
        self.assertIn("schedule:", weekly)
        self.assertIn("workflow_dispatch:", weekly)
        self.assertIn("acr-evidence multi", weekly)
        self.assertIn("acr-evidence atag-report", weekly)
        self.assertIn("acr-evidence weekly-summary", weekly)
        self.assertIn("HF_TOKEN", weekly)
        self.assertIn("reports/weekly", weekly)
        self.assertIn("--previous-collection reports/collection.json", weekly)
        self.assertIn("gh pr create", weekly)
        self.assertIn("contents: write", weekly)
        self.assertIn("pull-requests: write", weekly)
        self.assertIn("${{ github.token }}", weekly)
        self.assertNotIn("deploy-pages", weekly)

    def test_pages_workflow_uses_allowlist_and_pages_actions(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch", workflow)
        self.assertIn("branches: [main]", workflow)
        self.assertIn("reports/**", workflow)
        self.assertIn("github-pages", workflow)
        self.assertIn("actions/upload-pages-artifact", workflow)
        self.assertIn("actions/deploy-pages", workflow)
        self.assertIn("private-evidence", workflow)
        self.assertIn("collection.json", workflow)
        self.assertIn("analysis.json", workflow)
        self.assertIn("grep -RIn '<script'", workflow)
        self.assertIn("matrix.html", workflow)
        for name in ("index.html", "report.css", "evidence.json", "summary.json", "openacr.yaml", "openacr-validation.json", "acr.html", "acr.md", "atag-report.json", "atag-evidence.json"):
            self.assertIn(name, workflow)


if __name__ == "__main__":
    unittest.main()
