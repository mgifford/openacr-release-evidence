# ACR narrative

Each target exports:

- `acr.html` — static, no-JavaScript narrative
- `acr.md` — editable Markdown source

This is a human-readable companion to the validated OpenACR YAML. It follows the
shape of an ACR: product information, term definitions, scope and method,
executive summary, WCAG 2.2 A/AA/AAA criterion tables, non-WCAG chapters, ATAG separation,
reviewer actions, limitations and sources.

## What it does not do

It uses a **draft issue-queue evaluation**. Criteria with active tagged issues
carry a draft `Partially Supports` result for Web and Authoring Tool; criteria
without a tagged issue remain `Not Evaluated`. No issue is treated as reproduced
against an installed target. The four component results are draft proposals for
human confirmation.

The narrative does **not** claim:

- that a criterion is met because no issue is tagged;
- that an issue count is a severity or conformance score;
- that an issue was reproduced against an installed Drupal target;
- that manual, keyboard, screen-reader, zoom or assistive-technology testing was
  performed;
- that hardware, packaged software, functional-performance or support
  documentation was evaluated.

## Structure

1. **Product information** — product, version, target ref, support status,
   report date, draft status, placeholder reviewer, assessment ID and standards
   baseline.
2. **Component scope** — Section 508 results for Web, Electronic Documents,
   Software and Authoring Tool. Web and Authoring Tool are draft Partially
   Supports; Electronic Documents and Software are Not Applicable. Component
   labels are proposals for review.
3. **ACR result terms** — definitions for Supports, Partially Supports, Does Not
   Support, Not Applicable and Not Evaluated.
4. **Scope and method** — active statuses, full-queue pagination, detailed vs
   metadata-only inventory, no reproduction, no AI.
5. **Executive summary** — active issue counts, status distribution, largest
   explicitly tagged criterion clusters and unmapped issues.
6. **WCAG 2.2 Level A and AA tables** — one row per catalog criterion with:
   - criterion number, title and W3C link;
   - conformance level for Web, Electronic Documents, Software and Authoring
     Tool;
   - remarks and explanations with issue evidence, statuses, target evidence
     states, examples and the explicit warning that no issue was reproduced.
   - issue-tagged criteria use draft `Partially Supports`; untagged criteria
     remain `Not Evaluated`.
7. **AAA table** — outside the declared AA target; issue-tagged criteria use the
   same draft rule; untagged criteria remain `Not Evaluated`.
8. **Functional performance, hardware, software and support documentation** —
   outside the web issue-evidence method’s coverage; reviewer must evaluate or
   mark Not Applicable with a rationale.
9. **ATAG** — separate standard; links to the ATAG evidence, never copied into a
   WCAG criterion.
10. **Review actions** — collect missing evidence, verify the product, select each
   ACR result, complete reviewer identity and approval, remove the draft status.
11. **Limitations and sources** — active-only scope, no reproduction, inventory
    limits, source links.

## Authoring vs web classification

Use explicit evidence: `/admin` paths, Drupal login paths (`/user`,
`/user/login`, `/user/password`), login/reproduction steps or an administrator
account indicate the authoring interface; public front-end pages indicate web.
All `/user` paths, including `/user/1`, are authoring/account surfaces. Record the basis (`admin-path`, `login-step` or `default-web`) and
review ambiguous cases. An authoring interface may also serve live content, so
the boundary must be explained.

Drupal Core has no live audio/video feature. For 1.2.4 and 1.2.5 the narrative
records a proposed Not Applicable for Core and points to the contrib Video or
AblePlayer modules for separate assessment.

## Project context notes

Human-maintained scope and AI wording notes live in [`context/DRUPAL.md`](../context/DRUPAL.md)
for Drupal Core, with separate files for Drupal CMS, LocalGov Drupal and CKEditor.
They describe component treatment, authoring boundaries and issue references.
They are not evidence and do not assign conformance.

## Relationship to OpenACR and ATAG

- **OpenACR YAML** is the machine-readable, schema/catalog-validated draft. It
  contains all 182 criteria. Issue-tagged criteria carry proposed
  `partially-supports` values for Web and Authoring Tool; Electronic Documents
  and Software are `not-applicable`; untagged Web/Authoring values are unset.
- **ACR narrative** is the human-readable explanation for reviewers. It presents
  the same draft issue-queue evaluation with full remarks.
- **ATAG evidence** is a separate authoring-tool report. It is not part of the
  ACR WCAG chapters.

All three must be reviewed by a person. A schema-valid file or a complete
narrative is not a conformance claim.

## Review workflow

1. Read the executive summary and scope.
2. For each criterion with active issues, open `index.html#issues` and review the
   source issues.
3. For metadata-only inventory issues, collect comments, merge requests and
   target evidence before relying on them.
4. Verify the criterion against the installed product, with the declared scope.
5. Select the ACR result and write a specific remark that names the evidence and
   the limitation.
6. Replace the placeholder reviewer and complete the approval record outside the
   generated draft.
7. Remove the draft statement only after independent review and sign-off.

## References

The structure follows common ACR reporting practice; **OpenACR is the
machine-readable format** and the schema/catalog pinned in this repository.

- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [GSA OpenACR](https://github.com/GSA/openacr)
