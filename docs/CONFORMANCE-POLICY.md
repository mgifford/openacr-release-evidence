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
