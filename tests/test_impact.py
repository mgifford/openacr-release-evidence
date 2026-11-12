import json
import unittest

from acr_evidence.impact import coverage, get_criterion_impact, validate_dataset
from acr_evidence.openacr_export import load_catalog


class ImpactDatasetTests(unittest.TestCase):
    def test_all_active_wcag22_criteria_have_impact(self):
        catalog = load_catalog()
        active = {
            str(criterion["id"])
            for chapter in catalog["chapters"] if chapter["id"].startswith("success_criteria")
            for criterion in chapter.get("criteria") or []
            if str(criterion["id"]) != "4.1.1"
        }
        self.assertEqual(86, len(active))
        for criterion in active:
            record = get_criterion_impact(criterion)
            self.assertIsNotNone(record, criterion)
            self.assertTrue(record["barrier"].strip())
            self.assertTrue(record["description"].strip())
            self.assertTrue(record["groups"])
            self.assertTrue(record["sources"])
            self.assertEqual("proposed", record["review_status"])

    def test_wcag22_additions_are_present(self):
        for criterion in ("2.4.11", "2.4.12", "2.4.13", "2.5.7", "2.5.8", "3.2.6", "3.3.7", "3.3.8", "3.3.9"):
            record = get_criterion_impact(criterion)
            self.assertEqual("2.2", record["introduced_in"], criterion)

    def test_4_1_1_is_historical_not_active(self):
        self.assertIsNone(get_criterion_impact("4.1.1"))
        historical = json.load(open("data/accessibility-impact/wcag/2.2/historical.json", encoding="utf-8"))
        self.assertEqual(["4.1.1"], [item["id"] for item in historical["historical_criteria"]])
        self.assertEqual("removed", historical["historical_criteria"][0]["status"])

    def test_seizure_risk_is_not_hidden_by_fpc_gap(self):
        record = get_criterion_impact("2.3.1")
        groups = {item["id"] for item in record["groups"]}
        self.assertIn("photosensitive_epilepsy", groups)
        self.assertEqual("reviewed-no-mapping", record["standards_mappings"]["section508_fpc"]["status"])

    def test_en301549_is_pending_not_invented(self):
        record = get_criterion_impact("2.3.1")
        self.assertEqual("pending", record["standards_mappings"]["en301549"]["v3.2.1"])
        self.assertEqual("pending", record["standards_mappings"]["en301549"]["v4.1.1"])

    def test_dataset_is_valid_and_complete(self):
        result = coverage()
        self.assertEqual([], validate_dataset())
        self.assertEqual(86, result["active"])
        self.assertEqual(86, result["descriptions"])
        self.assertEqual(86, result["sources"])
        self.assertEqual(86, result["proposed"])


if __name__ == "__main__":
    unittest.main()
