# OpenACR Release Evidence (prototype)

A release-scoped, source-traceable accessibility evidence pipeline for Drupal
Core, Drupal CMS and LocalGov Drupal. **This does not certify accessibility or
automatically determine conformance.** It collects public issue evidence,
classifies release-specific applicability, and produces a draft evidence report
and optional incomplete OpenACR authoring worksheet for human review.

The first real draft report is
[`reports/drupal-core-11.4.12/index.html`](reports/drupal-core-11.4.12/index.html),
based on 15 real Drupal Core accessibility issues and the 11.4.12 tag. It is a
draft evidence report, **not an ACR**.

## Why it exists

Issue trackers usually describe a development branch, not an installed release.
A closed issue may still affect an older release; a fix on `main` may not be in a
supported version; a commit in a tag proves code inclusion, not a corrected
barrier. Downstream products share Drupal Core code but cannot inherit its
conformance statements mechanically.

The primary object is an **assessment target**: product, release, exact tag,
Drupal Core version, install profile, enabled modules/themes and declared scope.
Tracker status and release applicability are stored separately.

## Quick start (offline)

Requires Python 3.10+; no runtime dependencies for evidence collection or the
report. Packaging needs setuptools; the optional worksheet needs PyYAML.

```sh
python3 -m pip install -e '.[yaml]'
python3 -m unittest discover -s tests -v
python3 -m compileall -q src
```

On a machine without an installed package, either install it as above or set
`PYTHONPATH=src`. The `AGENTS.md` check block includes the install step.

Build the synthetic explorer from fixtures:

```sh
acr-evidence build --manifest config/drupal-core-example.json \
  --issues tests/fixtures/issues.json --output site
python3 -m http.server 8000 --directory site
```

All example findings are **synthetic** and the manifest is marked
`"synthetic": true`.

## Reproduce the real Drupal Core 11.4.12 report

Install `mglaman/drupalorg-cli` 0.15.0 (PHP 8.1+) in a temporary Composer home,
then run the pipeline. The manifest carries the sample IDs and collection
settings, so no long inline ID list is required:

```sh
export COMPOSER_HOME="$(mktemp -d)"
composer global require mglaman/drupalorg-cli --no-interaction
export ACR_DRUPALORG_BIN="$COMPOSER_HOME/vendor/bin/drupalorg"

acr-evidence pipeline \
  --manifest config/drupal-core-11.4.12.json \
  --release 11.4.12 \
  --output reports/drupal-core-11.4.12
```

This writes:

- `collection.json` — normalized issues, comments, all MR states, provenance.
- `analysis.json` — release applicability findings and commit/tag evidence.
- `index.html` — static, no-JavaScript accessible report.
- `evidence.json`, `summary.json`, `report.css`.
- `private-evidence/raw/` — raw upstream snapshots (gitignored, mode `0600`).

The pipeline is incremental: issue data is cached for six hours and commit
indexes are cached; use `--refresh` to force retrieval. A single failed issue is
recorded and does not invalidate the run.

### Individual steps

```sh
acr-evidence collect --manifest config/drupal-core-11.4.12.json \
  --output reports/drupal-core-11.4.12/collection.json
acr-evidence analyze --collection reports/drupal-core-11.4.12/collection.json \
  --manifest config/drupal-core-11.4.12.json --release 11.4.12 \
  --output reports/drupal-core-11.4.12/analysis.json
acr-evidence report --analysis reports/drupal-core-11.4.12/analysis.json \
  --output reports/drupal-core-11.4.12
```

## What the current sample shows

Against Drupal Core **11.4.12** (tag commit `aa556ff1…`, composer.lock
`d3d2949e…`), with the Default Admin theme enabled as a declared configuration:

| Applicability | Findings |
| --- | --- |
| `confirmed-fixed` — fix commit contained in the tag, not behaviourally verified | 4 |
| `likely-affected` — report evidence, not reproduced | 9 |
| `unknown` — insufficient target-specific evidence | 2 |

The four contained fixes are issues 3621109, 3623388, 3618127 and 3617875. The
two unknown findings were reported after the release and have no target-branch
fix. **This is not an accessibility score.** See the report for the per-issue
reasoning, source links, comments and verification gaps.

## Applicability states

- `confirmed-affected` — reproduction on the target release (not emitted by the
  automated pipeline in this phase).
- `likely-affected` — report evidence; not reproduced.
- `confirmed-fixed` — fix commit in the tag and tracker closed fixed; still
  unreviewed and not behaviourally verified.
