# Conformance and evidence policy

**This project does not automatically issue ACRs or certify WCAG compliance.**

Issue tickets provide positive evidence of reported problems. They do not prove
absence of problems. A closed issue may still affect an older release, while a
main-branch issue may reference a feature absent from the release. Git commit
inclusion does not prove behavioural correction. A successful automated check
covers only the test’s assertions, not an entire WCAG success criterion.

We require release-target specificity and evidence-backed applicability.
Insufficient evidence is `unknown`. Status and severity are not conformance
levels. Model confidence is not conformance confidence. The same issue may have
different applicability for distinct assessment targets.

## Applicability is not conformance

- `confirmed-affected` requires a reproduction on the target release. The
  automated pipeline does not emit it.
- `likely-affected` means report evidence suggests the barrier is present but it
  was not reproduced.
- `confirmed-fixed` means a matching fix commit is contained in the target tag
  **and** the tracker is closed fixed. It remains `unreviewed` and explicitly
  notes that commit inclusion is not behavioural verification.
- `not-introduced` requires code/feature evidence that the affected feature is
  absent from the release. Absence of issue reports is never such evidence.
- `not-in-scope` records a declared scope exclusion; it is not a statement that
  the barrier does not exist.
- `unknown` is the safe default.

A finding must carry a target, an observation timestamp, a source URL, a reason,
a basis, evidence URLs and a review state. Reviewed decisions need a date and a
reviewer identity or attributable review record. A new artifact must not
silently overwrite a reviewed decision; it should mark it `stale` and request
re-review.

## OpenACR draft export

`openacr.yaml` is a **validated draft**, not a final conformance decision. It
lists every catalog criterion and the four Section 508 components. Issue-tagged
Web/Authoring components have no adherence value: issue tags are reported
barriers, not conformance results. Electronic Documents and Software are
`not-applicable` from documented product scope; all other unassessed values are
unset. Schema/catalog validity is not evidence that a
claim is true. A reviewer must confirm every value, complete the reviewer identity
and independently approve the file; `--strict` rejects a draft, a placeholder
reviewer and unfilled criteria. The official editor round-trip is not yet verified.

## Active-issue scope

An ACR evidence pass covers active, review-relevant issues only: Active, Needs
review, Needs work, RTBC and Patch. Fixed, closed, duplicate, won't-fix,
works-as-designed, outdated, cannot-reproduce and postponed issues are excluded.
RTBC is included until the issue is closed. Closed/fixed issues must not be
resurrected as conformance evidence.

The full Accessibility queue is paginated; a first-page sample is not a census.
All active issues are inventoried. Full comments/MRs/commit analysis is collected
for a review-priority subset; inventory-only issues are explicitly marked and do
not receive a release applicability conclusion.

## ACR narrative

The ACR narrative uses a draft issue-queue evidence summary. Web and Authoring
Tool use Partially Supports for known active issues and Supports when the assessed
surface has no known issue. Electronic Documents and Software are Not Applicable
from documented product scope. Does Not Support requires explicit broad-failure
evidence and is not emitted automatically. Issue reports are not release
reproductions; a reviewer must confirm every term. The
narrative does not replace the OpenACR YAML and does not inherit ATAG results.

## Issue-queue attestation versus a periodic vendor ACR

This project publishes an **issue-queue accessibility attestation**, not a
WCAG-EM evaluation. Standard vendor ACRs are often periodic, sample-based
snapshots approved by legal or product management, with the issue queue kept
separate. This report reads the full active Drupal Core Accessibility queue,
links every cited issue, separates Web and Authoring Tool, and regenerates
weekly.

It is stronger on known-report completeness, traceability, recency and backlog
connection. It is weaker on independent page sampling, manual assistive-
technology coverage and visibility of unreported barriers. It is not a
certification, not a substitute for a procurement-specific ACR, and does not
claim that an untagged criterion is supported.

See [Why this ACR is different](ACR-POSITION.md), [GSA OpenACR issue
#180](https://github.com/GSA/openacr/issues/180) and the [Drupal ACR
process](https://www.drupal.org/docs/getting-started/accessibility/accessibility-conformance-report-acr-process).

## ATAG evidence

ATAG 2.0 authoring evidence is separate from WCAG/OpenACR. The `atag` issue tag
is evidence of a reported authoring-tool problem, not an ATAG result. Part A/B
tags and curated `config/atag-scope.json` mappings are authoritative; component
candidates are triage only. The WAI ATAG Report Tool JSON contains no results
(all 63 criteria `Not checked`). No ATAG conclusion may be copied into an OpenACR
WCAG value, and no WCAG conclusion may be copied into ATAG.

## Before a formal OpenACR

1. Select the scope and exact installation, including the Composer lockfile where
   applicable.
2. Enumerate applicable criteria from the declared standards baseline.
3. Document manual and automated testing methods, including limitations.
4. Record reviewer decisions separately from generated suggestions.
5. Validate the result against the official GSA OpenACR schema and editor.

Do not map unknown WCAG A/AA results to `Not Evaluated`: that OpenACR option has
restricted use. Never auto-fill `Supports`. Do not describe the current YAML
worksheet as a valid or import-ready OpenACR.

Changes to this policy require public review under `GOVERNANCE.md`.
