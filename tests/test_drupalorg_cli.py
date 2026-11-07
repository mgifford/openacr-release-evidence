"""Tests for the optional Drupal.org/GitLab integration; no live network required."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from acr_evidence.adapters.drupalorg_cli import (
    collect_issue, collect_releases, run_read, save_private_snapshot,
    DrupalOrgCliError,
)


class DrupalCliTests(unittest.TestCase):
    def mock_runner(self, argv, **kwargs):
        self.calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, '<issue><title>Example</title></issue>', '')

    def setUp(self):
        self.calls = []

    def test_migrated_work_item_project_scoped(self):
        snapshot = collect_issue('ai_context#3586157', runner=self.mock_runner)
        self.assertEqual('unknown', snapshot['release_applicability'])
        self.assertEqual(2, len(snapshot['commands']))
        self.assertEqual(['drupalorg', 'issue:show', 'ai_context#3586157', '--format=llm'], self.calls[0])
        self.assertEqual('mr:list', snapshot['commands'][1]['command'])

    def test_legacy_nid(self):
        record = collect_issue('3619127', include_mrs=False, runner=self.mock_runner)
        self.assertEqual(1, len(record['commands']))

    def test_project_releases(self):
        result = collect_releases('drupal', runner=self.mock_runner)
        self.assertEqual('project:releases', result['command'])

    def test_reject_shell_argument_and_write_commands(self):
        with self.assertRaises(ValueError):
            collect_issue('123;rm -rf /', runner=self.mock_runner)
        with self.assertRaises(ValueError):
            run_read('issue:apply', ['123'], runner=self.mock_runner)
        with self.assertRaises(ValueError):
            run_read('issue:show', ['--danger'], runner=self.mock_runner)

    def test_raw_snapshot_never_overwritten_or_public(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'private-evidence' / 'a.json'
            save_private_snapshot(p, {'source':'fixture'})
            self.assertTrue(p.exists())
            with self.assertRaises(FileExistsError):
                save_private_snapshot(p, {})
            with self.assertRaises(ValueError):
                save_private_snapshot(Path(folder) / 'site' / 'raw.json', {})

    def test_failure_is_not_a_success(self):
        def fail(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 1, '', 'not available')
        with self.assertRaises(DrupalOrgCliError):
            collect_issue('123', runner=fail)


if __name__ == '__main__':
    unittest.main()
