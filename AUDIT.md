# AUDIT.md — Phase 0 audit of the OpenACR release-evidence prototype

Status: complete for the first vertical slice (2026-11-07).
Scope: the existing Python pipeline, static explorer, tests, manifests, CI,
documentation, and the installed `drupalorg-cli`.

This audit records what was independently verified, what was only a stub, what
was corrected in this change, and what remains open. It is not a conformance
report and does not certify Drupal or this project.

## 1. Environment and method

- macOS (arm64), Python 3.14.5, `python` not on PATH (only `python3`), PHP 8.5.9,
  Composer 2.10.3, Git 2.54.0, Playwright 1.63.0 and axe-core 4.13.0.
- `drupalorg-cli` 0.15.0 was installed with Composer into a temporary
  `COMPOSER_HOME` for validation. It is **not** committed and is not a runtime
  dependency of the package.
- Live read-only probes were made against `www.drupal.org/api-d7` and
  `git.drupalcode.org/api/v4` on 2026-11-07. No issue was modified, and no
  mutating CLI command was called.
- The existing test suite was run before and after changes. The explorer and the
  new report were rendered in headless Chromium with axe-core, at 1280 px and
  320 px, with keyboard and JavaScript-disabled passes.

## 2. What already worked

- `build` produced a static explorer from the synthetic manifest and fixtures.
- The core safety rule held: closed issues stayed `unknown`; no `Supports`
  output was produced; overrides needed a reason, a basis and an HTTPS URL.
- `evidence.json` was deterministic for the same input and `generated_at`.
- The explorer used `textContent` and `createElement` rather than `innerHTML`.
- The existing `git_release.commit_in_ref` correctly distinguished “commit in a
  tag” from “fix verified”.
- The repository-wide and nested `AGENTS.md` files contained useful boundaries,
  and several were already reflected in tests.

## 3. What was a stub, missing, or wrong

### 3.1 Verified defects corrected in this change

| Severity | Defect | Evidence | Correction |
| --- | --- | --- | --- |
| High | The published `evidence_digest` could not be reproduced from the published artifact. The digest covered the full manifest, including overrides, while the artifact stripped overrides. | Recomputed digest from `site/evidence.json` differed: `5d3567…` vs `6251a7…`. | Digest now covers the exact published artifact minus `generated_at`/`evidence_digest`; a separate `manifest_digest` covers the input. See `model.digest_artifact`. |
| High | Findings had no per-finding target or observation timestamp. | `model.assess` output had only top-level assessment and `source_updated_at` (tracker update time). | Findings now carry `assessment_id`, `target`, `observed_at`, and `observed_at_basis`. |
| High | Placeholder release values passed validation. | `release: "SET-A-REAL-RELEASE"` and `"EXAMPLE-UNVERIFIED"` passed `validate_manifest`. | Placeholder values are rejected unless `"synthetic": true`; the example manifest is marked synthetic and the templates now fail until filled. |
| High | `mr:list` was called without `--state=all`; the CLI defaults to **opened** MRs, so merged/closed MRs were invisible. | `drupalorg help mr:list` documents the default; live `mr:list 3621109` returned a closed MR only when `--state=all` was used. | The bridge passes `--state=all` and preserves all states. |
| High | `issue:show` never requested comments. | The old code passed only `--format=llm`; `--with-comments` is a separate option. | JSON output plus `--with-comments` is now used for ingestion. |
| High | Drupal status 8 was assumed to mean “closed fixed”. | Live pages: 8 = “Needs review”, 7 = “Closed (fixed)”, 2 = “Fixed”, 13 = “Needs work”, 14 = “RTBC”, 17 = “Closed (outdated)”, 18 = “Closed (cannot reproduce)”. | A verified status map is in `model.STATUS_LABELS`; normalisation uses it. |
| High | The explorer overflowed horizontally at 320 px. | Rendered 320 px: `scrollWidth` 602; the 64-character digest text extended to x=602; the select was 325 px wide. | `overflow-wrap` was added; the select uses `width:100%; max-width:23rem`. Verified `scrollWidth` 320. |
| Medium | The explorer was unusable with JavaScript disabled. | Text stopped at “Loading assessment…” / “Loading findings…”. | Added a `<noscript>` message with a link to `evidence.json`; the new report is fully static and needs no JS. |
| Medium | The skip link did not move focus to `<main>`. | In Chromium, `activeElement` remained `BODY` after activation. | `<main tabindex="-1">` in both the explorer and the report; verified `activeElement` is `MAIN`. |
| Medium | `openacr.py` had no test and the “no Supports” assertion was case-sensitive and findings-only. | Audit found no test for `export_worksheet`. | Added `tests/test_openacr.py`, including a case-insensitive no-`Supports` check. |
| Medium | Snapshot writing had a check-then-write race and chmod after write. | `save_private_snapshot` used `exists()` then `write_text` then `chmod`. | Uses `O_CREAT|O_EXCL` with mode `0600`; path guard also rejects `public-*` components. |
| Medium | `collect-drupal` could not record comments, and the MR state was incomplete. | See above. | `collect_issue` returns `issue`/`merge_requests` JSON plus raw CLI records. |
| Low | `atomic_write_json` produced `0600` collection/analysis files. | `mkstemp` default mode persisted. | Output artifacts use `0644`; cache/raw snapshots remain `0600`. |

