import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContextTests(unittest.TestCase):
    def test_drupal_ecosystem_context_files_exist_and_reference_template(self):
        expected = ("DRUPAL.md", "DRUPAL-CMS.md", "LOCALGOV.md", "CKEDITOR.md")
        for name in expected:
            text = (ROOT / "context" / name).read_text(encoding="utf-8")
            self.assertIn("templates/drupal-acr-template.md", text, name)
            self.assertIn("Authoring", text, name)
            self.assertIn("human-maintained", text.casefold(), name)


if __name__ == "__main__":
    unittest.main()
