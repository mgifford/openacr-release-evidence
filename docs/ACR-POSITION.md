# Why this ACR is different

This project publishes an **issue-queue accessibility attestation**, not a
conventional periodic vendor ACR and not a WCAG-EM evaluation report. The
distinction should be explicit in every generated report.

A VPAT is a template; a completed report is an Accessibility Conformance Report
(ACR). Most vendor ACRs are completed periodically, based on a selected sample of
pages or workflows, then reviewed and approved by legal or product management.
The vendor's issue queue is usually a separate internal system and is not linked
from the ACR. A barrier can remain open after the report is signed.

This project takes a different approach:

- It reads the **full active Drupal Core Accessibility issue queue** on a weekly
  cadence, not a selected page sample.
- Every cited issue remains linked to its public Drupal.org discussion.
- Web and Authoring Tool are reported separately because they are different
  surfaces with different users and barriers.
- The ACR is regenerated from the current queue and declared release target; it
  is not a static document refreshed every year or two.
- Issue-tagged criteria are summarized as unverified evidence and remain Not Evaluated; criteria with no
  tagged issue remain `Not Evaluated`, because absence of a reported issue is not
  evidence of support.
- The weekly workflow opens a review PR. Merging that PR is the publication
  review event; it is not an automatic certification.

## Comparison

| Dimension | Conventional vendor ACR | This issue-queue attestation |
|---|---|---|
| Cadence | Annual, biennial or procurement-driven | Every weekly tracker snapshot |
| Evidence base | Selected pages, flows or a WCAG-EM sample | Full active Accessibility issue queue; detailed comments/MRs where collected |
| Traceability | Summary claims, often without issue links | Every cited issue links to the public Drupal.org source |
| Scope | Vendor-selected product snapshot | Declared target, ref/commit, configuration and collection date |
| Authoring tool | Often folded into web or omitted | Explicit Authoring Tool component, separate remarks |
| Review | Vendor/legal approval, sometimes a third party | Review-gated PR, draft terms and human sign-off still required |
| Change over time | Static until the next report | Incremental; new issues and status changes appear in the next snapshot |
| Independence | Often a commissioned assessment | Community-reported issue evidence; **no independent WCAG-EM audit** |

## What is stronger

- **Completeness of known reports:** every active queue item is represented, not
  only a sample of pages.
- **Traceability:** a reader can open the issue, its comments and merge requests.
- **Recency:** the report changes when the queue changes, rather than waiting for
  a periodic review.
- **Backlog connection:** unresolved barriers remain visible instead of
  disappearing after a signed report.
- **Authoring/web separation:** both surfaces are named and assessed separately.

## What is weaker

- **No independent page/sample evaluation.** This is not WCAG-EM, not an
  independent audit and not a manual assistive-technology test.
- **Depends on issue quality.** The issue must carry the Accessibility tag, a
  useful criterion tag and enough information to understand the barrier.
- **Cannot see unreported barriers.** A missing issue is not evidence of support.
- **Not a legal certification.** A procurement process may still require a
  separate ACR/VPAT or evaluation report in the purchaser's required format.

## How it should be read

- Treat the queue as **reported barrier evidence**, not as a complete census of
  every possible barrier.
- Treat the criterion result as a **draft issue-queue attestation**, subject to
  human confirmation.
- Do not turn issue counts into a conformance score or a percentage.
- Do not assume that an untagged criterion is supported.
- Use the linked issues and the evidence report to plan remediation; use a
  WCAG-EM or procurement-specific evaluation when the buyer requires one.

## References

- [GSA OpenACR issue #180 — Accessibility Statements, OpenACR and WCAG-EM best practices](https://github.com/GSA/openacr/issues/180)
- [Drupal ACR process — use the issue queue as evidence, not as the evaluation](https://www.drupal.org/docs/getting-started/accessibility/accessibility-conformance-report-acr-process)
- [WCAG-EM 2.0](https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/)
- [GSA OpenACR](https://github.com/GSA/openacr)
