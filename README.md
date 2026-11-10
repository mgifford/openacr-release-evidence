# OpenACR Release Evidence (prototype)

A release-scoped, source-traceable accessibility evidence pipeline for Drupal
Core, Drupal CMS and LocalGov Drupal. **This does not certify accessibility or
automatically determine conformance.** It collects public issue evidence,
classifies release-specific applicability, and produces a draft evidence report
and optional incomplete OpenACR authoring worksheet for human review.

The current multi-target snapshot is
[`reports/index.html`](reports/index.html), covering Drupal Core 10.6.21,
11.4.12, 12.0.0-alpha1, 12.0.0-beta2 and the `main` development branch. It is a
draft evidence collection with a cross-release applicability matrix, **not an
ACR**. The 11.4.12 report is at
[`reports/drupal-core-11.4.12/index.html`](reports/drupal-core-11.4.12/index.html).

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

Requires Python 3.10+; the core evidence/report path has no runtime dependencies.
Packaging needs setuptools. The OpenACR export extra adds `jsonschema` and PyYAML.

```sh
python3 -m pip install -e '.[openacr]'
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

## Reproduce the multi-target snapshot

Install `mglaman/drupalorg-cli` 0.15.0 (PHP 8.1+) in a temporary Composer home.
A shared issue collection is analyzed once per declared target:

```sh
export COMPOSER_HOME="$(mktemp -d)"
composer global require mglaman/drupalorg-cli --no-interaction
export ACR_DRUPALORG_BIN="$COMPOSER_HOME/vendor/bin/drupalorg"

acr-evidence collect \
  --manifest config/drupal-core-11.4.12.json \
  --output reports/collection.json

acr-evidence multi \
  --collection reports/collection.json \
  --targets config/drupal-core-targets.json \
  --output reports
```

The target policy is in
[`config/drupal-core-targets.json`](config/drupal-core-targets.json). Each target
has its own manifest, ref, support status, release line and branch set. The
shared collection is target-independent; the applicability analysis is not.

This writes:

- `reports/collection.json` — normalized active-issue collection (428 issues; 30 with full comments/MRs, 398 inventory-only, provenance). It also acts as the committed issue cache: the weekly run reuses unchanged issues and fetches only issues changed since the previous high-water mark.
- `reports/<target>/index.html` — static, no-JavaScript target report.
- `reports/<target>/evidence.json` — compact published evidence (findings and issue identity; comments/descriptions are not duplicated).
- `reports/<target>/summary.json`, `report.css`.
- `reports/<target>/acr.html`, `acr.md` — ACR narrative draft.
- `reports/<target>/openacr.yaml`, `openacr-validation.json` — validated OpenACR draft.
- `reports/index.html` — landing page with release finder and matrix preview.
- `reports/matrix.html` — complete cross-release applicability matrix.
- `reports/weekly/` — weekly ACR digest archive (created by the weekly workflow).
- `private-evidence/raw/` — raw upstream snapshots (gitignored, mode `0600`).

The report set is about **17 MB**, down from about 50 MB. The full per-target
`analysis.json` is no longer committed; the published `evidence.json` is compact,
and the detailed comments remain in the HTML report and the private collection.

The single-target pipeline remains available:

```sh
acr-evidence pipeline \
  --manifest config/drupal-core-11.4.12.json \
  --release 11.4.12 \
  --output reports/drupal-core-11.4.12
