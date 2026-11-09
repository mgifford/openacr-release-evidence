# Roadmap / TODO

## Milestone 0: starter (complete)

- [x] Separate product target from issue and tracker status
- [x] Strict `unknown` applicability default
- [x] Evidence URLs, observation times and reproducible artifact digest
- [x] Browser review of draft evidence, static site, CI tests
- [x] Governance, security, AI, conformance and agent documentation
- [x] Audit of the prototype and correction of verified high-severity defects
- [ ] Confirm permanent name, steward group, licence and private reporting route

## Milestone 1: defensible release applicability (first vertical slice complete)

- [x] Normalized Drupal issue schema with comments, MRs, tags, provenance and
      content hashes
- [x] Real Drupal Core collection through Drupal.org REST + drupalorg-cli 0.15.0
- [x] 20 real accessibility issues, including comments and all MR states
- [x] Exact 11.4.12 tag, tag commit and composer.lock hash
- [x] Commit index, deduplication and tag containment via the GitLab refs API
- [x] Documented applicability rules and five required classification cases
      (the `not-introduced` case is covered by an offline classification test)
- [x] Static, no-JavaScript, 320 px-safe evidence report
- [x] GitHub Pages workflow with an explicit publication allowlist
- [x] First live Pages deployment verified (https://mgifford.github.io/openacr-release-evidence/)
- [x] Node 24 GitHub Actions runtimes
- [x] 122 offline tests, trimmed real fixtures, caching and failure isolation
- [ ] Reproduce `likely-affected` findings against an installed 11.4.12 site
- [ ] Add a human review/approval workflow for `confirmed-fixed`
- [ ] Add file/diff-level evidence for fixes that omit the issue number
- [ ] Add conflicting-evidence and stale-approved-decision handling
- [x] Multi-target policy for 10.6.x, 11.4.x, 12 pre-releases and `main`
- [x] Cross-release applicability matrix and per-target reports
- [x] Weekly review-gated snapshot workflow that opens a PR
- [ ] Issue-level component/theme evidence across the Claro/Default Admin boundary
- [ ] Parse Composer lockfiles and enabled modules/themes/configurations for
      Drupal CMS and LocalGov
- [ ] Parent-linked ACRs for Claro, Olivero, Drupal CMS and LocalGov Drupal
- [ ] Add browser regression checks (Playwright/axe) as an opt-in CI job

## Milestone 2: authoring and trustworthy export

- [x] Pin the Civicactions/GSA OpenACR schema/catalog and export a validated draft per target
- [x] Export an ACR narrative with four Section 508 component scopes and draft issue-queue results
- [x] Add a reusable Drupal ACR template
- [x] Add a no-script release finder, grouped downloads and a separate complete matrix page
- [x] Add report utility links, criterion/issue indexes and ACR section navigation
- [x] Collect ATAG-tagged authoring issues, classify Part A/B candidates and export a WAI ATAG Report Tool JSON draft
- [x] Verify ATAG JSON import in the live WAI ATAG Report Tool
- [ ] Complete human ATAG editing/export and add release-scoped ATAG applicability
- [ ] Round-trip the reviewed YAML in the ACR Editor and reuse the official HTML renderer
- [ ] Reuse the official OpenACR HTML renderer where feasible
- [ ] Add reviewer identity, dates, review states and independently approved
      sign-off
- [ ] Generate an evidence appendix and accessible HTML export
- [ ] Show draft vs approved outputs unambiguously

## Milestone 3: synthesis, other products and automation

- [ ] Provider-independent AI interface with no-AI fallback, schema validation,
      grounding checks, caching and gold-standard evaluation
- [ ] Drupal CMS and LocalGov manifests, exact Core versions and inheritance
      policy
- [ ] GitHub Issues, Jira and non-Drupal GitLab adapters (explicitly deferred)
- [ ] Scheduled incremental ingestion with checkpoints and rate-limit controls
      (weekly collection + review PR is in place; no auto-publish)
- [ ] Publication approval workflow; never auto-publish private evidence
- [ ] Accessibility evaluation of the report with disabled users

## Revised Drupal-first priorities (November 2026)

1. Keep the real Drupal Core evidence pipeline reproducible and audited.
2. Add reproduction evidence and human review rather than increasing issue
   counts.
3. Add official OpenACR schema/editor compatibility and verify the WAI ATAG Report Tool round-trip.
4. Extend to Drupal CMS and LocalGov with exact Composer locks.
5. Only then evaluate AI-assisted synthesis.

GitHub Issues and Jira remain deferred; see `docs/FUTURE-SOURCES.md`.

## Weekly digest

- [x] Deterministic weekly facts and immutable archive
- [x] Optional Hugging Face executive summary with validation, provenance and fallback
- [ ] Publish the weekly digest on Pages
- [ ] Compare Cloudflare and Hugging Face on past snapshots
