import unittest

from acr_evidence.criterion_evidence import build_criterion_evidence


def analysis():
    return {
        "assessment": {"id": "drupal-core-test", "product": "Drupal Core"},
        "target": {"assessment_id": "drupal-core-test", "release": "11.4.12", "ref": "11.4.12"},
        "generated_at": "2026-11-11T00:00:00Z",
        "findings": [
            {
                "issue_id": "drupal:1",
                "source_url": "https://www.drupal.org/project/drupal/issues/1",
                "title": "Reported web barrier",
                "component": "forms system",
                "tracker_status_label": "Active",
                "evidence_status": "inventory",
                "applicability": "unknown",
                "wcag_candidates": ["1.1.1"],
                "surface": {"surface": "web", "basis": "default-web"},
            }
        ],
    }


class CriterionEvidenceTests(unittest.TestCase):
    def test_issue_tag_is_reported_evidence_not_conformance(self):
        ledger = build_criterion_evidence(analysis())
        criterion = next(item for item in ledger["criteria"] if item["criterion"] == "1.1.1")
        components = {item["component"]: item for item in criterion["components"]}
        web = components["web"]
        self.assertEqual("reported-barrier-unverified", web["evidence_state"])
        self.assertEqual("issue-tag", web["candidate_relationship"])
        self.assertEqual("unreviewed", web["relationship_review_status"])
        self.assertIsNone(web["conformance_result"])
        self.assertEqual("drupal:1", web["issues"][0]["issue_id"])
        self.assertEqual("insufficient-evidence", components["authoring-tool"]["evidence_state"])
        self.assertEqual("partial", criterion["automation"]["coverage"])
        self.assertIn("image-alt", criterion["automation"]["axe_rules"])
        self.assertEqual("not-recorded", criterion["automation"]["result"])
        self.assertEqual("method-available-not-recorded", criterion["automation"]["guidepup"])
        self.assertEqual(0, ledger["summary"]["formal_conformance_results"])

    def test_media_scope_is_recorded_separately_from_empty_queue(self):
        ledger = build_criterion_evidence(analysis())
        criterion = next(item for item in ledger["criteria"] if item["criterion"] == "1.2.1")
        web = next(item for item in criterion["components"] if item["component"] == "web")
        self.assertEqual("outside-documented-scope", web["evidence_state"])
        self.assertIn("does not provide audio/video", web["scope_basis"])
        self.assertIsNone(web["conformance_result"])


if __name__ == "__main__":
    unittest.main()
