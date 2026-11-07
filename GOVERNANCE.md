# Governance (initial proposal)

## Mission and scope

Develop reusable, auditable, public-interest tooling for documenting accessibility
evidence about **specific software releases** and preparing human-reviewed draft
ACRs. No project or vendor can buy a favourable assessment.

## Decision-making

Until a maintainer group is formally constituted, the repository owner is the
interim steward. This file is a **proposed governance model**, not evidence of an
existing elected committee. Changes to scope, policy, licence and data formats
require a public issue, rationale, a review period of at least 7 calendar days,
and a recorded decision. Security and privacy emergency fixes may bypass the
waiting period with retrospective explanation.

Recommended future structure: at least three maintainers, including an
accessibility practitioner and a technical maintainer, with published terms,
rotating responsibility and open meeting notes. Seek participation from Drupal
Core, Drupal CMS, LocalGov Drupal, procurement and disability communities.

## Roles

These roles are **not yet staffed**; they describe separation of duty, not an
existing committee.

- Contributors: submit issues, patches, tests and documentation.
- Maintainers: review changes, run CI, merge and release.
- Source adapter maintainers: own Drupal.org/GitLab retrieval and read-only
  command semantics.
- Evidence reviewers: verify mappings, target applicability, observation times
  and test results.
- Report approvers: independently sign off on statements for a defined target.
- AI model and prompt maintainers: own provider configuration, prompt versions,
  evaluation, cost controls and disclosure. They cannot approve ACR claims.

Maintainer status **never** grants authority to approve an ACR on behalf of the
Drupal Association, GSA, vendors or any third party.

## Decisions, challenge and correction

Record consequential design decisions in `docs/decisions/` (ADR 0001 and 0002
exist) or in traceable issues/PRs. Require at least one independent code review
for changes to source adapters, release interpretation or policy.

Anyone may challenge an accessibility claim with evidence. A disputed claim must
be visibly marked, its review state set to `stale` or `needs-evidence`, and it
must be re-reviewed before reuse. Corrections should preserve the previous
artifact and its digest rather than silently overwriting history. Report
perceived errors publicly where safe; use `SECURITY.md` for private issues.

Contributors may appeal decisions through a new issue. Conflicts of interest
require recusal.

## Publication

A generated report is a draft, not a publication authorization. Publishing to
GitHub Pages requires an approver to confirm the target, scope, evidence links,
redactions and that the artifact contains no raw private tracker data. Approval
of a release tag or a commit is not approval of an ACR.

## Transparency and sustainability

Publish data provenance and correction histories; use open standards and avoid
model/vendor lock-in. Avoid unnecessary repeated retrieval or model inference and
retain minimal personal information. Contributors retain attribution under the
repository licence. Funding and institutional sponsorship must not override
technical findings.

## Community standards

See `CODE_OF_CONDUCT.md` and `SECURITY.md`. A small project cannot promise
response SLAs; security and personal information are handled privately. The
starter code of conduct requires an independently accessible reporting route
before the project invites a larger public community.
