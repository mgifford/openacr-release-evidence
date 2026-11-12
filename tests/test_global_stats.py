import unittest

from acr_evidence.impact import load_global_stats


class GlobalStatsTests(unittest.TestCase):
    def test_global_statistics_have_source_metadata(self):
        data = load_global_stats()
        self.assertEqual(3, len(data["statistics"]))
        for item in data["statistics"]:
            self.assertTrue(item["source_url"].startswith("https://www.who.int/"))
            self.assertTrue(item["source_publication_date"])
            self.assertTrue(item["population_definition"])
            self.assertTrue(item["limitations"])
            self.assertEqual("global", item["geography"])

    def test_statistics_are_context_not_drupal_counts(self):
        data = load_global_stats()
        text = str(data).casefold()
        self.assertNotIn("estimated_excluded", text)
        self.assertIn("not counts of drupal users", text)
