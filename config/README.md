# Assessment manifests

- `drupal-core-11.4.12.json` — the real target used for the first evidence
  report. It records the 11.4.12 tag, composer.lock SHA-256, profile, enabled
  themes and the reproducible issue sample.
- `drupal-core-example.json` — synthetic fixture. It is marked
  `"synthetic": true`; its findings are not evidence about Drupal.
- `drupal-cms-template.json` and `localgov-template.json` — unresolved
  templates. They intentionally contain placeholder values and therefore fail
  `validate_manifest` until a real release, tag and installation are recorded.
  Do not copy them into a report without replacing every placeholder.
- WCAG criterion labels used by the report live in `src/acr_evidence/wcag.py`
  and link to the W3C WCAG 2.2 Recommendation.

A target must identify a real release. Placeholder sentinels are rejected unless
the manifest is explicitly synthetic.
