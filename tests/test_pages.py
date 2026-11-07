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
        for name in ("index.html", "report.css", "evidence.json", "summary.json"):
            self.assertIn(name, workflow)


if __name__ == "__main__":
    unittest.main()