### 3.2 Open defects and limitations

| Severity | Defect | Why it matters | Next action |
| --- | --- | --- | --- |
| Medium | ACR Editor round-trip and official HTML renderer are not implemented. | Per-report YAML now validates against the pinned Civicactions/GSA schema and catalog, but editor compatibility is unverified. | Import/edit/export in the official editor and reuse its renderer. |
| High | No reproduction or assistive-technology testing of Drupal 11.4.12. | “Likely affected” and “fix included” are not behavioural verification. | Add a manual/imported reproduction protocol; do not upgrade to `confirmed-affected` without it. |
| Medium | Commit matching relies on issue numbers in commit titles. | Fixes delivered without an issue number, via configuration, or in contributed modules are not matched. | Add file/diff-level analysis and a safe manual evidence override path. |
| Medium | Unused applicability overrides are silently ignored. | A typo can leave a reviewer believing evidence was applied. | Warn or fail on override keys that match no collected issue. |
| Medium | The explorer still omits source dates, `ref`, installation and coverage. | `web/AGENTS.md` requires those fields. | Port the report’s scope and observation fields into the explorer, or retire the explorer in favour of the static report. |
| Medium | AI governance describes controls `ai.py` does not implement. | The document overstates validation, hashing, caching and parameter recording. | Keep AI off by default; mark the document as planned or implement before enabling. |
| Medium | `collect-drupal` accepts a bare numeric reference. | A migrated GitLab IID is project-scoped and not globally unique. | Require `project#iid` for migrated projects or emit an explicit ambiguity warning. |
| Resolved | First Pages deployment verified. | https://mgifford.github.io/openacr-release-evidence/ returns 200 after the Pages workflow ran. | Keep the allowlist and environment-review option under review. |
| Low | `run_read` checks the 2 MB limit after capturing stdout. | A very large output is buffered before rejection. | Stream or cap the capture. |
| Low | `git-check` has no timeout and reuses raw revision strings for `merge-base`. | Rare local failure mode; already guarded by `rev-parse --end-of-options`. | Resolve to SHAs and add a timeout. |
| Low | CI actions are pinned to major tags, not SHAs. | Supply-chain hardening. | Pin digests when the workflow stabilises. |
| Low | The explorer has dead CSS classes and a `role="status"` scope region that announces the long digest. | Noisy announcements; maintenance noise. | Clean up when the explorer is revised. |

## 4. `drupalorg-cli` validation (0.15.0)

Commands verified as read-only on 2026-11-07:

| Command | Verified behaviour |
| --- | --- |
| `drupalorg list` | 0.15.0; includes `issue:show`, `issue:search`, `mr:list`, `mr:show`, `mr:diff`, `mr:files`, `mr:logs`, `project:releases`, `project:contains`, `project:issues`, `skill:get`. |
| `drupalorg skill:get` | Lists `drupalorg-cli`, `drupalorg-issue-search`, `drupalorg-issue-summary-update`, `drupalorg-work-on-issue`. |
| `issue:show <nid> --format=json --with-comments` | JSON with `nid`, timestamps, status, component, version, body and comments. A 40-comment issue produced ~17 KB. |
| `mr:list <nid> --state=all --format=json` | Returns `project_path`, `issue_fork`, and all MR states. Without `--state=all` only opened MRs are returned. |
| `project:releases drupal --format=json` | Returns core releases (11.4.12, 11.3.21, 10.6.21 at audit time). |
| `project:contains drupal <sha> --format=json` | Returns containing branches and tags; agrees with the GitLab refs API. |

The CLI is a **CLI dependency**, not a library contract. Version 0.15.0 output
shapes are now covered by trimmed real fixtures. The bridge deliberately keeps
only an allowlist of read commands and rejects unknown flags.

## 5. Live sample and release analysis

- The full Drupal Core **Accessibility** queue (term 1101) was paged. 428 active,
  review-relevant issues were collected: 1,666 comments, 29 with MR metadata,
  193 with WCAG tags. Statuses are Active (235), Needs work (172), Needs review
  (14) and RTBC (7); fixed, closed, duplicate, won’t-fix, outdated,
  cannot-reproduce and postponed issues are excluded.
