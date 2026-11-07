# ADR 0003: Multi-target release lines and parent ACRs

Status: Accepted for the prototype
Date: 2026-11-07

## Context

A single 11.4.12 report is not enough. Drupal normally supports two release
lines, while `main` is the bleeding edge where new issues and fixes land. A
report must keep an old issue visible across 10.x, 11.x and 12.x until it is
closed or ruled out for a target. Components move between core and contributed
projects: Claro and Olivero are core themes in 10.x/11.x and contributed
projects in 12.x. Drupal CMS and LocalGov Drupal combine Core with their own
modules, themes and recipes and need separate ACRs with a parent Core ACR.

## Decision

1. Add `config/drupal-core-targets.json` as the policy source for supported,
   pre-release and development targets.
2. Use one shared issue collection and analyze it independently against each
   target's tag or branch.
3. Make target branch sets explicit. A 10.6 analysis must not treat an 11.x fix
   as evidence for 10.6.
4. Add `ref_type="branch"` support. Branch findings are labelled development
   results and never described as release claims.
5. Render a landing page with a cross-release matrix and one report per target.
6. Run a weekly workflow that opens a review PR; a human merge triggers Pages.
7. Carry `parent_project` in target metadata and document the intended graph
   Core → Claro/Olivero and Core → Drupal CMS/LocalGov. Do not inherit
   conformance automatically.

## Consequences

- The same issue remains visible across release lines, with target-specific
  status and reasoning.
- 10.6.21 currently produces many `unknown` results because fixes landed on
  newer branches and the generic “Admin theme” component spans Claro and Default
  Admin. This is honest but highlights the need for issue-level component and
  feature evidence.
- Support labels and EOL notes are maintained policy, not inferred from tags.
- Weekly generation is review-gated; the site is not an unreviewed auto-deploy.
- Parent-linked contributed-project ACRs, Composer lock resolution for
  distributions and a full project graph remain future work.

## Alternatives considered

- Run five independent pipelines: rejected because it duplicates issue retrieval
  and loses a single shared evidence snapshot.
- Treat 12 pre-releases and `main` as supported releases: rejected; they are not
  release claims.
- Auto-deploy the weekly snapshot: rejected under the publication policy; the
  workflow opens a PR instead.
- Copy Core conformance into Claro/Olivero/CMS/LocalGov: rejected; each needs its
  own scoped assessment and parent link.