```

Collection is incremental: issue data is cached for six hours and commit
indexes are cached; use `--refresh` to force retrieval. A single failed issue is
recorded and does not invalidate the run.

## What the current collection shows

The same **428 active, review-relevant** Drupal Core accessibility issues are
analyzed against every declared target. Fixed and closed issues are excluded by
policy; RTBC issues stay in until closed. The collection covers statuses 1, 8,
13, 14 and 15; 30 review-priority issues have full comments/MRs, while 398 are
metadata-only inventory records.

| Target | Support | Fix included | Confirmed fixed | Likely affected | Unknown |
| --- | --- | ---: | ---: | ---: | ---: |
| 10.6.21 | Supported | 0 | 0 | 28 | 400 |
| 11.4.12 | Supported | 0 | 0 | 28 | 400 |
| 12.0.0-alpha1 | Pre-release | 0 | 0 | 23 | 405 |
| 12.0.0-beta2 | Pre-release | 0 | 0 | 26 | 402 |
| `main` / 12.0.x-dev | Development | 0 | 0 | 30 | 398 |

No active issue has a fix commit contained in a target. Closed-fixed issues are
not used as evidence, so there is no `confirmed-fixed` count in this active-only
pass. Most `unknown` results are metadata-only inventory records; the 30 detailed
issues carry commit/MR evidence (28 are likely affected and two have no target
conclusion). **This is not an accessibility score.** See the [matrix](reports/index.html) and the
per-target reports for source links and verification gaps.

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
- GitHub Pages deployment workflow with an explicit, script-free publication allowlist.
- Multi-target analysis for supported releases, pre-release tags and the `main` development branch.
- Weekly review-gated snapshot workflow that opens a PR instead of auto-publishing.
- A no-script release finder, compact release cards, grouped downloads and a separate complete matrix page.
- A report header with top supporting-output links, section navigation, at-a-glance evidence metrics, WCAG criterion index and 428-row issue index.
- Breadcrumb and section navigation from the ACR draft back to the release report.
- Validated per-report OpenACR draft export against the pinned Civicactions/GSA schema and WCAG 2.2 + Section 508 catalog.
- ATAG 2.0 authoring evidence: ATAG-tagged issues separated into explicit Part A/Part B and unassigned evidence, with a WAI ATAG Report Tool JSON draft.
- 129 offline tests; synthetic fixtures and trimmed real CLI fixtures.
- Optional incomplete YAML worksheet, with a test that it never emits
  `Supports`.

## Not implemented / intentionally excluded

- ACR Editor round-trip and reuse of the official OpenACR HTML renderer. The
  per-report YAML is schema/catalog-valid but has not been editor-tested.
- Full WAI ATAG Report Tool edit/export sign-off and release-scoped ATAG
  applicability. Import into the live tool was verified; the draft metadata
  loaded and all 52 A/AA criteria showed `Not checked`.
- Reproduction testing against an installed release; screen-reader, keyboard,
  zoom and forced-colors testing of the assessed release.
- Composer lockfile resolution for Drupal CMS and LocalGov, and their manifests.
- AI-assisted applicability or criterion mappings in the evidence report. No AI is
  used there; the optional weekly digest is separate and validated.
- Parent-linked contributed-project ACRs (Claro, Olivero, Drupal CMS, LocalGov
  Drupal); the parent field and design are present, but collection is not.
- GitHub Issues, Jira or non-Drupal GitLab adapters.
- Automatic publication of an unreviewed weekly snapshot. The weekly job opens
  a PR; a human merge is still required before Pages deploys.
- A single accessibility percentage or conformance score. None is produced.

## OpenACR draft export

Each target report exports `openacr.yaml` and `openacr-validation.json`. The YAML
is validated against the pinned Civicactions/GSA OpenACR 0.1.0 schema and the
OpenACR 2.5 WCAG 2.2 + Revised Section 508 catalog (commit `d6d18a9…`).

It is a **draft skeleton**, not an approved ACR:

- all 182 catalog criteria and all seven chapters are present;
- WCAG criteria carry the four Section 508 component names; issue-tagged criteria
  carry proposed `partially-supports` values for Web and Authoring Tool, while
  untagged criteria leave those components unset;
- the author is a placeholder (`reviewer@example.invalid`);
- notes link the evidence report and require human review;
- `not-evaluated` is never used for Level A/AA.

```sh
acr-evidence openacr-export \
  --analysis reports/drupal-core-11.4.12/evidence.json \
  --output reports/drupal-core-11.4.12
acr-evidence openacr-validate \
  --file reports/drupal-core-11.4.12/openacr.yaml --strict
