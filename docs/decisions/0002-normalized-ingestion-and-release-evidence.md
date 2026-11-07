# ADR 0002: Normalized ingestion and git-based release applicability

Status: Accepted for the prototype
Date: 2026-11-07

## Context

The starter prototype could build a synthetic explorer, but it could not collect
real Drupal discussion, could miss merged merge requests, treated Drupal status 8
as “fixed”, and produced a digest that could not be reproduced from the published
artifact. It also had no release-specific evidence for a real Drupal Core tag.

## Decision

1. Use Drupal.org REST for filtered discovery and taxonomy tags, and
   `drupalorg-cli` 0.15.0 JSON for per-issue detail, comments and all MR states.
2. Normalize issues into a versioned, source-independent public schema. Keep raw
   payloads private with mode `0600` and never overwrite them.
3. Use the verified Drupal status map (7 = closed fixed, 8 = needs review).
4. Build a cached commit index from the release branch and adjacent development
   branches, deduplicate commits by SHA, and check tag containment through the
   public GitLab refs API.
5. Apply the documented applicability rules. Commit inclusion + a closed-fixed
   tracker may produce `confirmed-fixed`, but the finding remains unreviewed and
   states that behavioural verification is not done.
6. Make `evidence_digest` reproducible from the published artifact and keep a
   separate `manifest_digest` for the input.
7. Generate a static, no-JavaScript report with explicit scope, observation,
   provenance and verification gaps.

## Consequences

- The first real report can be reproduced from a manifest and cached data.
- Some findings remain `unknown`; this is intended.
- Commit matching depends on issue numbers in commit messages; file/diff-level
  evidence and reproduction testing are still required.
- The report is a draft, not an ACR. Official OpenACR schema/editor work remains
  a later milestone.
- No AI is used in this increment.

## Alternatives considered

- Scraping the issue queue HTML: rejected as brittle and less auditable.
- Using only the Drupal.org API: rejected because it does not expose GitLab MR
  state or the CLI’s migration-aware issue detail.
- Treating a commit in a tag as a verified fix: rejected; it conflates code
  inclusion with behavioural correction.
- Reporting only `unknown`: rejected as not useful; documented `likely-affected`
  findings with explicit gaps are more honest and actionable.
