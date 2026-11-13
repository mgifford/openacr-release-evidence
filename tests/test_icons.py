import tempfile
import unittest
from pathlib import Path

from acr_evidence.icons import (
    SPRITE_PATH,
    copy_sprite,
    icon_description,
    icon_id,
    icon_markup,
    load_mapping,
    validate_sprite,
)


class IconMappingTests(unittest.TestCase):
    def test_mapping_counts(self):
        document, mapping = load_mapping()
        self.assertEqual("1.0", document["version"])
        self.assertEqual(86, sum(1 for item in mapping.values() if item["type"] == "success-criterion"))
        self.assertNotIn("4.1.1", mapping)

    def test_known_and_unknown_icons(self):
        self.assertEqual("sc-1-4-3", icon_id("1.4.3"))
        self.assertIn("contrast", (icon_description("1.4.3") or "").casefold())
        self.assertIsNone(icon_id("4.1.1"))
        markup = icon_markup("1.4.3")
        self.assertIn('aria-hidden="true"', markup)
        self.assertIn('focusable="false"', markup)
        self.assertIn("wcag22_icons.svg#sc-1-4-3", markup)
        self.assertNotIn("<title", markup)
        self.assertEqual("", icon_markup("4.1.1"))

    def test_sprite_is_safe_and_unique(self):
        result = validate_sprite(SPRITE_PATH)
        self.assertEqual(99, result["symbols"])
        self.assertEqual(len(result["ids"]), len(set(result["ids"])))
        source = SPRITE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("<script", source.casefold())
        self.assertNotIn("javascript:", source.casefold())
        self.assertNotIn("<!DOCTYPE", source.upper())
        self.assertNotIn("<!ENTITY", source.upper())

    def test_copy_sprite(self):
        with tempfile.TemporaryDirectory() as folder:
            path = copy_sprite(folder)
            self.assertTrue(path.is_file())
            self.assertEqual("wcag22_icons.svg", path.name)


if __name__ == "__main__":
    unittest.main()
