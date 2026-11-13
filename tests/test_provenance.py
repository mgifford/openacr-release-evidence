import unittest

from acr_evidence.provenance import associate_issue, component_from_path, is_test_path


ISSUE = {
    "id": "drupal:3159933",
    "source": "drupal",
    "source_id": "3159933",
    "url": "https://www.drupal.org/project/drupal/issues/3159933",
    "component": "markup",
    "title": "Status Message in Claro on theme install should have role=status",
    "description_text": "The status message in the Claro theme uses the wrong landmark.",
}


class PathMappingTests(unittest.TestCase):
    def test_core_extension_paths(self):
        self.assertEqual(("theme", "default_admin"), component_from_path("core/themes/default_admin/css/base/elements.css"))
        self.assertEqual(("module", "navigation"), component_from_path("core/modules/navigation/navigation.module"))
        self.assertEqual(("profile", "standard"), component_from_path("core/profiles/standard/standard.info.yml"))

    def test_core_library_is_not_attributed_to_a_module(self):
        self.assertIsNone(component_from_path("core/lib/Drupal/Core/Form/FormBuilder.php"))
        self.assertIsNone(component_from_path("composer.json"))

    def test_test_only_paths_are_excluded_by_default(self):
        path = "core/modules/layout_builder/tests/src/FunctionalJavascript/DialogTest.php"
        self.assertTrue(is_test_path(path))
        self.assertIsNone(component_from_path(path))
        self.assertEqual(("module", "layout_builder"), component_from_path(path, include_tests=True))
        self.assertIsNone(component_from_path("core/tests/Drupal/FunctionalJavascriptTests/Ajax/DialogTest.php"))


class AssociationTests(unittest.TestCase):
    def test_changed_path_is_verified_source_code(self):
        result = associate_issue(
            ISSUE,
            changed_paths=["core/themes/default_admin/css/base/elements.css"],
            known_components={("theme", "default_admin")},
        )
        self.assertEqual("verified-source-code", result["level"])
        self.assertEqual("default_admin", result["primary"]["component"])

    def test_ambiguous_component_label_is_not_verified(self):
        issue = dict(ISSUE, component="Admin theme", title="Buttons are hard to see", description_text="")
        result = associate_issue(
            issue,
            known_components={("theme", "default_admin"), ("theme", "claro")},
        )
        self.assertEqual("unknown", result["level"])
        self.assertEqual([], result["associations"])

    def test_title_mention_is_only_a_strong_candidate(self):
        result = associate_issue(
            ISSUE,
            known_components={("theme", "claro"), ("theme", "default_admin")},
        )
        self.assertEqual("strong-candidate", result["level"])
        self.assertEqual("claro", result["primary"]["component"])

    def test_explicit_alias_is_explicit_metadata(self):
        result = associate_issue(
            dict(ISSUE, component="Admin theme", title="Buttons are hard to see"),
            component_aliases={"Admin theme": ["default_admin"]},
        )
        self.assertEqual("explicit-metadata", result["level"])

    def test_multiple_components_keep_one_issue(self):
        issue = dict(
            ISSUE,
            changed_paths=None,
            component="markup",
            title="Claro and Default Admin status messages use the wrong landmark",
        )
        result = associate_issue(
            issue,
            changed_paths=[
                "core/themes/claro/css/base/elements.css",
                "core/themes/default_admin/css/base/elements.css",
            ],
            known_components={("theme", "claro"), ("theme", "default_admin")},
        )
        self.assertTrue(result["multiple"])
        self.assertEqual(2, len(result["associations"]))
        self.assertEqual("drupal:3159933", result["issue_id"])

    def test_association_does_not_claim_applicability_or_conformance(self):
        result = associate_issue(ISSUE, changed_paths=["core/themes/claro/css/base/elements.css"])
        serialized = str(result).casefold()
        for forbidden in ("applicable", "conformance", "fixed", "supports"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