```

All five target drafts were checked with the official `@civicactions/openacr`
0.3.11 CLI and returned `Valid!`. See
[`docs/OPENACR-EXPORT.md`](docs/OPENACR-EXPORT.md) for the review workflow,
validation rules and limitations. Editor round-trip testing is still pending.

## ACR narrative

Each target also exports a human-readable ACR narrative:

- `acr.html` — static, no-JavaScript narrative
- `acr.md` — editable Markdown source

The narrative follows the ACR/OpenACR shape: product information, four
Section 508 component scopes, term definitions, scope and method, executive
summary, WCAG 2.2 A/AA/AAA criterion tables, non-WCAG chapters, ATAG
separation, reviewer actions and limitations.

Web and Authoring Tool are shown as **proposed Partially Supports**; Electronic
Documents and Software as **proposed Not Applicable**. These are proposed labels
for review, not final terms. Criteria with active tagged issues use a draft
**Partially Supports** result based on the open issue queue; criteria without a
tagged issue remain **Not Evaluated**. Web and Authoring Tool remarks are
separate; issue statistics and examples sit at the bottom of each remarks cell,
with direct Drupal.org links and a per-criterion reference list in the footer.
The narrative uses the same active-issue scope (428 issues; 30 detailed, 398
inventory-only) and links back to the evidence report.

An optional `criterion-summaries` step can add model-assisted Web/Authoring
barrier paragraphs, cached by issue-content hash. Without a configured model it
falls back to deterministic issue-title summaries.

The generated reports explicitly contrast this issue-queue attestation with a
periodic, sample-based vendor ACR. See [`docs/ACR-POSITION.md`](docs/ACR-POSITION.md).

See [`docs/ACR-NARRATIVE.md`](docs/ACR-NARRATIVE.md), the reusable
[`templates/drupal-acr-template.md`](templates/drupal-acr-template.md), and the
human-maintained [`context/DRUPAL.md`](context/DRUPAL.md) scope notes.

## Weekly ACR digest (optional Hugging Face)

The weekly workflow can also produce a deterministic digest of what changed and
an optional short executive summary from a pinned Hugging Face model.

- `reports/weekly/YYYY-MM-DD.facts.json` — counts, status changes, new and
  no-longer-active issues, RTBC changes, criterion changes, target and ATAG
  changes.
- `reports/weekly/YYYY-MM-DD.md` — digest with optional AI executive summary.
- `reports/weekly/YYYY-MM-DD.provenance.json` — provider, model, revision,
  prompt version, input/output hashes and status.
- `reports/weekly/index.md` — trend table across weeks.

The facts are deterministic. The model receives only issues with new activity
(plus new/no-longer-active and aggregate context), writes only the executive
summary, and is skipped when nothing changed. Output is validated against the
facts and falls back to the deterministic digest if rejected or the provider
fails. The digest is not an ACR result.

Setup: add `HF_TOKEN` as a repository Actions secret and `HF_MODEL`,
`HF_PROVIDER`, optional `HF_ENDPOINT`/`HF_MODEL_REVISION` as repository Actions
variables. Install `.[openacr,summaries]` for the Hugging Face client. See
[`docs/HF-WEEKLY-SUMMARY.md`](docs/HF-WEEKLY-SUMMARY.md).

## ATAG 2.0 authoring evidence

Drupal Core is an authoring tool as well as a CMS. ATAG 2.0 evidence is kept
separate from the WCAG release matrix and the OpenACR draft:

- [`reports/drupal-core-atag/`](reports/drupal-core-atag/) — static evidence report
- `atag-report.json` — WAI ATAG Report Tool JSON draft with all 63 criteria
  **Not checked**
- `atag-evidence.json` — issue/Part A/Part B classification

The ATAG tag is Drupal taxonomy term `5050`; the common Accessibility tag is
`1101`. Part A/B tags (`atag-a`, `atag-b`, `atag-part-a`, `atag-part-b`) override
the component triage hints. Issues without a part are shown as
`ATAG-tagged, part not specified`.

```sh
acr-evidence atag-report \
  --collection reports/drupal-core-atag/collection.json \
  --output reports/drupal-core-atag
