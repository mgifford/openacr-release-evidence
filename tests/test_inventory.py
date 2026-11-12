import json
import tempfile
import unittest
from pathlib import Path

from acr_evidence.inventory import (
    build_inventory,
    compare_inventories,
    extension_status,
    parse_info_yml,
)
from acr_evidence.model import digest_artifact


INFO = """\
# A comment
name: 'Node'
type: module
description: 'Core module'
package: Core
version: VERSION
dependencies:
  - drupal:text
  - drupal:field (>= 10.0)
"""


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_tree(root, *, beta=False):
    write(root / "core/modules/node/node.info.yml", INFO)
    write(root / "core/modules/text/text.info.yml", "name: Text\ntype: module\ndependencies:\n  - drupal:field\n")
    write(root / "core/modules/field/field.info.yml", "name: Field\ntype: module\ndependencies:\n  - drupal:system\n")
    write(root / "core/modules/system/system.info.yml", "name: System\ntype: module\n")
    write(root / "core/modules/action/action.info.yml", "name: Action\ntype: module\nlifecycle: deprecated\n")
    write(root / "core/themes/default_admin/default_admin.info.yml",
          "name: Default Admin\ntype: theme\nbase theme: false\nlifecycle: experimental\n")
    if not beta:
        write(root / "core/themes/olivero/olivero.info.yml", "name: Olivero\ntype: theme\nbase theme: false\n")
        write(root / "core/themes/claro/claro.info.yml", "name: Claro\ntype: theme\nbase theme: false\n")
        write(root / "core/themes/stable9/stable9.info.yml",
              "name: Stable 9\ntype: theme\nlifecycle: deprecated\n")
    install = ["node"]
    themes = ["olivero", "claro"] if not beta else ["default_admin"]
    system_theme = "admin: claro\ndefault: olivero\n" if not beta else "admin: default_admin\ndefault: default_admin\n"
    write(
        root / "core/profiles/standard/standard.info.yml",
        "name: Standard\ntype: profile\ninstall:\n  - node\nthemes:\n"
        + "".join(f"  - {item}\n" for item in themes),
    )
    write(root / "core/profiles/standard/config/install/system.theme.yml", system_theme)


class InfoYamlTests(unittest.TestCase):
    def test_parses_shallow_keys_and_lists(self):
        info = parse_info_yml(INFO)
        self.assertEqual("Node", info["name"])
        self.assertEqual(["drupal:text", "drupal:field (>= 10.0)"], info["dependencies"])

    def test_legacy_experimental_and_deprecated(self):
        self.assertEqual(("experimental", "experimental"), extension_status({"experimental": "true"}))
        self.assertEqual(("experimental", "package-label"), extension_status({"package": "Core (Experimental)"}))
        self.assertEqual(("deprecated", "lifecycle"), extension_status({"lifecycle": "deprecated"}))
        self.assertEqual(("stable", "no-lifecycle-field"), extension_status({}))


class InventoryTests(unittest.TestCase):
    def build(self, beta=False):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture_tree(root, beta=beta)
            return build_inventory(
                root,
                ref="12.0.0-beta2" if beta else "11.4.12",
                commit="a" * 40,
                retrieved_at="2026-11-12T00:00:00Z",
            )

    def test_counts_bundled_installed_and_defaults(self):
        inventory = self.build()
        self.assertEqual(5, inventory["counts"]["modules_bundled"])
        self.assertEqual(4, inventory["counts"]["themes_bundled"])
        self.assertEqual(4, inventory["counts"]["modules_installed_by_standard_profile"])
        self.assertEqual(2, inventory["counts"]["themes_installed_by_standard_profile"])
        self.assertEqual("olivero", inventory["profile"]["default_theme"])
        self.assertEqual("claro", inventory["profile"]["admin_theme"])
        self.assertEqual(1, inventory["counts"]["modules_deprecated"])
        self.assertEqual(1, inventory["counts"]["themes_experimental"])

    def test_dependency_closure_and_not_installed(self):
        inventory = self.build()
        modules = {item["machine_name"]: item for item in inventory["components"] if item["type"] == "module"}
        self.assertTrue(modules["field"]["installed_by_standard_profile"])
        self.assertFalse(modules["action"]["installed_by_standard_profile"])
        self.assertTrue(modules["action"]["bundled"])

    def test_removal_is_not_a_fix_or_an_inheritance_claim(self):
        before = self.build(beta=False)
        after = self.build(beta=True)
        comparison = compare_inventories(before, after)
        removed = {(item["type"], item["machine_name"]) for item in comparison["removed"]}
        self.assertIn(("theme", "claro"), removed)
        self.assertIn(("theme", "olivero"), removed)
        self.assertIn(("theme", "stable9"), removed)
        self.assertIn("removed does not mean fixed", comparison["disclaimer"].casefold())
        self.assertNotIn("lineage", comparison)

    def test_digest_is_reproducible(self):
        first = self.build()
        second = self.build()
        self.assertEqual(first["content_digest"], second["content_digest"])
        self.assertEqual(first["evidence_digest"], second["evidence_digest"])
        self.assertEqual(digest_artifact(first), first["evidence_digest"])

    def test_artifact_type_and_disclaimer(self):
        inventory = self.build()
        self.assertEqual("drupal-component-inventory", inventory["artifact_type"])
        self.assertIn("not an accessibility assessment", inventory["disclaimer"])


if __name__ == "__main__":
    unittest.main()
