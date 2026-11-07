# Architecture

```text
Drupal.org REST (discovery, tags)
        +
drupalorg-cli JSON (issue, comments, all MR states)
        ↓
normalize.py  →  normalized issue (public) + raw snapshot (private)
        ↓
collect.py    →  collection.json (schema 0.2.0)
        ↓
release.py    →  commit index + tag containment + applicability rules
        ↓
analysis.json →  report.py → static index.html, report.css, evidence.json
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
- `report.py` — fully static, no-JavaScript HTML report. All source text is
  escaped; internal links are checked by tests; the layout is usable at 320 CSS
  pixels.
- `model.py` — legacy assessment contract plus the schema-0.2 digest,
  observation, target and placeholder rules.
- `wcag.py` — small WCAG 2.2 criterion catalogue for labels and links only. It
  is not a conformance catalogue.
- `openacr.py` — preliminary YAML review worksheet. It remains **not** a
  schema-validated OpenACR.
- `ai.py` — optional Cloudflare helper, not called by any pipeline command. No
  AI is used in the current evidence report.

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

## Cross-project dependencies

Drupal Core, Drupal CMS and LocalGov Drupal are separate assessment targets.
Upstream evidence may be *candidate* evidence for downstream products, but
applicability must be re-established for the downstream installation. Do not
merge their conclusions.

## Privacy and deployment

The report is a preview artifact, not a publication authorization. The
`pages.yml` workflow publishes an explicit allowlist to GitHub Pages: a landing
page plus each report's `index.html`, `report.css`, `evidence.json` and
`summary.json`. Raw evidence and raw collection/analysis files are excluded, and
HTML with client-side scripts is rejected. Merging a PR that changes `reports/**`
is the publication review event; the `github-pages` environment can require an
additional reviewer. Private trackers require separate storage and a separate
publication workflow.

## Not implemented

- Official GSA OpenACR schema validation, editor round-trip and official HTML
  renderer reuse.
- Reproduction testing against an installed release.
- Automatic Composer lockfile resolution for Drupal CMS and LocalGov.
- AI provider abstraction and evaluation.
- GitHub Issues, Jira and non-Drupal GitLab adapters.
- Scheduled ingestion and publication.
