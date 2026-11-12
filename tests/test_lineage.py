import json
import tempfile
import unittest
from pathlib import Path

from acr_evidence.lineage import (
    ARTIFACT_TYPE,
    RELATION_TYPES,
    lineage_digest,
    load_lineage,
    relationships_for,
    validate_lineage,
)


def document(**overrides):
    record = {
        "id": "olivero-core-to-contrib",
        "relation": "moved-to-contrib",
        "source": {
            "project": "drupal",
            "component": "olivero",
            "type": "theme",
            "release_boundary": {"last_bundled": "11.4.12", "removed_in": "12.0.0-beta2"},
        },
        "destination": {
            "project": "olivero",
            "component": "olivero",
            "type": "theme",
            "release_boundary": {"first_release": "2.0.0"},
        },
        "evidence": [{
            "kind": "source-code",
            "url": "https://git.drupalcode.org/project/drupal/-/tree/12.0.0-beta2/core/themes",
            "observed_at": "2026-11-12T00:00:00Z",
            "note": "Theme directory absent at the beta2 tag.",
        }],
        "evidence_class": "verified-source-code",
        "verification": {"status": "unreviewed"},
        "limitations": ["Code continuity is a separate source comparison."],
    }
    record.update(overrides)
    return {
        "schema_version": "1.0.0",
        "artifact_type": ARTIFACT_TYPE,
        "records": [record],
    }


class LineageValidationTests(unittest.TestCase):
    def test_valid_record_round_trips(self):
        self.assertEqual(document(), validate_lineage(document()))

    def test_unknown_relation_rejected(self):
        with self.assertRaises(ValueError):
            validate_lineage(document(relation="fixed"))

    def test_missing_source_link_rejected(self):
        broken = document()
        broken["records"][0]["evidence"][0]["url"] = "http://example.invalid"
        with self.assertRaises(ValueError):
            validate_lineage(broken)

    def test_duplicate_id_rejected(self):
        duplicated = document()
        duplicated["records"].append(json.loads(json.dumps(duplicated["records"][0])))
        with self.assertRaises(ValueError):
            validate_lineage(duplicated)

    def test_evidence_is_required(self):
        with self.assertRaises(ValueError):
            validate_lineage(document(evidence=[]))

    def test_relation_vocabulary_covers_required_transitions(self):
        for relation in (
            "introduced-into-core", "moved-to-contrib", "adopted-from-contrib",
            "renamed", "deprecated", "removed", "replaced", "split-into",
            "merged-into", "derived-from", "shares-inherited-code",
        ):
            self.assertIn(relation, RELATION_TYPES)

    def test_load_and_query(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "lineage.json"
            path.write_text(json.dumps(document()), encoding="utf-8")
            loaded = load_lineage(path)
        self.assertEqual(1, len(relationships_for(loaded["records"], project="olivero")))
        self.assertEqual(1, len(relationships_for(loaded["records"], project="drupal", component="olivero")))
        self.assertEqual([], relationships_for(loaded["records"], project="gin"))

    def test_digest_is_stable_and_content_addressed(self):
        first = document()
        second = document()
        self.assertEqual(lineage_digest(first), lineage_digest(second))
        second["records"][0]["verification"]["status"] = "reviewed"
        self.assertNotEqual(lineage_digest(first), lineage_digest(second))


if __name__ == "__main__":
    unittest.main()
