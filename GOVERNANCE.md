# Governance (initial proposal)

## Mission and scope

Develop reusable, auditable, public-interest tooling for documenting accessibility
evidence about **specific software releases** and preparing human-reviewed draft
ACRs. No project or vendor can buy a favourable assessment.

## Decision-making

Until a maintainer group is formally constituted, the repository owner is the
interim steward. This file is a **proposed governance model**, not evidence of an
existing elected committee. Changes to scope, policy, licence and data formats
require a public issue, rationale, review period of at least 7 calendar days,
and a recorded decision. Security and privacy emergency fixes may bypass the
waiting period with retrospective explanation.

Recommended future structure: at least three maintainers, including an
accessibility practitioner and a technical maintainer, with published terms,
rotating responsibility and open meeting notes. Seek participation from Drupal
Core, Drupal CMS, LocalGov Drupal, procurement and disability communities.

## Roles

- Contributors: submit issues, patches, tests, documentation.
- Maintainers: review changes, run CI, merge and release.
- Evidence reviewers: verify mappings, target applicability and test results.
- ACR approvers: independently sign off on assertions for a defined target.

Maintainer status **never** grants authority to approve an ACR on behalf of
Drupal Association, GSA, vendors or any third party.

## Decisions and appeal

Record design decisions in `docs/decisions/` (planned) or traceable issues/PRs.
Require at least one independent code review for changes to source adapters,
release interpretation or policy. Report perceived errors publicly where safe.
Anyone may challenge an accessibility claim with evidence; disputed claims
must be visibly marked and re-reviewed. Contributors may appeal decisions
through a new issue; conflicts of interest require recusal.

## Transparency and sustainability

Publish data provenance and correction histories; use open standards and avoid
model/vendor lock-in. Avoid unnecessary repeated model inference and retain
minimal personal information. Contributors retain attribution under the
repository licence. Funding and institutional sponsorship must not override
technical findings.

## Community standards

See `CODE_OF_CONDUCT.md` and `SECURITY.md`. A small project cannot promise
response SLAs; security and personal information are handled privately.
