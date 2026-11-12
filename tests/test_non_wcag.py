import unittest

from acr_evidence.non_wcag import load_considerations


class NonWcagTests(unittest.TestCase):
    def test_considerations_cover_preferences_and_motion(self):
        data = load_considerations()
        ids = {item["id"] for item in data["items"]}
        self.assertIn("en301549-user-preferences", ids)
        self.assertIn("visually-induced-motion-sickness", ids)
        self.assertIn("prefers-reduced-motion", ids)
        self.assertIn("forced-colors", ids)

    def test_items_are_not_conformance_results(self):
        data = load_considerations()
        for item in data["items"]:
            self.assertEqual("not-evaluated", item["evidence_state"])
            self.assertEqual("unreviewed", item["review_status"])
            self.assertNotIn("Supports", item["evidence_state"])
