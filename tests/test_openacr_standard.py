import copy
import json
import tempfile
import unittest
from pathlib import Path

from acr_evidence.openacr_export import (
    DEFAULT_CATALOG,
    DEFAULT_SCHEMA,
    OPENACR_SOURCE,
    build_draft,
    export_openacr,
    load_catalog,
    validate_document,
    validate_file,
)

try:
    import jsonschema  # noqa: F401
    import yaml  # noqa: F401
    HAVE_OPENACR = True
except ImportError:
    HAVE_OPENACR = False


def analysis():
    return {
        "schema_version": "0.2.0",
        "artifact_type": "drupal-release-applicability-draft",
        "assessment": {
            "id": "drupal-core-11.4.12-default-admin",
            "product": "Drupal Core",
            "release": "11.4.12",
            "ref": "11.4.12",
            "installation": {"configuration": "Default Admin theme enabled."},
        },
        "target": {
            "assessment_id": "drupal-core-11.4.12",
            "product": "Drupal Core",
            "release": "11.4.12",
            "ref": "11.4.12",
            "ref_type": "tag",
            "support_status": "supported",
            "release_line": "11.4.x",
            "parent_project": None,
        },
        "generated_at": "2026-11-07T00:00:00Z",
        "evidence_digest": "evidence-digest",
        "findings": [],
        "issues": [],
    }


def _has_adherence(value):
    if isinstance(value, dict):
        return "adherence" in value or any(_has_adherence(v) for v in value.values())
    if isinstance(value, list):
        return any(_has_adherence(v) for v in value)
    return False


@unittest.skipUnless(HAVE_OPENACR, "jsonschema and PyYAML are optional dependencies")
class OpenACRExportTests(unittest.TestCase):
    def test_vendored_standards_are_present_and_pinned(self):
        self.assertTrue(DEFAULT_SCHEMA.exists())
        self.assertTrue(DEFAULT_CATALOG.exists())
        self.assertEqual("d6d18a93d8b043f7edfec13834f2d6b9557c5dbd", OPENACR_SOURCE["commit"])
        catalog = load_catalog()
        self.assertEqual(7, len(catalog["chapters"]))
        self.assertEqual(182, sum(len(chapter["criteria"]) for chapter in catalog["chapters"]))

    def test_draft_is_schema_and_catalog_valid_without_conformance_values(self):
        catalog = load_catalog()
        document = build_draft(analysis(), catalog)
        result = validate_document(document, catalog)
        self.assertTrue(result["valid"], result["errors"])
        self.assertTrue(document["draft"])
        self.assertEqual("reviewer@example.invalid", document["author"]["email"])
        self.assertEqual(7, len(document["chapters"]))
        self.assertEqual(182, sum(len(chapter["criteria"]) for chapter in document["chapters"].values()))
        self.assertFalse(_has_adherence(document))
        self.assertNotIn("not-evaluated", str(document))
        self.assertIn("DRAFT", document["title"])

    def test_export_writes_yaml_and_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            result = export_openacr(analysis(), folder)
            yaml_text = Path(result["yaml"]).read_text(encoding="utf-8")
            validation = json.loads(Path(result["validation"]).read_text(encoding="utf-8"))
        self.assertIn("catalog: 2.5-edition-wcag-2.2-508-en", yaml_text)
        self.assertTrue(validation["valid"])
        self.assertTrue(validation["draft"])
        self.assertEqual(OPENACR_SOURCE["commit"], validation["source"]["commit"])
        self.assertEqual("2026-11-07T00:00:00Z", validation["checked_at"])

    def test_schema_failure_is_reported(self):
        catalog = load_catalog()
        document = build_draft(analysis(), catalog)
        broken = copy.deepcopy(document)
        del broken["title"]
        result = validate_document(broken, catalog)
        self.assertFalse(result["valid"])
        self.assertTrue(any("schema:" in error for error in result["errors"]))

    def test_catalog_failure_is_reported(self):
        catalog = load_catalog()
        document = build_draft(analysis(), catalog)
        broken = copy.deepcopy(document)
        broken["chapters"]["success_criteria_level_a"]["criteria"].append({"num": "99.99"})
        result = validate_document(broken, catalog)
        self.assertFalse(result["valid"])
        self.assertTrue(any("99.99" in error for error in result["errors"]))

    def test_not_evaluated_is_rejected_for_level_a_and_aa(self):
        catalog = load_catalog()
        document = build_draft(analysis(), catalog)
        broken = copy.deepcopy(document)
        broken["chapters"]["success_criteria_level_aa"]["criteria"][0]["components"] = [
            {"name": "web", "adherence": {"level": "not-evaluated"}}
        ]
        result = validate_document(broken, catalog)
        self.assertFalse(result["valid"])
        self.assertTrue(any("not-evaluated" in error for error in result["errors"]))

    def test_strict_requires_reviewed_values(self):
        catalog = load_catalog()
        document = build_draft(analysis(), catalog)
        result = validate_document(document, catalog, strict=True)
        self.assertFalse(result["valid"])
        self.assertTrue(any("draft" in error for error in result["errors"]))
        self.assertTrue(any("placeholder" in error for error in result["errors"]))

    def test_validate_file_matches_export(self):
        with tempfile.TemporaryDirectory() as folder:
            result = export_openacr(analysis(), folder)
            checked = validate_file(result["yaml"])
        self.assertTrue(checked["valid"], checked["errors"])
        self.assertTrue(checked["draft"])


if __name__ == "__main__":
    unittest.main()