- 30 review-priority issues have full comments/MRs; 398 are metadata-only
  inventory records. Inventory records are not assigned a release conclusion.
- Target: Drupal Core **11.4.12**, tag commit `aa556ff1…`, composer.lock
  SHA-256 `d3d2949e…`.
- No active issue has a fix commit contained in the selected targets, so no
  `confirmed-fixed` result is emitted in this active-only pass. Closed-fixed
  issues are not used as evidence.
- 28 detailed issues were classified `likely-affected` for 10.6.21 and 11.4.12;
  400 findings were `unknown` (398 inventory + two detailed issues without a
  target conclusion).
- The target intentionally enables the **Default Admin** theme. Drupal 11.4.12’s
  stock standard profile still uses Claro and Olivero, so this is a declared
  configuration, not the stock default.
- Active evidence demonstrates the open-barrier, fix-only-on-a-newer-branch and
  unknown cases. The closed-fixed/contained-fix case is covered by fixtures
  because closed issues are excluded from the active ACR collection. The
  `not-introduced` case is also fixture-tested with explicit feature-absence
  evidence; a future sample should include a real 11.5-only feature issue.

The evidence report is `reports/drupal-core-11.4.12/index.html`. It is a draft
evidence report, **not** an ACR.

## 6. Tests and checks

- Before: `python3 -m unittest discover -s tests -v` failed with 3 import errors
  when the package was not installed; `python` did not exist on this machine.
  With `PYTHONPATH=src`, 17 tests passed.
- After: 98 offline tests pass; `python3 -m compileall -q src` passes.
- New coverage: normalization, real status mapping, WCAG tag parsing, ATAG
  Part A/B classification, release classification, commit deduplication,
  caching, failure isolation, report escaping/anchors/headings, the digest,
  placeholder guards, the worksheet, OpenACR schema/catalog validation, active
  pagination/inventory, ACR narrative rendering and weekly summary validation.
- Report rendered with axe-core: **0 violations** at 1280 px; `scrollWidth` 320
  at a 320 px viewport; all internal anchors resolve; the skip link focuses
  `MAIN`; `<details>` toggles by keyboard; no JavaScript is required. The ATAG
  report has the same axe/reflow/skip-link result.
- The Pages artifact was simulated locally for the landing page, five target
  reports, the ACR narrative and the ATAG report (45 allowlisted files), with no
  collection/analysis files, private paths or script tags. The landing page,
  matrix region, target reports and ATAG report pass axe at 1280 px and have no
  320 px page overflow.
- Not done: screen-reader/manual keyboard testing of the reports, full WCAG
  catalogue coverage, ACR Editor round-trip, and human ATAG editing/export.
  Official OpenACR schema/catalog validation and ATAG JSON import were verified.

## 7. Documentation claims that were stronger than the implementation

- `docs/AI-GOVERNANCE.md` describes structured output validation, content
  hashes, caching and parameter recording that `ai.py` does not implement.
- `docs/ROADMAP.md` marked a GitHub adapter as done; GitHub Issues are explicitly
  deferred.
- `docs/EVIDENCE-MODEL.md` described an `assessment` containing overrides that
  the published artifact strips, listed fewer finding fields than are emitted,
  and implied input hashes that did not exist.
- `README.md` said the licence was still “proposed” while `LICENSE` already
  granted MIT.
- `GOVERNANCE.md` called `docs/decisions/` “planned” after ADR 0001 existed.
- `.env.example` advertised `GITHUB_TOKEN` for an unimplemented integration.

These were corrected or explicitly marked as planned in this change.

## 8. Next phase

The evidence pipeline (collection → normalization → release classification →
static report) is functioning and repeatable. The next reviewable increments are:

1. ACR Editor round-trip and an HTML export that reuses the official OpenACR
   implementation; schema/catalog validation is now in place, editor compatibility
   is not.
2. A provider-independent AI interface with a no-AI path preserved, a validated
   structured-response schema, and gold-standard evaluation (Phase 3).
3. Manual reproduction evidence for a small number of `likely-affected` and
   `confirmed-fixed` findings, with review state and reviewer identity.
4. Drupal CMS and LocalGov manifests and Composer-lock analysis (Phase 7).
5. Explorer parity with the report’s scope, observation and coverage fields, or
   retirement of the explorer in favour of the static report.

See `docs/ROADMAP.md` for sequencing.


## 9. Post-audit increments (2026-11-07)

After the first audit and report:

