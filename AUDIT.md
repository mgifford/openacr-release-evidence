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
| High | Drupal status 8 was assumed to mean “closed fixed”. | Live pages: 8 = “Needs review”, 7 = “Closed (fixed)”, 2 = “Fixed”, 13 = “Needs work”, 14 = “RTBC”, 17 = “Closed (outdated)”. | A verified status map is in `model.STATUS_LABELS`; normalisation uses it. |
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
| High | No official OpenACR schema validation or editor round-trip. | The current worksheet is explicitly not an OpenACR; the mission’s later milestone requires GSA schema/editor compatibility. | Phase 6: pin the official schema, validate, and reuse the official renderer. |
| High | No reproduction or assistive-technology testing of Drupal 11.4.12. | “Likely affected” and “fix included” are not behavioural verification. | Add a manual/imported reproduction protocol; do not upgrade to `confirmed-affected` without it. |
| Medium | Commit matching relies on issue numbers in commit titles. | Fixes delivered without an issue number, via configuration, or in contributed modules are not matched. | Add file/diff-level analysis and a safe manual evidence override path. |
| Medium | Unused applicability overrides are silently ignored. | A typo can leave a reviewer believing evidence was applied. | Warn or fail on override keys that match no collected issue. |
| Medium | The explorer still omits source dates, `ref`, installation and coverage. | `web/AGENTS.md` requires those fields. | Port the report’s scope and observation fields into the explorer, or retire the explorer in favour of the static report. |
| Medium | AI governance describes controls `ai.py` does not implement. | The document overstates validation, hashing, caching and parameter recording. | Keep AI off by default; mark the document as planned or implement before enabling. |
| Medium | `collect-drupal` accepts a bare numeric reference. | A migrated GitLab IID is project-scoped and not globally unique. | Require `project#iid` for migrated projects or emit an explicit ambiguity warning. |
| Medium | GitHub Pages publication is still procedural. | `build`/`report` have no publication gate; `save_private_snapshot` protects only the snapshot path. | Add a publication checklist/allowlist and keep private evidence out of `reports/`. |
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

- 20 Drupal Core issues explicitly tagged **Accessibility** (term 1101) were
  collected: 743 comments, 20 issues with MR metadata, 12 with WCAG tags.
  This meets Phase 1’s 20-issue threshold.
- Target: Drupal Core **11.4.12**, tag commit `aa556ff1…`, composer.lock
  SHA-256 `d3d2949e…`.
- 4 fixes were found contained in the tag:
  3621109, 3623388, 3618127, 3617875.
- 14 were classified `likely-affected`; 2 remained `unknown` because they were
  reported after the release date and have no target-branch fix.
- The target intentionally enables the **Default Admin** theme. Drupal 11.4.12’s
  stock standard profile still uses Claro and Olivero, so this is a declared
  configuration, not the stock default.

The evidence report is `reports/drupal-core-11.4.12/index.html`. It is a draft
evidence report, **not** an ACR.

## 6. Tests and checks

- Before: `python3 -m unittest discover -s tests -v` failed with 3 import errors
  when the package was not installed; `python` did not exist on this machine.
  With `PYTHONPATH=src`, 17 tests passed.
- After: 60 offline tests pass; `python3 -m compileall -q src` passes.
- New coverage: normalization, real status mapping, WCAG tag parsing, release
  classification, commit deduplication, caching, failure isolation, report
  escaping/anchors/headings, the digest, placeholder guards, and the worksheet.
- Report rendered with axe-core: **0 violations** at 1280 px; `scrollWidth` 320
  at a 320 px viewport; all 66 internal anchors resolve; the skip link focuses
  `MAIN`; `<details>` toggles by keyboard; no JavaScript is required.
- Not done: screen-reader/manual keyboard testing of the report, full WCAG
  catalogue coverage, official OpenACR schema validation, live integration tests
  in CI.

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

1. Official OpenACR schema/editor validation and an HTML export that reuses the
   GSA implementation (Phase 6).
2. A provider-independent AI interface with a no-AI path preserved, a validated
   structured-response schema, and gold-standard evaluation (Phase 3).
3. Manual reproduction evidence for a small number of `likely-affected` and
   `confirmed-fixed` findings, with review state and reviewer identity.
4. Drupal CMS and LocalGov manifests and Composer-lock analysis (Phase 7).
5. Explorer parity with the report’s scope, observation and coverage fields, or
   retirement of the explorer in favour of the static report.

See `docs/ROADMAP.md` for sequencing.
