import unittest

from acr_evidence.reproduction_evidence import build_reproduction_evidence


def analysis():
    return {
        "target": {"assessment_id": "drupal-core-test", "release": "11.4.12"},
        "findings": [{
            "issue_id": "drupal:3619127",
            "source_url": "https://www.drupal.org/project/drupal/issues/3619127",
            "title": "Forms sidebar does not open from Inline Form Errors links",
        }],
    }


class ReproductionEvidenceTests(unittest.TestCase):
    def test_external_reproduction_is_not_target_verification(self):
        artifact = build_reproduction_evidence(analysis())
        entry = next(item for item in artifact["entries"] if item["issue_id"] == "drupal:3619127")
        self.assertTrue(entry["in_active_collection"])
        self.assertEqual("reproduced-and-fixed", entry["source_result"])
        self.assertEqual("not-established", entry["target_applicability"])
        self.assertFalse(entry["target_verified"])
        self.assertIsNone(entry["conformance_result"])
        self.assertEqual(0, artifact["summary"]["target_verified"])

    def test_unmatched_source_is_kept_out_of_active_count(self):
        artifact = build_reproduction_evidence(analysis())
        unmatched = [item for item in artifact["entries"] if not item["in_active_collection"]]
        self.assertTrue(unmatched)
        self.assertGreater(artifact["summary"]["records"], artifact["summary"]["in_active_collection"])


if __name__ == "__main__":
    unittest.main()
