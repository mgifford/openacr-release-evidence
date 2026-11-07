# OpenACR Release Evidence (prototype)

A release-scoped, source-traceable accessibility evidence pipeline for Drupal Core,
Drupal CMS, and LocalGov Drupal. Other tracker ecosystems are explicitly deferred. **This does not
certify accessibility or automatically determine conformance.** It creates an
evidence bundle and optional *incomplete OpenACR authoring draft* for human review.

## Why it exists

Issue trackers typically describe a project's development branch, not a released
software installation. A fixed issue may still affect an older release; an issue
in a new feature may not affect that release at all. Downstream products share
Drupal Core code, but cannot inherit its conformance statements mechanically.

The primary object is an **assessment target**: product, release, exact package
versions and configuration, plus a declared scope. We preserve an issue's
source status separately from its applicability to the target release.

## Quick start (offline, from included fixtures)

Requires Python 3.10+. No runtime dependencies for evidence generation or the browser UI. Packaging needs setuptools.

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
acr-evidence build --manifest config/drupal-core-example.json \
  --issues tests/fixtures/issues.json --output site
python -m http.server 8000 --directory site
# Open http://localhost:8000
```

The generated site includes `index.html`, `app.js`, `style.css`, and `evidence.json`. The packaged site assets are maintained under `src/acr_evidence/static/`; `web/` is the readable source copy, and changes must be synchronized until a build-copy step is added.
All example findings are **synthetic**, not findings about Drupal Core.

To fetch specific publicly known issues rather than fixtures:

```sh
acr-evidence fetch-drupal --project drupal --ids 3631337,3619127 --output issues.json
acr-evidence build --manifest config/drupal-core-example.json \
  --issues issues.json --output site
```

The Drupal adapter respects a sequential request schedule and uses a descriptive
user agent. Retrieval can fail if the upstream API changes or throttles.
The preferred new path is the **Drupal-aware CLI bridge**, supporting classic
Drupal.org issues and projects migrated to GitLab work items:

```sh
# Install and verify mglaman/drupalorg-cli first (PHP 8.1+ required)
drupalorg list
drupalorg skill:get drupalorg-cli --full

acr-evidence collect-drupal --issue 3619127 \
  --output private-evidence/core-3619127.json
acr-evidence drupal-releases --project drupal \
  --output private-evidence/drupal-releases.json
```

These commands capture **raw, unreviewed, private evidence snapshots**. They do
not yet ingest the CLI output into the normalized site evidence model. The older
`fetch-drupal` command remains available for narrow API experiments but does
not handle the migration to GitLab. See [Drupal.org CLI integration](docs/DRUPALORG-CLI.md).

To make an **incomplete** OpenACR authoring draft, install the optional YAML
extra and run:

```sh
python -m pip install -e '.[yaml]'
acr-evidence export-draft --evidence site/evidence.json --output draft.yaml
```

The export is explicitly blocked from representing unknown WCAG outcomes as
`Supports`. It is **not a complete, schema-validated OpenACR**. In this initial
prototype, it is a YAML review worksheet, not an import-ready ACR for the GSA
editor. Full GSA catalog/schema integration and editor round-trip testing are
tracked as a subsequent milestone; do not describe this file as editor-compatible.

## Source editing convention

Static UI files are under `web/`, with a packaged copy under
`src/acr_evidence/static/`. Keep both in sync when editing. CI verifies that
they are byte-identical.

## What works now

- JSON assessment-target manifests and schema-free strict validation.
- A legacy Drupal.org REST issue adapter plus optional `drupalorg-cli` read-only snapshot collection for Drupal.org and GitLab work items.
- Source-independent normalized issue and evidence records.
- Version applicability overrides requiring cited evidence, plus optional local
  git commit-in-tag checks that **do not** imply successful remediation.
- Duplicate-safe issue identifiers and stable evidence hashes.
- Static GitHub Pages-compatible HTML interface, status filters and issue links.
- Explicit provenance, draft-only output, no conformance score or claims.
- Optional Cloudflare inference client for issue summaries, disabled by default.
- Unit/integration tests and a CI workflow; governance and agent instructions.

## Not implemented / intentionally excluded

- Automated final conformance decisions, release-specific proof from issue status,
  release inference from tags alone, signoff, and production release inventory.
- Complete Drupal.org search queries, historical comments/MR ingestion, automatic
  Composer lockfile resolution, backport equivalence detection, GitHub Issues and Jira adapters.
- Official OpenACR schema validation, complete standards catalogs and working
  GSA editor round-trip export. A worksheet is not a conformant OpenACR.
- Scheduled public publication, credentials in frontend, unapproved AI claims.

The initial site **cannot be used as an authoritative ACR**. See
[docs/ROADMAP.md](docs/ROADMAP.md) and [docs/CONFORMANCE-POLICY.md](docs/CONFORMANCE-POLICY.md).

## Key documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Drupal.org CLI and GitLab](docs/DRUPALORG-CLI.md)
- [Deferred sources](docs/FUTURE-SOURCES.md)
- [Evidence model](docs/EVIDENCE-MODEL.md)
- [Governance](GOVERNANCE.md)
- [Conformance policy](docs/CONFORMANCE-POLICY.md)
- [AI governance](docs/AI-GOVERNANCE.md)
- [Security policy](SECURITY.md)
- [Accessibility policy](ACCESSIBILITY.md)
- [Contributing](CONTRIBUTING.md)

## Authoritative external references

- [GSA OpenACR](https://github.com/GSA/openacr)
- [GSA ACR Editor](https://acreditor.section508.gov/)
- [Drupal.org REST APIs](https://www.drupal.org/drupalorg/docs/apis/rest-and-other-apis)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [Cloudflare Workers AI REST API](https://developers.cloudflare.com/api/resources/ai/methods/run/)

## Name and licence

Working repository name: `openacr-release-evidence`. The MIT licence is proposed
for this new starter code, not inherited from `python-acr` or GSA OpenACR.
Select a permanent project name and confirm licensing before public launch.
