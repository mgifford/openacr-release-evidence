import unittest

from acr_evidence.fpc import disability_labels, load_mapping, summarize


class FpcTests(unittest.TestCase):
    def test_disability_labels_for_criterion(self):
        labels = disability_labels("1.1.1")
        self.assertIn("Vision", labels)
        self.assertIn("Hearing", labels)
        self.assertIn("Cognitive/learning", labels)

    def test_mapping_has_all_functional_categories(self):
        mapping = load_mapping()
        self.assertEqual(9, len(mapping))
        self.assertIn("1.2.2", mapping["WH"])
        self.assertIn("1.4.2", mapping["WV"])

    def test_without_hearing_reflects_authoring_caption_exception(self):
        result = summarize({
            "1.1.1": {"web": "Partially Supports", "authoring-tool": "Partially Supports"},
            "1.2.1": {"web": "Not Applicable", "authoring-tool": "Not Applicable"},
            "1.2.2": {"web": "Supports", "authoring-tool": "Partially Supports"},
            "1.2.4": {"web": "Not Applicable", "authoring-tool": "Not Applicable"},
            "1.3.3": {"web": "Supports", "authoring-tool": "Supports"},
        })
        without_hearing = next(row for row in result["rows"] if row["id"] == "WH")
        self.assertEqual("Partially Supports", without_hearing["status"])
        self.assertIn("1.2.2", without_hearing["criteria"])

    def test_mapped_summary_never_emits_does_not_support_without_evidence(self):
        result = summarize({})
        self.assertNotIn("Does Not Support", {row["status"] for row in result["rows"]})


if __name__ == "__main__":
    unittest.main()
