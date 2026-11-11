# Architecture

```text
Drupal.org REST (discovery, tags)
        +
drupalorg-cli JSON (issue, comments, all MR states)
        ↓
normalize.py  →  normalized issue (public) + raw snapshot (private)
        ↓
collect.py    →  shared collection.json (schema 0.2.0)
        ↓
release.py    →  per-target commit index + tag/branch containment
        ↓            (10.6.21, 11.4.12, 12 pre-releases, main)
atag.py       → ATAG 2.0 Part A/B evidence and WAI ATAG Report Tool draft
openacr_export.py → schema/catalog-valid OpenACR draft with no issue-tag-derived adherence values
acr.py       → ACR narrative (issue evidence summarized; criteria Not Evaluated until human review)
report.py     →  per-target report + landing page and cross-release matrix
        ↓
.github/workflows/pages.yml → GitHub Pages (allowlist)
.github/workflows/weekly.yml → weekly review-gated PR
```

## Modules

- `adapters/drupal.py` — read-only Drupal.org REST discovery, node detail,
  comments and taxonomy term resolution. Project IDs are explicit; it never
  guesses an ID from a machine name.
- `adapters/drupalorg_cli.py` — allowlisted read-only CLI bridge. It passes
  `--with-comments`, `--format=json` and `--state=all`; unknown flags are
  rejected. Raw CLI output is archived privately and is never published.
- `normalize.py` — stable normalized issue schema, verified status labels, WCAG
  tag parsing, comment/MR normalization, HTML-to-text conversion and content
  hashes. All upstream text remains untrusted.
- `collect.py` — discovery, per-issue collection, caching, failure isolation,
  raw snapshots, collection artifact and summary. One failed issue does not
  invalidate a run.
- `release.py` — Drupal Core tag resolution, paginated commit indexing,
  duplicate-commit merging, GitLab ref containment, and the documented
  applicability rules.
- `release.py` also supports a **branch target** (`main`, `12.0.x`): containment
  is checked against containing branches, the finding is labelled as a
  development result, and it never uses release language for a branch.
- `atag.py` — classifies ATAG-tagged issues by explicit tags, curated scope and
  explicit or human-curated Part A/B scope; renders the ATAG evidence page and WAI ATAG Report Tool
  JSON with all criteria `Not checked`.
- `acr.py` — turns active findings, WCAG tags and the OpenACR catalog into a
  human-readable ACR narrative. It never assigns an ACR result.
- `openacr_export.py` — builds a complete OpenACR draft from the pinned
  Civicactions/GSA schema and catalog, validates it with `jsonschema` and catalog
  checks, and writes `openacr.yaml` plus `openacr-validation.json`. It never
  fills adherence values; a human completes and revalidates the file.
- `report.py` — fully static, no-JavaScript HTML reports plus a landing page and
  cross-release matrix. All source text is escaped; internal links are checked by
  tests; target reports are usable at 320 CSS pixels. The matrix is a data table
  in a focusable scroll region.
- `model.py` — legacy assessment contract plus the schema-0.2 digest,
  observation, target and placeholder rules.
- `wcag.py` — small WCAG 2.2 criterion catalogue for labels and links only. It
  is not a conformance catalogue.
- `openacr.py` — preliminary YAML review worksheet. It remains **not** a
  schema-validated OpenACR.
- `ai.py` — optional Cloudflare helper, not called by any pipeline command. No
  AI is used in the current evidence report.

## Incremental issue cache

The weekly collector reuses the previous committed `reports/collection.json` as
an issue cache. Discovery stops at the previous changed high-water mark, and
unchanged issues are retained without another API/CLI fetch. Changed nodes are
refreshed; status-filtered nodes are removed. A manifest-digest mismatch forces a
full discovery. The cache is normalized public evidence, not raw CLI output.

## Data boundaries

- `private-evidence/` holds raw snapshots and is gitignored. Snapshots are
  created with mode `0600` and are never overwritten.
- `reports/drupal-core-11.4.12/` holds the public draft evidence report.
- `site/` is a local preview of the older explorer and is gitignored.
- `evidence.json` in a report contains normalized public data only: no raw CLI
  payloads, no secrets and no private tracker content.

## Release analysis

A release tag is resolved to an immutable commit. Commits are indexed from the
release branch and adjacent development branches. The same commit can appear on
several branches; it is deduplicated and its containing branches are recorded.
Containment in the tag is checked with the public GitLab refs API.

**Commit inclusion is not behavioural verification.** A contained fix is
classified `confirmed-fixed` only when the tracker is also closed fixed, and the
finding remains `unreviewed` with an explicit caveat. A fix found only on newer
branches is `likely-affected` for the older target. An open report after the
release date is `unknown` until reproduced.

## Supported release lines and targets

`config/drupal-core-targets.json` is the policy source: two supported lines,
pre-release tags and the development branch, each with its own manifest, ref,
branch set, support status and scope note. The shared issue collection is
analyzed once per target. The matrix shows an issue across every target so a
barrier does not disappear when a branch changes. Support status is declarative
policy, not a conformance statement.

`ref_type="tag"` uses tag containment; `ref_type="branch"` uses branch
containment and labels the result as development. Branches are explicit per
target so a 10.x analysis does not silently treat an 11.x fix as evidence.

## Parent ACR graph

`parent_project` is carried in the target metadata. The intended graph is Core
(top level) → Claro/Olivero (themes) and Core → Drupal CMS/LocalGov
(distributions), with each project publishing its own ACR and linking to the
matching parent release. This preserves responsibility without inheriting
upstream conformance judgments. The current release only collects Drupal Core;
contributed-project collection and parent-linked ACR export are future work.

## Scheduled snapshots

`weekly.yml` runs the tests, collects the active review-relevant collection, analyzes all targets and
opens a PR. It does not publish. A human merges the PR; `pages.yml` then deploys
the allowlisted reports. A failed issue in collection does not abort the rest of
the active collection.

## Cross-project dependencies

Drupal Core, Drupal CMS and LocalGov Drupal are separate assessment targets.
Upstream evidence may be *candidate* evidence for downstream products, but
applicability must be re-established for the downstream installation. Do not
merge their conclusions.

## Privacy and deployment

The report is a preview artifact, not a publication authorization. The
`pages.yml` workflow publishes an explicit allowlist to GitHub Pages: a landing
page plus `matrix.html` and each report's `index.html`, `report.css`, `evidence.json`,
`summary.json`, `acr.html`, `acr.md`, `openacr.yaml`, `openacr-validation.json`,
and the ATAG `atag-report.json`/`atag-evidence.json`. Raw evidence and
raw collection/analysis files are excluded, and
HTML with client-side scripts is rejected. Merging a PR that changes `reports/**`
is the publication review event; the `github-pages` environment can require an
additional reviewer. Private trackers require separate storage and a separate
publication workflow.

## Not implemented

- OpenACR editor round-trip and official HTML renderer reuse (schema/catalog
  validation and draft export are implemented).
- Reproduction testing against an installed release.
- Automatic Composer lockfile resolution for Drupal CMS and LocalGov.
- AI provider abstraction and evaluation.
- GitHub Issues, Jira and non-Drupal GitLab adapters.
- Parent-linked contributed-project ACRs and a full project graph.
- Automatic deployment of an unreviewed weekly snapshot; the weekly job opens a
  PR and a human merge publishes.
