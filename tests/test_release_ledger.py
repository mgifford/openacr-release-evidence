import unittest

from acr_evidence.release_ledger import build_ledger, collect_closed_issues


class ReleaseLedgerTests(unittest.TestCase):
    def test_fix_in_12_only_is_not_in_11(self):
        node = {
            "nid": "123",
            "title": "Fix a focus bug",
            "field_issue_component": "navigation.module",
            "changed": "1700000000",
        }
        commit = {"sha": "abcdef1234567890", "title": "Issue #123", "web_url": "https://example.test/commit"}

        def annotate(commits, ref, **_kwargs):
            return [{**item, "in_target": ref == "12.0.0"} for item in commits]

        targets = [
            {"id": "core-10", "ref": "10.6.0", "ref_type": "tag", "release_line": "10.6.x"},
            {"id": "core-11", "ref": "11.4.0", "ref_type": "tag", "release_line": "11.4.x"},
            {"id": "core-12", "ref": "12.0.0", "ref_type": "tag", "release_line": "12.0.x"},
        ]
        ledger = build_ledger(
            [node], targets, {"by_issue": {"123": [commit]}},
            release_changes={"release_lines": {"12.0.x": {"removed": ["olivero"]}}},
            annotate=annotate,
        )
        issue = ledger["issues"][0]
        self.assertEqual("not-included", issue["targets"]["core-10"])
        self.assertEqual("not-included", issue["targets"]["core-11"])
        self.assertEqual("included", issue["targets"]["core-12"])
        self.assertEqual(["core-12"], issue["included_in"])
        self.assertEqual("included", issue["backport_state"])

    def test_removed_theme_is_scope_change_not_fix(self):
        node = {
            "nid": "124",
            "title": "Olivero focus bug",
            "field_issue_component": "Olivero",
            "changed": "1700000000",
        }
        targets = [
            {"id": "core-11", "ref": "11.4.0", "ref_type": "tag", "release_line": "11.4.x"},
            {"id": "core-12", "ref": "12.0.0", "ref_type": "tag", "release_line": "12.0.x"},
        ]
        ledger = build_ledger(
            [node], targets, {"by_issue": {}},
            release_changes={"release_lines": {"12.0.x": {"removed": ["olivero"]}}},
            annotate=lambda commits, ref, **kwargs: commits,
        )
        self.assertEqual("removed", ledger["issues"][0]["targets"]["core-12"])
        self.assertEqual("removed", ledger["issues"][0]["backport_state"])

    def test_collect_closed_issues_pages_and_filters(self):
        seen = []

        def find_issues(**kwargs):
            seen.append(kwargs["page"])
            if kwargs["page"] == 0:
                return [{"nid": str(number)} for number in range(1, 51)]
            if kwargs["page"] == 1:
                return [{"nid": "2"}, {"nid": "3"}]
            return []

        issues = collect_closed_issues(find_issues, "drupal", "3060", max_pages=5)
        self.assertIn("3", {str(item["nid"]) for item in issues})
        self.assertEqual([0, 1], seen)


if __name__ == "__main__":
    unittest.main()
