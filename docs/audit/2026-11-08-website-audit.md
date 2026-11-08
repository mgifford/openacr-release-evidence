# Website audit — OpenACR Release Evidence

Date: 2026-11-08
Scope: generated static site, homepage, one full release report, and its ACR
draft. This is an audit of the reporting interface, not the assessed Drupal
release.

## Existing pages and outputs

The Pages workflow publishes an explicit allowlist:

- `reports/index.html` — homepage and cross-release matrix;
- five `reports/drupal-core-*/index.html` release reports;
- per-target `report.css`, `evidence.json`, `summary.json`, `openacr.yaml`,
  `openacr-validation.json`, `acr.html`, `acr.md`;
- `reports/drupal-core-atag/` ATAG report and JSON exports.

The homepage currently contains the introduction, draft notice, snapshot
metadata, five target cards, ATAG evidence, the complete 428-row
cross-release matrix, parent-ACR responsibility, publication allowlist and
limitations. Each target report contains assessment scope, evidence summary,
WCAG criterion sections, every issue record, verification gaps, method and
limitations, provenance and downloads, plus the ACR draft.

Current snapshot: **5 targets, 428 active issues, 30 full-evidence records and
398 metadata-only inventory records**. The homepage is about 240 KB and the
12.0.0-alpha1 release report about 784 KB; both are server-generated and require
no JavaScript.

Before screenshots: [`screenshots/before/`](screenshots/before/).

## Strengths to preserve

- Every finding remains reachable, with a source issue link and stable anchor.
- Full and metadata-only evidence are explicitly distinguished.
- Release applicability, tracker status, commits and merge requests are separate
  concepts and are not collapsed into a score.
- The matrix is a real data table with a caption and a focusable scroll region.
- The report and ACR are usable without JavaScript and at 320 CSS px.
- ATAG evidence is kept separate from WCAG/OpenACR.
- Provenance and machine-readable downloads are present.
- The ACR remains a draft and every criterion remains `Not Evaluated`.

## Gaps against the requested experience

### Homepage

- No release finder or release-line/status filter; readers scan five large cards.
- Artifact links sit in the same line as the report summary and compete with the
  primary report action.
- Snapshot metadata is a single sentence, not a scannable summary.
- The complete 428-row matrix dominates the page before method and limitations.
- There is no compact matrix preview or explicit route to the full matrix.
- Release cards do not consistently expose status, line and evidence
  completeness as scannable facts.

### Release report

- The report header does not put the primary downloads (evidence, summary,
  OpenACR, validation, ACR) near the top.
- Section navigation is a flat link list with no section index beyond seven
  links.
- Assessment scope is one long definition list; key identifiers are not
  separated from technical metadata.
- The evidence summary has tables but no at-a-glance metrics with definitions.
- The WCAG section has no criterion index table before the long criterion list.
- The issue section has no compact issue index before 428 full articles.
- There is no breadcrumb back to all releases.
- Verification gaps and provenance are preserved but visually under-signposted.

### ACR draft

- No breadcrumb back to the release report.
- No section navigation.
- The product/version context is in the title but not in a persistent top bar.

## Constraint: no client-side scripts

The Pages workflow rejects any published `<script>`. The existing site is
therefore intentionally no-JavaScript. The release finder will use:

- a static release index with direct anchors;
- CSS-only radio filters for support status and release line;
- a visible note that exact-version search can use the browser's Find command.

All releases remain present and visible if a browser does not support `:has()`.
No filtering is required to reach a report.

## Planned first two improvements

1. **Homepage**: snapshot metadata, release index and no-JS status/line filters,
   clearer release cards with grouped downloads, compact matrix preview with a
   full-matrix disclosure, and preserved ATAG/limitations.
2. **Release report**: breadcrumb, report header utility links, section nav,
   at-a-glance facts, evidence metrics, criterion index, issue index, and
   preserved full issue/criterion content. Add ACR back-link and section nav.

## Preservation checks

Before and after, verify:

- 5 target reports and all target links;
- 428 unique issue IDs and their report anchors;
- 428 matrix rows;
- 30 full and 398 inventory records;
- 29 issues with merge requests;
- all `evidence.json`, `summary.json`, `openacr.yaml`,
  `openacr-validation.json`, `acr.html`, `acr.md` links;
- ATAG report and JSON links;
- every WCAG criterion section and criterion anchor;
- the ACR `Not Evaluated` state and component proposals.

## Out of scope for this change

- Issue search/filtering that requires JavaScript (deferred until the
  publication policy is explicitly changed).
- Canonical cross-release issue records and a separate issue database.
- New issue-tracker adapters, GitHub/Jira integration, or multi-project
  manifest work beyond the existing target structure.
- Any manual ACR editing/approval interface.

## Implemented in this pass

### Homepage

- Added a concise introduction and a prominence-preserving draft/evidence banner.
- Added a compact snapshot metadata grid: generated date, targets, unique active
  issues, full evidence, metadata-only records, merge requests, source and
  standards.
- Added a release finder:
  - a release index with direct anchors;
  - CSS-only support-status filters (All, Supported release line, Pre-release,
    Development branch);
  - CSS-only release-line filters generated from the target metadata;
  - a no-script note pointing to the browser Find command for exact versions.
