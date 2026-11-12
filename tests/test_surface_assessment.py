import unittest

from acr_evidence.surface_assessment import component_results, criterion_results


def issue(surface):
    return {"surface": {"surface": surface}}


class SurfaceAssessmentTests(unittest.TestCase):
    def test_reported_issue_does_not_create_partial_support(self):
        results = criterion_results("1.1.1", [issue("authoring")])
        self.assertEqual("Not Evaluated", results["web"])
        self.assertEqual("Not Evaluated", results["authoring-tool"])

    def test_empty_queue_does_not_create_support(self):
        results = criterion_results("1.3.2", [])
        self.assertEqual("Not Evaluated", results["web"])
        self.assertEqual("Not Evaluated", results["authoring-tool"])

    def test_audio_control_is_not_applicable_without_native_audio(self):
        results = criterion_results("1.4.2", [])
        self.assertEqual("Not Applicable", results["web"])
        self.assertEqual("Not Applicable", results["authoring-tool"])

    def test_feature_absence_is_not_applicable(self):
        results = criterion_results("1.2.4", [])
        self.assertEqual("Not Applicable", results["web"])
        self.assertEqual("Not Applicable", results["authoring-tool"])

    def test_component_results_do_not_grade_the_queue(self):
        results = component_results([issue("web"), issue("authoring")])
        self.assertEqual("Not Evaluated", results["web"])
        self.assertEqual("Not Evaluated", results["authoring-tool"])
        self.assertNotIn("Supports", results.values())
        self.assertNotIn("Partially Supports", results.values())
        self.assertNotIn("Does Not Support", results.values())

    def test_explicit_broad_failure_is_still_honoured(self):
        policy = {
            "surfaces": {},
            "does_not_support": [{"criterion": "1.1.1", "surface": "web"}],
        }
        results = criterion_results("1.1.1", [], policy=policy)
        self.assertEqual("Does Not Support", results["web"])
        self.assertEqual("Not Evaluated", results["authoring-tool"])


if __name__ == "__main__":
    unittest.main()
