import json
import tempfile
import unittest
from pathlib import Path
from acr_evidence.model import assess, normalize_issue, validate_manifest
from acr_evidence.build import build

ROOT = Path(__file__).resolve().parents[1]


def sample():
    return (json.loads((ROOT / 'config/drupal-core-example.json').read_text()),
            json.loads((ROOT / 'tests/fixtures/issues.json').read_text()))


class EvidenceTests(unittest.TestCase):
    def test_closed_issue_is_not_assumed_fixed_in_release(self):
        manifest, issues = sample()
        result = assess(manifest, issues, generated_at='2026-11-07T00:00:00Z')
        issue = next(x for x in result['findings'] if x['issue_id'] == 'fixture:1001')
        self.assertEqual('closed', issue['tracker_status'])
        self.assertEqual('unknown', issue['applicability'])
        self.assertEqual('none', issue['basis'])

    def test_override_is_explicit_and_not_independently_verified(self):
        manifest, issues = sample()
        result = assess(manifest, issues)
        issue = next(x for x in result['findings'] if x['issue_id'] == 'fixture:1002')
        self.assertEqual('confirmed-affected', issue['applicability'])
        self.assertEqual('evidence-supplied-not-independently-verified', issue['review_status'])

    def test_unknown_future_feature(self):
        manifest, issues = sample()
        result = assess(manifest, issues)
        issue = next(x for x in result['findings'] if x['issue_id'] == 'fixture:1003')
        self.assertEqual('unknown', issue['applicability'])

    def test_no_support_claims(self):
        manifest, issues = sample()
        result = assess(manifest, issues)
        self.assertEqual('release-accessibility-evidence-draft', result['artifact_type'])
        self.assertFalse(any('supports' in json.dumps(x) for x in result['findings']))

    def test_deterministic_digest_and_order(self):
        manifest, issues = sample()
        a = assess(manifest, issues, generated_at='2026-11-07T00:00:00Z')
        b = assess(manifest, list(reversed(issues)), generated_at='2026-11-07T00:00:00Z')
        self.assertEqual(a['evidence_digest'], b['evidence_digest'])

    def test_reject_bad_override_without_evidence(self):
        manifest, issues = sample()
        manifest['applicability_overrides']['fixture:1002']['evidence_urls'] = []
        with self.assertRaises(ValueError):
            assess(manifest, issues)

    def test_reject_insecure_evidence_link(self):
        manifest, issues = sample()
        manifest['applicability_overrides']['fixture:1002']['evidence_urls'] = ['javascript:alert(1)']
        with self.assertRaises(ValueError):
            assess(manifest, issues)

    def test_duplicate_issues_rejected(self):
        manifest, issues = sample()
        with self.assertRaises(ValueError):
            assess(manifest, issues + issues)

    def test_packaged_static_assets_match_sources(self):
        for name in ("index.html", "app.js", "style.css"):
            self.assertEqual((ROOT / "web" / name).read_bytes(),
                             (ROOT / "src/acr_evidence/static" / name).read_bytes())

    def test_static_site_and_provenance(self):
        manifest, issues = sample()
        with tempfile.TemporaryDirectory() as folder:
            result = build(manifest, issues, folder)
            self.assertEqual(4, len(result['findings']))
            for file in ('index.html', 'app.js', 'style.css', 'evidence.json'):
                self.assertTrue((Path(folder) / file).exists())
            self.assertIn("fetch('./evidence.json'", (Path(folder) / 'app.js').read_text())
            self.assertNotIn('innerHTML', (Path(folder) / 'app.js').read_text())
            self.assertIn('<script>alert(1)</script>', (Path(folder) / 'evidence.json').read_text())
            self.assertIn('textContent', (Path(folder) / 'app.js').read_text())


if __name__ == '__main__':
    unittest.main()
