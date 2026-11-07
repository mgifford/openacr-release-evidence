# Architecture

`adapter -> normalized issue -> assessment target -> applicability evidence -> public evidence JSON -> static UI`.

- `config/*.json` specifies target scope; the example is intentionally incomplete.
- `adapters/` contains the legacy Drupal.org API reader and a read-only `drupalorg-cli` bridge that archives classic issues and GitLab work-item/MR output. Normalization of CLI output is not yet implemented.
- `model.py` validates minimal contracts, normalizes issues and assesses known
  applicability overrides; all unproven relations stay unknown.
- `git_release.py` can check whether a commit is reachable from a tag in an
  explicitly provided local checkout. This alone is NOT verification of a fix.
- `build.py` emits the static site and `evidence.json`.
- `ai.py` is an optional Cloudflare helper for **unreviewed** wording. It is not
  invoked by `build` and cannot change applicability or conformance.
- `openacr.py` emits a preliminary YAML *worksheet* with no completed SC claims.

A future `standards/` catalog loader and validation adapter must use the pinned
version of the GSA OpenACR format and prove compatibility with its editor.
An ACR release must separately preserve the referenced evidence snapshot.

## Cross-project dependencies

Drupal Core, Drupal CMS and LocalGov Drupal are separate assessment targets.
A future package graph resolver will use Composer lockfiles and enabled feature
manifests. Upstream evidence may be *candidate* evidence for downstream projects,
but must be scoped and reverified. Do not merge their ACR conclusions.

## Privacy and deployment

The `site/` directory is a preview artifact, not a publication authorization.
Only deliberately approved public evidence should be deployed to Pages. Private
trackers require a separate non-public storage and publication workflow.

Site assets in `src/acr_evidence/static/` are packaged copies of `web/`. Update both until a build-sync step replaces duplication.

## Drupal-first scope

See [DRUPALORG-CLI.md](DRUPALORG-CLI.md) for integration details and [FUTURE-SOURCES.md](FUTURE-SOURCES.md) for explicitly deferred Jira and GitHub Issues adapters. GitHub Actions is a delivery environment, not a source of Drupal Core issues.
