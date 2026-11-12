import unittest

from acr_evidence.surface_assessment import component_results, criterion_results


def issue(surface):
    return {"surface": {"surface": surface}}


class SurfaceAssessmentTests(unittest.TestCase):
    def test_known_issue_is_partial_and_other_surface_is_supports(self):
        results = criterion_results("1.1.1", [issue("authoring")])
        self.assertEqual("Supports", results["web"])
        self.assertEqual("Partially Supports", results["authoring-tool"])

    def test_no_known_issue_on_assessed_surface_is_supports(self):
        results = criterion_results("1.3.2", [])
        self.assertEqual("Supports", results["web"])
        self.assertEqual("Supports", results["authoring-tool"])

    def test_audio_control_is_not_applicable_without_native_audio(self):
        results = criterion_results("1.4.2", [])
        self.assertEqual("Not Applicable", results["web"])
        self.assertEqual("Not Applicable", results["authoring-tool"])

    def test_feature_absence_is_not_applicable(self):
        results = criterion_results("1.2.4", [])
        self.assertEqual("Not Applicable", results["web"])
        self.assertEqual("Not Applicable", results["authoring-tool"])

    def test_component_results_never_emit_does_not_support(self):
        results = component_results([issue("web"), issue("authoring")])
        self.assertEqual("Partially Supports", results["web"])
        self.assertEqual("Partially Supports", results["authoring-tool"])
        self.assertNotIn("Does Not Support", results.values())


if __name__ == "__main__":
    unittest.main()