- `not-introduced` — affected feature/code absent from the release.
- `not-in-scope` — component outside the declared scope.
- `unknown` — insufficient evidence; the safe default.

Commit inclusion is **not** a behavioural fix. A closed issue is **not** a fix in
the release. No issues found is **not** evidence of support. See
[`docs/EVIDENCE-MODEL.md`](docs/EVIDENCE-MODEL.md) and
[`docs/CONFORMANCE-POLICY.md`](docs/CONFORMANCE-POLICY.md).

## Sources and verified CLI

Discovery uses the public Drupal.org REST API filtered by project and the
**Accessibility** taxonomy term. Per-issue detail and MRs use
`drupalorg-cli` 0.15.0 JSON:

- `issue:show <nid> --format=json --with-comments`
- `mr:list <nid> --state=all --format=json`

Important: `mr:list` defaults to **opened** MRs, so `--state=all` is required.
Drupal status **7** is “Closed (fixed)”; **8** is “Needs review”. The verified
map is in [`docs/DRUPALORG-CLI.md`](docs/DRUPALORG-CLI.md).

Release containment uses the public GitLab refs API. No mutating Drupal CLI
command is called. Raw output is private and never published.

## What works now

- Read-only Drupal Core accessibility issue collection, with comments and all
  MR states.
- Normalized, versioned evidence with retrieval time, content hash, source URL,
  target and observation time.
- Incremental cache, failure isolation, raw private snapshots and collection
  summaries.
- Release tag resolution, deduplicated commit indexing, tag containment and
  documented applicability rules.
- A static, accessible, no-JavaScript report with source links, WCAG candidate
  grouping and explicit verification gaps.
- Reproducible artifacts with a digest that can be recomputed from the published
  JSON, plus an input-manifest digest.
- 59 offline tests; synthetic fixtures and trimmed real CLI fixtures.
- Optional incomplete YAML worksheet, with a test that it never emits
  `Supports`.

## Not implemented / intentionally excluded

- Official GSA OpenACR schema validation, ACR Editor round-trip and reuse of the
  official HTML renderer. The worksheet is not an import-ready ACR.
- Reproduction testing against an installed release; screen-reader, keyboard,
  zoom and forced-colors testing of the assessed release.
- Composer lockfile resolution for Drupal CMS and LocalGov, and their manifests.
- AI-assisted summaries or mappings. No AI is used in the current report.
- GitHub Issues, Jira or non-Drupal GitLab adapters.
- Automated publication to GitHub Pages. Publication remains a human decision.
- A single accessibility percentage or conformance score. None is produced.

## Repository layout

```text
config/                     assessment manifests and WCAG label catalogue
docs/                       architecture, evidence model, policy, CLI, ADRs
private-evidence/           raw snapshots (gitignored, never published)
reports/drupal-core-11.4.12 first real draft evidence report
src/acr_evidence/           pipeline, adapters, static assets
tests/                      offline tests and trimmed real fixtures
web/                        source copy of the older explorer
```

## Accessibility of this project

The static report is designed to WCAG 2.2 AA intent: semantic headings, native
details/links, visible focus, no color-only status, no JavaScript requirement,
320 px reflow, and text alternatives for statuses. Automated checks (axe-core)
and keyboard/reflow/no-JS checks were run; manual screen-reader testing is not
yet recorded. See [`ACCESSIBILITY.md`](ACCESSIBILITY.md) and
[`AUDIT.md`](AUDIT.md).

## Documentation

- [Audit](AUDIT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Drupal.org CLI and GitLab](docs/DRUPALORG-CLI.md)
- [Evidence model](docs/EVIDENCE-MODEL.md)
- [Conformance policy](docs/CONFORMANCE-POLICY.md)
- [AI governance](docs/AI-GOVERNANCE.md)
- [Governance](GOVERNANCE.md)
- [Security](SECURITY.md)
- [Accessibility](ACCESSIBILITY.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](docs/ROADMAP.md)
- [Deferred sources](docs/FUTURE-SOURCES.md)
- [Third-party content notice](NOTICE)

## Authoritative references

- [GSA OpenACR](https://github.com/GSA/openacr)
- [GSA ACR Editor](https://acreditor.section508.gov/)
- [Drupal.org REST APIs](https://www.drupal.org/drupalorg/docs/apis/rest-and-other-apis)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [mglaman/drupalorg-cli](https://github.com/mglaman/drupalorg-cli)

## Name and licence

Working repository name: `openacr-release-evidence`. MIT licence for this
starter code, not inherited from `python-acr` or GSA OpenACR. The permanent
project name and stewardship still need confirmation.
