import json
import tempfile
import unittest
from pathlib import Path

from acr_evidence.provenance_report import (
    apply_target,
    build_artifact,
    fetch_merge_request_changes,
    write_target_artifacts,
)


def collection():
    return {
        "evidence_digest": "collection-digest",
        "issues": [{
            "id": "drupal:123",
            "url": "https://www.drupal.org/project/drupal/issues/123",
            "title": "Default Admin focus ring",
            "component": "Admin theme",
            "merge_requests": [{"iid": 10, "state": "opened", "url": "https://git.drupalcode.org/project/drupal/-/merge_requests/10"}],
        }, {
            "id": "drupal:456",
            "url": "https://www.drupal.org/project/drupal/issues/456",
            "title": "No merge request",
            "component": "node system",
            "merge_requests": [],
        }],
    }


def fetcher(url):
    return {
        "iid": 10,
        "state": "opened",
        "title": "Focus",
        "web_url": "https://git.drupalcode.org/project/drupal/-/merge_requests/10",
        "changes": [
            {"old_path": "core/themes/default_admin/css/base/elements.css", "new_path": "core/themes/default_admin/css/base/elements.css"},
            {"old_path": "core/modules/node/node.module", "new_path": "core/modules/node/node.module"},
            {"old_path": "README.md", "new_path": "README.md"},
        ],
    }


class ProvenanceTests(unittest.TestCase):
    def test_changed_paths_create_verified_source_associations(self):
        artifact = build_artifact(collection(), fetcher=fetcher, cache_dir=tempfile.mkdtemp())
        issue = artifact["issues"][0]
        self.assertEqual(["core/modules/node/node.module", "core/themes/default_admin/css/base/elements.css"], issue["changed_paths"])
        self.assertEqual("verified-source-code", issue["level"])
        components = {(item["type"], item["component"]) for item in issue["associations"]}
        self.assertIn(("theme", "default_admin"), components)
        self.assertIn(("module", "node"), components)
        self.assertNotIn("README.md", issue["changed_paths"])
        self.assertEqual(1, artifact["summary"]["issues_with_changed_paths"])
        self.assertEqual(1, artifact["summary"]["merge_requests"])

    def test_no_merge_request_is_not_evidence(self):
        artifact = build_artifact(collection(), fetcher=fetcher, cache_dir=tempfile.mkdtemp())
        self.assertEqual(1, len(artifact["issues"]))
        self.assertNotIn("drupal:456", [item["issue_id"] for item in artifact["issues"]])

    def test_failed_mr_is_recorded_and_does_not_invent_paths(self):
        def failing(_url):
            raise TimeoutError("timeout")
        artifact = build_artifact(collection(), fetcher=failing, cache_dir=tempfile.mkdtemp())
        issue = artifact["issues"][0]
        self.assertEqual([], issue["changed_paths"])
        self.assertEqual("unknown", issue["level"])
        self.assertTrue(artifact["summary"]["errors"])

    def test_cache_reuses_public_metadata(self):
        calls = []

        def counting(url):
            calls.append(url)
            return fetcher(url)

        cache = tempfile.mkdtemp()
        first = fetch_merge_request_changes(10, cache_dir=cache, fetcher=counting)
        second = fetch_merge_request_changes(10, cache_dir=cache, fetcher=counting)
        self.assertEqual(1, len(calls))
        self.assertEqual(first["changed_paths"], second["changed_paths"])

    def test_target_marks_bundled_and_installed_presence(self):
        artifact = build_artifact(collection(), fetcher=fetcher, cache_dir=tempfile.mkdtemp())
        inventory = {"source": {"ref": "12.0.0-beta2"}, "components": [
            {"type": "theme", "machine_name": "default_admin", "installed_by_standard_profile": True},
        ]}
        target = apply_target(artifact, {"id": "drupal-core-12.0.0-beta2", "product": "Drupal Core", "release": "12.0.0-beta2", "ref": "12.0.0-beta2"}, inventory)
        associations = target["issues"][0]["associations"]
        theme = next(item for item in associations if item["component"] == "default_admin")
        node = next(item for item in associations if item["component"] == "node")
        self.assertTrue(theme["present_in_bundled_release"])
        self.assertTrue(theme["installed_by_standard_profile"])
        self.assertFalse(node["present_in_bundled_release"])

    def test_write_target_artifacts(self):
        artifact = build_artifact(collection(), fetcher=fetcher, cache_dir=tempfile.mkdtemp())
        with tempfile.TemporaryDirectory() as folder:
            inventory_dir = Path(folder) / "inventory"
            inventory_dir.mkdir()
            (inventory_dir / "drupal-core-12.0.0-beta2.json").write_text(json.dumps({"source": {"ref": "12.0.0-beta2"}, "components": []}))
            output = Path(folder) / "reports"
            targets = {"targets": [{"id": "drupal-core-12.0.0-beta2", "product": "Drupal Core", "ref": "12.0.0-beta2"}]}
            written = write_target_artifacts(artifact, targets, output, inventory_dir=inventory_dir)
            self.assertEqual(1, len(written))
            self.assertTrue(written[0].is_file())


if __name__ == "__main__":
    unittest.main()
