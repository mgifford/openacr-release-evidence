import unittest

from acr_evidence.adapters.drupal import KNOWN_PROJECT_IDS


class ProjectIdTests(unittest.TestCase):
    def test_distribution_project_ids_are_known(self):
        self.assertEqual("3060", KNOWN_PROJECT_IDS["drupal"])
        self.assertEqual("3466967", KNOWN_PROJECT_IDS["drupal_cms"])
        self.assertEqual("3154243", KNOWN_PROJECT_IDS["localgov"])


if __name__ == "__main__":
    unittest.main()