- **Pages is live:** `https://mgifford.github.io/openacr-release-evidence/` returns
  200; the workflow deploys an explicit allowlist and rejects raw/private paths,
  `collection.json`/`analysis.json` and client-side scripts.
- **Node 24 actions:** CI and Pages now use `checkout@v7`,
  `setup-python@v7`, `upload-artifact@v7`, `configure-pages@v6`,
  `upload-pages-artifact@v5` and `deploy-pages@v5`, resolving the Node 20
  deprecation warning from run 42402400410.
- **Multi-target analysis:** the shared 428-issue active collection is analyzed against
  10.6.21 (supported), 11.4.12 (supported), 12.0.0-alpha1 and 12.0.0-beta2
  (pre-release), and `main`/12.0.x-dev (development). The landing page contains a
  cross-release matrix; each cell links to the target finding.
- **Weekly review gate:** `weekly.yml` runs Mondays at 13:00 UTC and on manual
  dispatch, runs tests, collects, analyzes and opens a PR. It does not publish;
  a human merge triggers Pages.
- **Parent graph:** `parent_project` is carried in target metadata and documented
  as Core → Claro/Olivero and Core → Drupal CMS/LocalGov. Parent-linked ACR
  generation is not implemented.
- **Active-issue scope and pagination:** the earlier collection was an explicit
  20-issue sample and discovery stopped at one API page. The fix pages the full
  Accessibility queue (50 per page, up to 200 pages), keeps only statuses 1, 8,
  13, 14 and 15, excludes fixed/closed/postponed issues, and retains 428 active
  issues (30 full-detail, 398 inventory-only). RTBC remains included until
  closed.
- **ACR narrative:** each target exports `acr.html` and `acr.md` with
  product information, ACR result terms, active-evidence remarks for every
  WCAG 2.2 A/AA criterion, non-WCAG chapters, ATAG separation and reviewer
  actions. Every criterion remains **Not Evaluated**; no issue count becomes a
  ACR result.
- **Report-size reduction:** the duplicate per-target `analysis.json` files and
  stale per-target collection were removed, `evidence.json` is a compact
  published artifact, and inventory issue HTML is a compact metadata row. The
  report set fell from about 50 MB to about 16 MB.
- **Weekly ACR digest:** `weekly-summary` compares the current active
  collection with the previous snapshot, writes immutable facts/Markdown/
  provenance files under `reports/weekly/`, and optionally asks a pinned
  Hugging Face model for the executive summary only. The output is validated
  against the facts, conformance language is rejected, and the deterministic
  digest is used on failure. The digest is not an ACR result.
- **ATAG 2.0 evidence:** 32 active Drupal Core issues tagged `atag` are collected from
  the Accessibility queue, grouped by explicit Part A/B tags, curated mapping and
  component candidates, and exported as `atag-evidence.json` plus a WAI ATAG
  Report Tool JSON draft (`atag-report.json`, all 63 criteria `Not checked`).
  The ATAG report is separate from the WCAG matrix and the OpenACR draft.
- **OpenACR export:** each target now exports `openacr.yaml` and
  `openacr-validation.json`. The YAML is valid against the pinned Civicactions/
  GSA OpenACR 0.1.0 schema and the OpenACR 2.5 WCAG 2.2 + Section 508 catalog, with
  all 182 criteria and no conformance values. A placeholder reviewer and
  `draft: true` force human review; `openacr-validate --strict` checks the
  reviewed file. All five drafts were independently checked with the official
  `@civicactions/openacr` 0.3.11 CLI and returned `Valid!`. Editor round-trip
  remains pending.
- **ATAG caveat:** the queue currently exposes only the generic `atag` tag, so
  most issues are component candidates or unspecified; Part A/B tags and
  curated mappings are supported. Import into the live WAI ATAG Report Tool was
  verified (draft metadata loaded; all 52 A/AA criteria `Not checked`), but
  human editing/export and release-scoped applicability are not yet verified.

Current multi-target result (428 active issues, no reproduction):

| Target | Support | Fix included | Confirmed fixed | Likely affected | Unknown |
| --- | --- | ---: | ---: | ---: | ---: |
| 10.6.21 | Supported | 0 | 0 | 28 | 400 |
| 11.4.12 | Supported | 0 | 0 | 28 | 400 |
| 12.0.0-alpha1 | Pre-release | 0 | 0 | 23 | 405 |
| 12.0.0-beta2 | Pre-release | 0 | 0 | 26 | 402 |
| `main` | Development | 0 | 0 | 30 | 398 |

The 10.6 result is deliberately conservative. The generic “Admin theme”
component spans Claro and Default Admin, and fixes landed on newer branches; the
model cannot yet prove that a Default Admin issue is or is not a Claro issue.
Issue-level component/feature evidence is the next accuracy improvement.
