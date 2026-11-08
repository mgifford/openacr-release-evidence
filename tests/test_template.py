import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TemplateTests(unittest.TestCase):
    def test_drupal_acr_template_has_four_components_and_scope_guidance(self):
        text = (ROOT / "templates" / "drupal-acr-template.md").read_text(encoding="utf-8")
        for component in ("Web", "Electronic Documents", "Software", "Authoring Tool"):
            self.assertIn(component, text)
        self.assertIn("Partially Supports", text)
        self.assertIn("Not Applicable", text)
        self.assertIn("/admin", text)
        self.assertIn("1.2.4", text)
        self.assertIn("1.2.5", text)
        self.assertIn("DRAFT TEMPLATE", text)


if __name__ == "__main__":
    unittest.main()
