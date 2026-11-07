import json
import tempfile
import unittest
from pathlib import Path

from acr_evidence.model import assess

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(HAVE_YAML, "PyYAML is an optional dependency")
class WorksheetTests(unittest.TestCase):
    def test_worksheet_never_emits_supports(self):
        from acr_evidence.openacr import export_worksheet

        manifest = json.loads((ROOT / "config" / "drupal-core-example.json").read_text())
        issues = json.loads((ROOT / "tests" / "fixtures" / "issues.json").read_text())
        evidence = assess(manifest, issues, generated_at="2026-11-07T00:00:00Z")
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "draft.yaml"
            export_worksheet(evidence, output)
            text = output.read_text(encoding="utf-8")
            self.assertNotIn("supports", text.casefold())
            document = yaml.safe_load(text)
        self.assertEqual("openacr-authoring-worksheet-NOT-AN-OPENACR", document["document_type"])
        self.assertIn("Do not import", document["warning"])
        self.assertEqual(evidence["evidence_digest"], document["evidence_digest"])
        entries = [entry for rows in document["criterion_evidence"].values() for entry in rows]
        self.assertTrue(entries)
        for entry in entries:
            self.assertIsNone(entry["human_conformance_decision"])
            self.assertIsNone(entry["remarks_suggestion"])
            self.assertIn(entry["applicability"], {
                "confirmed-affected", "likely-affected", "confirmed-fixed",
                "not-introduced", "not-in-scope", "unknown",
            })

    def test_worksheet_missing_evidence_is_rejected(self):
        from acr_evidence.openacr import export_worksheet

        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(KeyError):
                export_worksheet({"assessment": {}, "findings": []}, Path(folder) / "x.yaml")


if __name__ == "__main__":
    unittest.main()
