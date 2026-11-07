# Conformance and evidence policy

**This project does not automatically issue ACRs or certify WCAG compliance.**

Issue tickets provide positive evidence of reported problems. They do not prove
absence of problems. A closed issue may still affect an older release, while a
main-branch issue may reference a feature absent from the release. Git commit
inclusion does not prove behavioural correction. A successful automated check
covers only the test's assertions, not an entire WCAG success criterion.

We require release-target specificity and evidence-backed applicability.
Insufficient evidence is `unknown`. Status and severity are not conformance
levels. Model confidence is not conformance confidence. The same issue may
have different applicability for distinct assessment targets.

Before a formal OpenACR: select scope, verify exact installation including
Composer lockfile, enumerate applicable criteria, document testing including
manual methods, record reviewer decisions, and run GSA format/schema/editor
validation. Do not map unknown WCAG Level A/AA results to `Not Evaluated`:
that OpenACR option has restricted use. Never auto-fill `Supports`.

Changes to the policy require public review under GOVERNANCE.md.