```

See [`docs/ATAG-EVIDENCE.md`](docs/ATAG-EVIDENCE.md). ATAG and WCAG are separate
standards; neither inherits the other’s conclusions, and no ATAG conformance
values are generated.

## Weekly snapshots

`.github/workflows/weekly.yml` runs on Mondays at 13:00 UTC and on manual
dispatch. It:

1. installs the package and `drupalorg-cli`;
2. runs the offline test suite;
3. pages the full Accessibility queue and collects active review-relevant issues;
4. analyzes all five declared targets;
5. opens a pull request on a generated branch.

It does **not** publish automatically. The PR must be reviewed and merged; the
Pages workflow then deploys the reviewed reports. If nothing changed, no PR is
opened. This is a weekly **review-gated snapshot**, not an auto-published
weekly site.

## Parent ACRs and project responsibility

Drupal Core is the top-level product in this snapshot. Claro and Olivero are
core themes in 10.x/11.x but contributed projects in 12.x; Drupal CMS and
LocalGov Drupal combine Core with their own modules, themes and recipes. The
model already carries a `parent_project` field and displays it. The intended
graph is:

```text
Drupal Core ACR (parent)
  ├── Claro ACR (theme, parent = drupal)
  ├── Olivero ACR (theme, parent = drupal)
  ├── Drupal CMS ACR (distribution, parent = drupal)
  └── LocalGov Drupal ACR (distribution, parent = drupal)
```

Responsibility for a barrier can then be attached to the closest project while
the Core ACR remains the parent evidence source. **Upstream conclusions are not
inherited automatically.** The current pipeline does not yet collect
contributed-project queues or generate parent-linked ACRs; that is the next
product-scope increment.

## GitHub Pages

The reviewed static reports are published from the `main` branch with
`.github/workflows/pages.yml`. The expected site URL is
<https://mgifford.github.io/openacr-release-evidence/>.

- The workflow runs on `workflow_dispatch` and on a push to `main` that changes
  `reports/**` or the workflow itself.
- It deploys only an explicit allowlist: the landing page plus each report's
  `index.html`, `report.css`, `evidence.json`, `summary.json`, `acr.html`,
  `acr.md`, OpenACR files and ATAG evidence files.
- Raw evidence, `collection.json`, `analysis.json`, repository files and
  unpublished drafts are excluded and checked before upload. The published
  `evidence.json` is compact normalized public evidence; `provenance.raw_ref` is
  a path reference only, not raw content.
- It refuses to publish an HTML report containing a client-side `<script>`.
- Merging a PR that changes `reports/**` is the publication review event.
  Configure required reviewers on the `github-pages` environment for a second
  approval gate; `workflow_dispatch` is available for a deliberate manual run.
- Enable Pages under **Settings → Pages → Build and deployment → GitHub
  Actions** if it is not already enabled. Until the workflow runs, the site URL
  returns 404.

The landing page is `reports/index.html` and contains the cross-release matrix.
Reports are at `/drupal-core-10.6.21/`, `/drupal-core-11.4.12/`,
`/drupal-core-12.0.0-alpha1/`, `/drupal-core-12.0.0-beta2/` and
`/drupal-core-main/`. Reports remain drafts, not conformance claims.

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
- [OpenACR export](docs/OPENACR-EXPORT.md)
- [Hugging Face weekly summary](docs/HF-WEEKLY-SUMMARY.md)
- [ACR narrative](docs/ACR-NARRATIVE.md)
- [Drupal ACR template](templates/drupal-acr-template.md)
- [Why this ACR is different](docs/ACR-POSITION.md)
- [Surface policy for Web vs Authoring Tool](docs/SURFACE-POLICY.md)
- [Onboarding Drupal CMS and LocalGov Drupal](docs/MULTI-PROJECT-ONBOARDING.md)
- [Drupal ecosystem AI/ACR context](context/README.md)
- [Drupal Core context notes](DRUPAL.md)
- [ATAG 2.0 authoring evidence](docs/ATAG-EVIDENCE.md)
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
