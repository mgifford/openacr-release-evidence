import json
import tempfile
import unittest
from pathlib import Path

from acr_evidence.atag import (
    build_report_json,
    classify,
    load_catalog,
    load_scope,
    render_atag_report,
)

ROOT = Path(__file__).resolve().parents[1]


def issue(nid, labels, component="ckeditor.module", title="Example authoring issue"):
    return {
        "id": f"drupal:{nid}",
        "source_id": str(nid),
        "url": f"https://www.drupal.org/project/drupal/issues/{nid}",
        "title": title,
        "component": component,
        "labels": labels,
        "status": {"code": 1, "label": "Active", "workflow_state": "open"},
        "provenance": {"retrieved_at": "2026-11-07T00:00:00Z"},
    }


def collection():
    return {
        "assessment": {"product": "Drupal Core", "release": "11.4.12"},
        "generated_at": "2026-11-07T00:00:00Z",
        "issues": [
            issue(1, ["Accessibility", "atag"], "ckeditor.module", "ATAG generic editor issue"),
            issue(2, ["Accessibility", "atag-a"], "toolbar", "ATAG Part A keyboard issue"),
            issue(3, ["Accessibility", "atag-b"], "filter.module", "ATAG Part B content issue"),
            issue(4, ["atag"], "theme system", "ATAG issue missing Accessibility tag"),
            issue(5, ["Accessibility"], "toolbar", "Not an ATAG issue"),
        ],
    }


class AtagTests(unittest.TestCase):
    def test_catalog_has_63_criteria_and_both_parts(self):
        catalog = load_catalog()
        nums = [c["num"] for p in catalog for g in p["guidelines"] for c in g["successcriteria"]]
        self.assertEqual(63, len(nums))
        self.assertEqual(31, sum(1 for n in nums if n.startswith("A.")))
        self.assertEqual(32, sum(1 for n in nums if n.startswith("B.")))

    def test_tag_classification(self):
        generic = classify(["Accessibility", "atag"], "ckeditor.module", "drupal:1")
        self.assertTrue(generic["is_atag"])
        self.assertEqual([], generic["parts"])
        self.assertEqual(["A", "B"], generic["candidate_parts"])
        self.assertEqual("needs-triage", generic["review_status"])

        part_a = classify(["atag-a"], "toolbar", "drupal:2")
        self.assertEqual(["A"], part_a["parts"])
        self.assertEqual([], part_a["candidate_parts"])
        part_b = classify(["atag", "atag-b"], "filter.module", "drupal:3")
        self.assertEqual(["B"], part_b["parts"])
        criterion = classify(["atag-a.3.1.1"], "toolbar", "drupal:4")
        self.assertEqual(["A.3.1.1"], criterion["criteria"])
        self.assertFalse(classify(["Accessibility"], "toolbar", "drupal:5")["is_atag"])

    def test_curated_scope_overrides_generic_tag(self):
        scope = {"issues": {"drupal:1": {"parts": ["A"], "criteria": ["A.3.1.1"], "basis": "curated", "review_status": "unreviewed"}}}
        result = classify(["atag"], "ckeditor.module", "drupal:1", scope)
        self.assertEqual(["A"], result["parts"])
        self.assertEqual(["A.3.1.1"], result["criteria"])
        self.assertIn("curated", result["basis"])
        self.assertEqual("unreviewed", result["review_status"])

    def test_wai_report_json_is_all_not_checked(self):
        report = build_report_json(collection(), [issue(1, ["atag"], "ckeditor.module")])
        self.assertEqual(63, len(report["evaluationData"]))
        self.assertEqual({"Not checked"}, {item["result"] for item in report["evaluationData"].values()})
        self.assertEqual("AA", report["meta"]["conformanceTarget"]["value"])
        self.assertTrue(report["meta"]["name"]["value"])
        self.assertIn("DRAFT", report["meta"]["executiveSummary"]["value"])
        for item in report["evaluationData"].values():
            self.assertIn("level", item)
            self.assertIn("evaluatedLevel", item)
            self.assertIsNone(item["observations"])

    def test_render_writes_static_report_and_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            result = render_atag_report(collection(), folder, scope=load_scope())
            html = (Path(folder) / "index.html").read_text(encoding="utf-8")
            evidence = json.loads((Path(folder) / "atag-evidence.json").read_text(encoding="utf-8"))
            report = json.loads((Path(folder) / "atag-report.json").read_text(encoding="utf-8"))
            css_exists = (Path(folder) / "report.css").exists()
        self.assertIn("ATAG 2.0 evidence", html)
        self.assertIn("Part A", html)
        self.assertIn("Part B", html)
        self.assertIn("does not currently carry the common Accessibility tag", html)
        self.assertIn("atag-report.json", html)
        self.assertIn("atag-evidence.json", html)
        self.assertNotIn("<script", html)
        self.assertIn('<main id="main" tabindex="-1">', html)
        self.assertEqual(4, evidence["summary"]["issues"])
        self.assertEqual(1, evidence["summary"]["missing_accessibility_tag"])
        self.assertTrue(evidence["issues"][1]["atag"]["is_atag"])
        self.assertEqual("Not checked", next(iter(report["evaluationData"].values()))["result"])
        self.assertTrue(css_exists)

    def test_missing_accessibility_flag(self):
        with tempfile.TemporaryDirectory() as folder:
            result = render_atag_report(collection(), folder)
        self.assertEqual(1, result["summary"]["missing_accessibility_tag"])
        self.assertEqual(4, result["summary"]["issues"])


if __name__ == "__main__":
    unittest.main()
