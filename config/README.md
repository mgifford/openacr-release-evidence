# Assessment manifests and target policy

- `drupal-core-11.4.12.json` — supported 11.4.x target used for the shared
  collection. It records the 11.4.12 tag, composer.lock SHA-256, profile, enabled
  themes and the reproducible issue sample.
- `drupal-core-10.6.21.json` — supported 10.6.x target (Claro admin theme).
- `drupal-core-12.0.0-alpha1.json` — pre-release 12.0.x target (Claro admin
  theme; Default Admin present but not default).
- `drupal-core-12.0.0-beta2.json` — pre-release 12.0.x target (Default Admin;
  Claro/Olivero no longer core themes).
- `drupal-core-main.json` — `main`/12.0.x development target (not a release).
- `drupal-core-targets.json` — the target policy: support status, release line,
  ref type, branch set, parent project and scope notes. `acr-evidence multi`
  consumes this file.
- `drupal-core-example.json` — synthetic fixture, marked `"synthetic": true`.
- `drupal-cms-template.json` and `localgov-template.json` — unresolved
  templates. They intentionally contain placeholder values and therefore fail
  `validate_manifest` until a real release, tag and installation are recorded.

A target must identify a real release or an explicitly declared branch. Placeholder
sentinels are rejected unless the manifest is explicitly synthetic.

WCAG criterion labels used by the report live in `src/acr_evidence/wcag.py` and
link to the W3C WCAG 2.2 Recommendation.