- Reworked release cards with status/type/line badges, exact version, snapshot,
  likely/unknown applicability, full/inventory counts, merge-request count, a
  primary **Open evidence report** action and grouped downloads.
- Replaced the 428-row homepage matrix with a 12-row preview and a separate
  `matrix.html` page containing the complete table. The full table remains a
  captioned, focusable data table with a link from every cell to the target
  finding.
- Preserved the ATAG section, parent-ACR responsibility, publication allowlist,
  limitations and all release links.

### Release report

- Added a breadcrumb back to all releases.
- Replaced the draft suffix in the H1 with explicit Draft/status badges.
- Added a supporting-outputs bar near the top: evidence JSON, summary JSON,
  OpenACR YAML, validation and ACR draft.
- Added a section navigation band.
- Split assessment scope into key facts and complete metadata; all original rows
  remain.
- Added at-a-glance metrics with definitions: active findings, full evidence,
  metadata-only, likely affected, unknown and needing verification.
- Added a WCAG criterion index table before the full criterion sections, with a
  Perceivable/Operable/Understandable/Robust principle column.
- Added a 428-row issue index before the canonical issue records, with issue
  link, title, component, criteria, tracker status, applicability, evidence
  detail and merge-request count.
- Preserved every full issue record, comments/MR details, method, limitations,
  verification gaps and provenance.
- Added a verification-gap count summary and a direct route to the issue index.

### ACR draft

- Added a three-level breadcrumb back to the release report.
- Added a section navigation list with stable heading IDs.
- Preserved the draft banner, every `Not Evaluated` criterion and the component
  proposals.

## After screenshots

- [Homepage desktop](screenshots/after/home-desktop.png)
- [Homepage mobile](screenshots/after/home-mobile.png)
- [Release cards](screenshots/after/home-releases-desktop.png)
- [Release report top](screenshots/after/report-top-desktop.png)
- [Release report mobile](screenshots/after/report-top-mobile.png)
- [WCAG criterion evidence](screenshots/after/report-criteria-desktop.png)
- [Issue evidence](screenshots/after/report-issues-desktop.png)
- [Verification gaps](screenshots/after/report-gaps-desktop.png)
- [ACR draft top](screenshots/after/acr-top-desktop.png)
- [Complete matrix](screenshots/after/matrix-desktop.png)

Before versions are in [`screenshots/before/`](screenshots/before/).

## Data preservation results

- 5 release cards and 5 target report directories.
- 428 unique active issues.
- 428 matrix rows on `matrix.html`.
- 30 full-evidence and 398 metadata-only records.
- 29 issues with merge requests.
- All target `evidence.json`, `summary.json`, `openacr.yaml`,
  `openacr-validation.json`, `acr.html` and `acr.md` links.
- ATAG report and both JSON exports.
- Every target issue anchor and WCAG criterion anchor.
- The ACR remains `Not Evaluated` per criterion and keeps the component
  proposals.

The data-preservation assertions are in `tests/test_pages.py`; the finder and
matrix generation assertions are in `tests/test_usability.py`.

## Test and accessibility results

- **117 offline tests pass**.
- axe-core: **0 violations** on the homepage, complete matrix, 12.0.0-alpha1
  report, ACR draft and ATAG report at 1280 px.
- 320 px: `scrollWidth` = 320 on all five pages; wide tables scroll inside
  focusable regions.
- Keyboard: first Tab reaches the skip link; Enter moves focus to `<main>`.
  Native radio filters, links, table scroll regions and `<details>` are usable
  without script.
- JavaScript disabled: 5 release cards, 428 issue records and the issue/criterion
  indexes remain in the HTML. No `<script>` is present; JavaScript payload is
  zero.
- CSS-only filters were exercised: All 5 → Supported 2 → line 12.0.x 2 →
  reset 5.
- Approximate page sizes after the change: homepage 28 KB, complete matrix
  228 KB, 12.0.0-alpha1 report 924 KB, ACR 52 KB. The matrix moved off the
  homepage, so the homepage fell from about 240 KB to 28 KB.

## Remaining limitations and next PR

- **No dynamic issue search/filtering.** The Pages workflow rejects any
  `<script>`, so issue-level search, component filters and issue-index
  filtering are deferred. A future PR should decide whether to allow a small
  progressive-enhancement script or generate static per-component pages. The
  current issue index is a compact scan, not a search interface.
- **Release finder is filter/index based, not a text search.** Exact-version
  lookup uses the release index and the browser Find command.
- **No component grouping** of issue evidence yet; the issue index exposes the
  component column but does not group rows.
- **No per-issue AI summary cache** in the site; the weekly digest is separate.
- **Manual testing remains outstanding:** screen reader, real 400% zoom,
  forced-colors and reduced-motion testing. Automated checks do not establish
  conformance.
- **The ACR remains a draft**; no criterion has a conformance term.

Recommended next PR: add progressive issue search/component filters with a
no-JavaScript fallback, or add static per-component issue pages. That is the
largest remaining usability gap for the developer-remediation task.
