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
use `Partially Supports` for known issues and `Supports` when an assessed surface
has no known issue. No issue is treated as reproduced
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
5. **Why this ACR is different** — direct comparison with a periodic,
   sample-based vendor ACR; issue-queue attestation scope; strengths and
   limitations; links to GSA OpenACR #180 and the Drupal ACR process.
6. **Executive summary** — active issue counts, status distribution, largest
   explicitly tagged criterion clusters and unmapped issues.
7. **WCAG 2.2 Level A and AA tables** — one row per catalog criterion with:
   - criterion number, title and W3C link;
   - conformance level for Web, Electronic Documents, Software and Authoring
     Tool;
   - separate Web and Authoring Tool barrier paragraphs;
   - statistics and examples at the bottom with direct Drupal.org issue links;
   - examples are a bulleted list, labelled **Example:** when there is one and
     **Examples:** otherwise;
   - the **All issue references** link is omitted when every issue is already
     shown in the examples.
- Every section heading has a visible `#` permalink with a descriptive
  accessible name; the “On this page” navigation also lists subsection headings.
- Every WCAG criterion row has a stable `#criterion-x-y-z` target and a local
  permalink, so a long report can be linked at the criterion level.
- Anchors use native fragment navigation, `scroll-margin`, and the existing
  skip link. No SkipTo JavaScript is required or published; the static heading
  index provides the same section/heading jump function without client scripts.
   - known issues produce `Partially Supports`; assessed surfaces with no known
     issue produce `Supports`.
8. **AAA table** — outside the declared AA target; issue-tagged criteria use the
   same surface-assessment policy; no `Does Not Support` is emitted without broad-failure evidence.
9. **References** — every cited issue grouped by criterion, with public links.
10. **Functional performance, hardware, software and support documentation** —
   outside the web issue-evidence method’s coverage; reviewer must evaluate or
   mark Not Applicable with a rationale.
11. **ATAG** — separate standard; links to the ATAG evidence, never copied into a
   WCAG criterion.
12. **Review actions** — collect missing evidence, verify the product, select each
   ACR result, complete reviewer identity and approval, remove the draft status.
13. **Limitations and sources** — active-only scope, no reproduction, inventory
    limits, source links.

## Authoring vs web classification

Use explicit evidence: `/admin` paths, Drupal login paths (`/user`,
`/user/login`, `/user/password`), login/reproduction steps or an administrator
account indicate the authoring interface; public front-end pages indicate web.
All `/user` paths, including `/user/1`, are authoring/account surfaces. The
component policy in `config/surface-policy.json` maps `navigation.module`,
toolbar, CKEditor, media library, Layout Builder, Views UI and Field UI to
authoring, with issue-specific overrides available. Record the basis and review
ambiguous cases. An authoring interface may also serve live content, so
the boundary must be explained.

Drupal Core has no audio/video playback, live audio/video, or core video player.
The narrative marks 1.2.1, 1.2.3, 1.2.4 and 1.2.5 as **N/A for Core** and points
to the contrib Able Player or Video modules for separate assessment. Component
labels are bold; `Not Applicable` is shortened to `N/A` in the table display;
`Evidence:` is omitted for simple no-issue rows and retained, bolded, for rows
with active issue evidence.

## Project context notes

Human-maintained scope and AI wording notes live in [`context/DRUPAL.md`](../context/DRUPAL.md)
for Drupal Core, with separate files for Drupal CMS, LocalGov Drupal and CKEditor.
They describe component treatment, authoring boundaries and issue references.
They are not evidence and do not assign conformance.

## Relationship to OpenACR and ATAG

- **OpenACR YAML** is the machine-readable, schema/catalog-validated draft. It
  contains all 182 criteria. Issue-tagged criteria carry proposed
  no adherence values from issue tags; Electronic Documents
  and Software are `not-applicable`; untagged Web/Authoring values are unset.
- **ACR narrative** is the human-readable explanation for reviewers. It presents
  the same draft issue-queue evaluation with separate Web/Authoring remarks,
  bottom-of-cell statistics/examples and per-criterion references. Where an
  accepted `acr-summaries.json` cache exists, the paragraph is a model-assisted
  draft; otherwise it is a deterministic issue-title extract.
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

## Criterion disability labels

The Criteria column includes a short **Affects:** line derived from the
CivicActions WCAG-to-FPC mapping. It identifies disability groups for orientation;
it is not a severity ranking, a complete taxonomy or a substitute for testing with
disabled people.

## Beyond WCAG

A separate bottom-of-report box records non-WCAG accessibility considerations:
EN 301 549 user preferences, visually induced motion sickness, reduced motion and
forced-colors/high-contrast modes. These are review gaps, not conformance terms,
and they are not included in OpenACR.

## References grouping

References are grouped into collapsible POUR sections: Perceivable, Operable,
Understandable and Robust. The groups are open by default so criterion reference
anchors remain visible; they can be collapsed for scanning.

## Surface assessment and positive evidence

The declared Drupal surface assessment is the baseline. A known active issue on
an assessed surface is Partially Supports; an assessed surface with no known
issue is Supports. Not Applicable requires documented feature absence. Does Not
Support requires explicit broad-failure evidence. Not Evaluated is reserved for
an unassessed surface.

## References

The structure follows common ACR reporting practice; **OpenACR is the
machine-readable format** and the schema/catalog pinned in this repository.

- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [GSA OpenACR](https://github.com/GSA/openacr)
