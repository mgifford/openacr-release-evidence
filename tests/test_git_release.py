import subprocess
import tempfile
import unittest
from pathlib import Path
from acr_evidence.git_release import commit_in_ref


class GitReleaseTests(unittest.TestCase):
    def test_commit_containment_only(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            def git(*args):
                return subprocess.run(['git', '-C', str(repo), *args], check=True,
                                      capture_output=True, text=True).stdout.strip()
            git('init', '-q')
            git('config', 'user.name', 'Fixture')
            git('config', 'user.email', 'fixture@example.org')
            (repo / 'file.txt').write_text('old')
            git('add', '.'); git('commit', '-qm', 'initial')
            old = git('rev-parse', 'HEAD')
            git('tag', 'release-1')
            (repo / 'file.txt').write_text('new')
            git('commit', '-qam', 'fix on main')
            new = git('rev-parse', 'HEAD')
            self.assertTrue(commit_in_ref(repo, old, 'release-1')['included'])
            self.assertFalse(commit_in_ref(repo, new, 'release-1')['included'])
            self.assertTrue(commit_in_ref(repo, new, 'HEAD')['included'])
            self.assertIn('not proof', commit_in_ref(repo, new, 'HEAD')['caution'])


if __name__ == '__main__':
    unittest.main()
