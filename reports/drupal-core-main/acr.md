# Drupal Core 12.0.x-dev — Draft Accessibility Conformance Report (ACR) Narrative

_Issue evidence is described for human review. No criterion is assigned Supports, Partially Supports or Does Not Support._

This document converts the active issue evidence into an ACR narrative. It is deliberately not a completed ACR: every criterion is marked Not Evaluated until a named reviewer completes the evaluation and approves the report.

## Product information

**Product and report identification**

| Field | Value |
| --- | --- |
| Product | Drupal Core |
| Version / release | 12.0.x-dev |
| Target ref | main (branch) |
| Support status | development |
| Report date | 2026-11-08 |
| Report status | DRAFT — not approved for publication |
| Prepared by | Unassigned reviewer (draft) |
| Assessment identifier | drupal-core-main |
| Standards baseline | WCAG 2.2 AA, Section 508 (revised, 2017) |

## Component scope and proposed result

These are proposed component-level labels for review, not final ACR terms. Every per-criterion result below remains Not Evaluated until a reviewer completes it.

**Section 508 component scope**

| Component | Proposed result | Evidence | Rationale |
| --- | --- | --- | --- |
| Web | Partially Supports (proposed) | 415 active findings classified as front-end/web | Partially Supports is proposed because active front-end accessibility issues exist in the published evidence. This label needs a specific explanation and independent review. |
| Electronic Documents | Not Applicable (proposed) | No core electronic-document product | Not Applicable is proposed: Drupal Core is a web CMS, not a standalone electronic-document authoring or playback product. Uploaded documents are delivered as web content. |
| Software | Not Applicable (proposed) | No packaged/non-web software product | Not Applicable is proposed: Drupal Core is web software. The Section 508 software chapter is not a separate installed application in this scope. |
| Authoring Tool | Partially Supports (proposed) | 13 active findings classified as authoring/admin UI | Partially Supports is proposed because active authoring-interface issues exist. The /admin, Drupal /user login and login/reproduction cues are the classification basis; a reviewer must confirm. |

Supports, Partially Supports and Not Applicable are conformance labels. A proposed Partially Supports result requires an explanation; a proposed Supports result must also be explained. The ACR template records this structure for reuse.

Surface counts are draft classification evidence. Inventory-only records have no collected descriptions/comments and default to Web; add explicit issue-queue guidance or tags to improve the authoring/web split.

## Draft status and ACR result terms

ACR result terms are defined here so the draft uses the same vocabulary as a completed ACR. This draft assigns no per-criterion term. A reviewer must select each term from the definitions below after evaluating the product.

**ACR result terms used in review**

| Term | Meaning |
| --- | --- |
| Supports | The product has at least one method of meeting the criterion, and the reviewer has evidence that it works for the evaluated scope. |
| Partially Supports | Some product functionality meets the criterion; other functionality does not, and the reviewer can explain the boundary. |
| Does Not Support | The majority of product functionality does not meet the criterion. |
| Not Applicable | The criterion is not relevant to the product, and the reviewer records why. |
| Not Evaluated | The reviewer has not completed enough evaluation to select a per-criterion term. Every criterion row uses this; the component proposals above are not per-criterion terms. |

## Scope and evaluation method

The evidence collection covers active, review-relevant Drupal Core Accessibility issues: Active, Needs review, Needs work, RTBC and Patch. Fixed, closed and postponed issues are excluded. The snapshot contains 428 active findings, of which 193 carry at least one explicit WCAG issue tag.

30 findings have full comments and merge-request evidence; 398 are metadata-only inventory records. The inventory records identify active issues but do not include comments, merge requests or commit analysis. All findings are unreviewed.

- Discovery pages the complete Accessibility queue; it does not stop at the first API page.
- WCAG tags are candidate relevance signals from the issue queue, not conformance determinations.
- No issue was reproduced against an installed Drupal target in this pass.
- No keyboard, screen-reader, zoom, reduced-motion or forced-colors testing of the product is claimed.
- No AI was used to assign applicability or an ACR result.

## Executive summary

The active queue contains 428 issues. Tracker states are: Active: 235, Needs review: 14, Needs work: 172, Reviewed & tested by the community: 7. 30 issues have detailed evidence and 398 are inventory-only. The queue is a triage input, not an accessibility score.

The largest explicitly tagged criterion clusters are listed below. A count reflects issue tagging, not severity or conformance.

- WCAG 4.1.2: 39 active issues
- WCAG 1.3.1: 23 active issues
- WCAG 3.3.1: 18 active issues
- WCAG 1.4.11: 15 active issues
- WCAG 1.1.1: 12 active issues
- WCAG 2.4.3: 9 active issues
- WCAG 2.5.3: 9 active issues
- WCAG 3.1.2: 9 active issues

235 active findings have no WCAG criterion tag. They remain in the evidence report and may still describe accessibility barriers; no criterion is inferred from their prose.

## WCAG 2.2 Level A criteria

**WCAG 2.2 Level A remarks and explanations**

| Criterion | Level | Active issue evidence | Draft result | Remarks and explanations |
| --- | --- | --- | --- | --- |
| 1.1.1 — Non-text Content | A | 12 active (1 detailed, 11 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 12 active issues tagged to this criterion: 1 detailed, 11 metadata-only inventory. Tracker statuses: Active: 7, Needs work: 5. Target evidence states: likely-affected: 1, unknown: 11. Examples: Add GUI to configure the site's logo alt attribute (drupal:2780293, Needs work); Do not use a CSS-only required marker in forms per WCAG 2.0 (drupal:2921627, Needs work); Media alt text not available in Views (drupal:2960415, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.2.1 — Audio-only and Video-only (Prerecorded) | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 1.2.2 — Captions (Prerecorded) | A | 3 active (0 detailed, 3 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 3 active issues tagged to this criterion: 0 detailed, 3 metadata-only inventory. Tracker statuses: Active: 1, Needs work: 2. Target evidence states: unknown: 3. Examples: Provide authors with tools to manage transcripts and captions/subtitles for local video… (drupal:3002770, Active); Provide a FieldType and FieldWidget to represent a WebVTT file for the HTML track element (drupal:3056714, Needs work); Update audio and video file field formatters to include track elements (drupal:3057144, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.2.3 — Audio Description or Media Alternative (Prerecorded) | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 1.3.1 — Info and Relationships | A | 23 active (3 detailed, 20 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 23 active issues tagged to this criterion: 3 detailed, 20 metadata-only inventory. Tracker statuses: Active: 7, Needs review: 1, Needs work: 15. Target evidence states: likely-affected: 3, unknown: 20. Examples: Allow a custom HTML element to be selected for a grouping field (drupal:1383696, Needs work); #description_display broken for details elements (drupal:2443815, Needs work); [Meta] Set the required state for all fields in Core in the Accessibility Object Model… (drupal:2852874, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.3.2 — Meaningful Sequence | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 1.3.3 — Sensory Characteristics | A | 1 active (0 detailed, 1 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: unknown: 1. Examples: Top-level menu items in the footer region are too far away from their submenu items (drupal:3531948, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.4.1 — Use of Color | A | 7 active (0 detailed, 7 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 7 active issues tagged to this criterion: 0 detailed, 7 metadata-only inventory. Tracker statuses: Active: 2, Needs work: 5. Target evidence states: unknown: 7. Examples: Style state select as a button bar (drupal:2863052, Active); Add an exposed filter to the Taxonomy overview view page (drupal:2975863, Needs work); Improve accessibility of Views table sortable columns (drupal:3038386, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.4.2 — Audio Control | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 2.1.1 — Keyboard | A | 8 active (1 detailed, 7 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 8 active issues tagged to this criterion: 1 detailed, 7 metadata-only inventory. Tracker statuses: Active: 6, Needs review: 1, Needs work: 1. Target evidence states: likely-affected: 1, unknown: 7. Examples: Return to tab position when exiting dialog opened from contextual link (drupal:2915762, Needs work); 508 Compliance - Tooltips not displayed for keyboard navigation (drupal:2933984, Active); Re-evaluate whether Contextual Links are the best interaction for configuring/moving/de… (drupal:3042516, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.1.2 — No Keyboard Trap | A | 1 active (0 detailed, 1 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Active: 1. Target evidence states: unknown: 1. Examples: Accessing a toolbar sub-menu seems to result in a keyboard trap (drupal:3559162, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.1.4 — Character Key Shortcuts | A | 1 active (0 detailed, 1 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Active: 1. Target evidence states: unknown: 1. Examples: Add an API for hotkeys to Drupal core (drupal:3532392, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.2.1 — Timing Adjustable | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 2.2.2 — Pause, Stop, Hide | A | 1 active (0 detailed, 1 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Active: 1. Target evidence states: unknown: 1. Examples: [policy, no patch] Use "prefers-reduced-motion" media query to disable animations (drupal:2928103, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.3.1 — Three Flashes or Below Threshold | A | 1 active (0 detailed, 1 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Active: 1. Target evidence states: unknown: 1. Examples: [policy, no patch] Use "prefers-reduced-motion" media query to disable animations (drupal:2928103, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.4.1 — Bypass Blocks | A | 1 active (1 detailed, 0 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 1 detailed, 0 metadata-only inventory. Tracker statuses: Needs review: 1. Target evidence states: likely-affected: 1. Examples: Use $element['#attributes]['id'] instead of $element['#id'] to create a link anchor (drupal:3557245, Needs review). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. |
| 2.4.2 — Page Titled | A | 2 active (0 detailed, 2 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 2 active issues tagged to this criterion: 0 detailed, 2 metadata-only inventory. Tracker statuses: Needs work: 2. Target evidence states: unknown: 2. Examples: Allow global tokens (and therefore page numbers) in display title (drupal:2509716, Needs work); Page title should contextualize the local navigation (drupal:3370946, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.4.3 — Focus Order | A | 9 active (0 detailed, 9 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 9 active issues tagged to this criterion: 0 detailed, 9 metadata-only inventory. Tracker statuses: Active: 9. Target evidence states: unknown: 9. Examples: Make sure controls within hidden content are not focusable (drupal:2925295, Active); When enabling or disabling a block, don't move the focus to the top of the page (drupal:2973114, Active); Return focus to point of action when the off-canvas dialog closes (drupal:3019849, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.4.4 — Link Purpose (In Context) | A | 2 active (0 detailed, 2 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 2 active issues tagged to this criterion: 0 detailed, 2 metadata-only inventory. Tracker statuses: Needs work: 2. Target evidence states: unknown: 2. Examples: "Add new comment" and "@count comments" links are not following accessibility good prac… (drupal:2922435, Needs work); Make the link descriptions more descriptive, helpful, and clear. (drupal:3439721, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.5.1 — Pointer Gestures | A | 2 active (0 detailed, 2 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 2 active issues tagged to this criterion: 0 detailed, 2 metadata-only inventory. Tracker statuses: Active: 2. Target evidence states: unknown: 2. Examples: Research accessibility of drag-and-drop grid interfaces. (drupal:2920006, Active); Modernize tabledrag accessibility. (drupal:3027229, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.5.2 — Pointer Cancellation | A | 4 active (0 detailed, 4 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 4 active issues tagged to this criterion: 0 detailed, 4 metadata-only inventory. Tracker statuses: Active: 1, Needs work: 3. Target evidence states: unknown: 4. Examples: Right click should not submit buttons with Ajax behaviors (drupal:2616184, Needs work); Assess JavaScript behaviours for WCAG 2.1 Pointer Cancellation (drupal:2958654, Needs work); Replace javascript event listeners which use "down" events in the ajax component (drupal:2960840, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.5.3 — Label in Name | A | 9 active (1 detailed, 8 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 9 active issues tagged to this criterion: 1 detailed, 8 metadata-only inventory. Tracker statuses: Active: 6, Needs review: 1, Needs work: 2. Target evidence states: likely-affected: 1, unknown: 8. Examples: Link labels generated by the Entity List Builder should provide more context for a11y (drupal:2960828, Needs work); Provide better context in accessible names of EntityOperation views plugin drop-button… (drupal:2973124, Needs work); Assess Drupal core for WCAG success criterion 2.5.3 Label in Name (drupal:3015239, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.5.4 — Motion Actuation | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 3.1.1 — Language of Page | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 3.2.1 — On Focus | A | 3 active (0 detailed, 3 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 3 active issues tagged to this criterion: 0 detailed, 3 metadata-only inventory. Tracker statuses: Active: 3. Target evidence states: unknown: 3. Examples: Redundant aural interface and the general interaction with CKEditor toolbar configuration (drupal:3506324, Active); Selecting a column in a table header by keyboard drops the focus (drupal:3506339, Active); Select field in modal dialog has jumpy focus (drupal:3611769, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 3.2.2 — On Input | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 3.2.6 — Consistent Help | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 3.3.1 — Error Identification | A | 18 active (2 detailed, 16 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 18 active issues tagged to this criterion: 2 detailed, 16 metadata-only inventory. Tracker statuses: Active: 4, Needs review: 1, Needs work: 13. Target evidence states: likely-affected: 2, unknown: 16. Examples: The file upload field needs a progress indicator that expresses to screen reading user… (drupal:2089703, Needs work); Error highlighting and reporting problems for the current password on the user profile… (drupal:2455933, Needs work); Inline Errors not shown for container elements (drupal:2560467, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 3.3.2 — Labels or Instructions | A | 7 active (0 detailed, 7 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 7 active issues tagged to this criterion: 0 detailed, 7 metadata-only inventory. Tracker statuses: Active: 2, Needs work: 5. Target evidence states: unknown: 7. Examples: Elements on grouped exposed filters configuration form are missing accessible names (drupal:2608212, Needs work); [Meta] Set the required state for all fields in Core in the Accessibility Object Model… (drupal:2852874, Active); Admin list filter fields are inconsistently labelled. (drupal:2942037, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 3.3.7 — Redundant Entry | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 4.1.1 — Parsing | A | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 4.1.2 — Name, Role, Value | A | 39 active (2 detailed, 37 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 39 active issues tagged to this criterion: 2 detailed, 37 metadata-only inventory. Tracker statuses: Active: 17, Needs review: 1, Needs work: 21. Target evidence states: likely-affected: 2, unknown: 37. Examples: Allow modules to classify blocks when defining them, so WAI-ARIA roles can automaticall… (drupal:1402250, Needs work); Cached render elements can have duplicate HTML IDs (drupal:1852090, Needs work); Add "changed" hints to translation settings page (drupal:1854046, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |

## WCAG 2.2 Level AA criteria

**WCAG 2.2 Level AA remarks and explanations**

| Criterion | Level | Active issue evidence | Draft result | Remarks and explanations |
| --- | --- | --- | --- | --- |
| 1.2.4 — Captions (Live) | AA | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. Core scope: Drupal Core does not provide live audio/video. Proposed Not Applicable for Core; evaluate the contrib Video or AblePlayer modules separately. |
| 1.2.5 — Audio Description (Prerecorded) | AA | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. Core scope: Drupal Core does not provide a video player or audio-description feature. Proposed Not Applicable for Core; audio/video caption and description support belongs to contrib Video or AblePlayer. |
| 1.3.4 — Orientation | AA | 1 active (0 detailed, 1 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: unknown: 1. Examples: Extend site information page to generate a manifest.json file (drupal:2698127, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.3.5 — Identify Input Purpose | AA | 2 active (0 detailed, 2 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 2 active issues tagged to this criterion: 0 detailed, 2 metadata-only inventory. Tracker statuses: Needs work: 2. Target evidence states: unknown: 2. Examples: IME enhancement stops autocomplete search event in Android when typing an English word (drupal:2928820, Needs work); Provide a new library to replace jQuery UI autocomplete (drupal:3076171, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.4.3 — Contrast (Minimum) | AA | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 1.4.4 — Resize text | AA | 1 active (0 detailed, 1 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: unknown: 1. Examples: Improve indentation in hierarchical select lists (drupal:2384203, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.4.5 — Images of Text | AA | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 1.4.10 — Reflow | AA | 4 active (0 detailed, 4 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 4 active issues tagged to this criterion: 0 detailed, 4 metadata-only inventory. Tracker statuses: Active: 2, Needs work: 2. Target evidence states: unknown: 4. Examples: Dialogs sub-optimal when fully zoomed (drupal:2234745, Active); Add another responsive tables solution that doesn't hide content (drupal:2280035, Needs work); Re-wrap text in views interface when zooming in mobile (drupal:2313471, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.4.11 — Non-text Contrast | AA | 15 active (3 detailed, 12 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 15 active issues tagged to this criterion: 3 detailed, 12 metadata-only inventory. Tracker statuses: Active: 9, Needs review: 2, Needs work: 4. Target evidence states: likely-affected: 3, unknown: 12. Examples: Add new Splitbutton render element to eventually replace Dropbutton (drupal:1899236, Needs work); Refine the layout selection UI (drupal:2848549, Active); Improve icon color contrast for WCAG 2.1 (drupal:2910102, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.4.12 — Text Spacing | AA | 1 active (0 detailed, 1 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Active: 1. Target evidence states: unknown: 1. Examples: Page title ellipsis accessibility issue (drupal:3623836, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 1.4.13 — Content on Hover or Focus | AA | 1 active (0 detailed, 1 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: unknown: 1. Examples: Top-level menu items in the footer region are too far away from their submenu items (drupal:3531948, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.4.5 — Multiple Ways | AA | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 2.4.6 — Headings and Labels | AA | 4 active (0 detailed, 4 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 4 active issues tagged to this criterion: 0 detailed, 4 metadata-only inventory. Tracker statuses: Active: 1, Needs work: 3. Target evidence states: unknown: 4. Examples: Add option for visually-hidden block titles (drupal:2614950, Needs work); Allow wrapping field labels in a heading tag (drupal:3277785, Needs work); [ATAG] Text editor should alert user when headings are out of order (drupal:3293673, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.4.7 — Focus Visible | AA | 7 active (1 detailed, 6 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 7 active issues tagged to this criterion: 1 detailed, 6 metadata-only inventory. Tracker statuses: Active: 3, Needs review: 1, Needs work: 3. Target evidence states: likely-affected: 1, unknown: 6. Examples: Build API to Replace Links using Title Attributes with Proper Accessible, Themable Tool… (drupal:1919940, Needs work); Add option to un-sticky table headers to benefit assistive tech users (drupal:3163765, Needs work); [drupalImage] Scroll to last image when uploading multiple images (drupal:3272493, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.4.11 — Focus Not Obscured (Minimum) | AA | 2 active (0 detailed, 2 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 2 active issues tagged to this criterion: 0 detailed, 2 metadata-only inventory. Tracker statuses: Active: 1, Needs work: 1. Target evidence states: unknown: 2. Examples: CKEditor 5 has its own focus styles, should use the admin theme's (e.g. Claro's) (drupal:3272592, Needs work); Some top-level menus obscure unrelated focused items in sidebar (drupal:3573225, Active). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 2.5.7 — Dragging Movements | AA | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 2.5.8 — Target Size (Minimum) | AA | 1 active (1 detailed, 0 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 1 detailed, 0 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: likely-affected: 1. Examples: Add a '#select_all' option for checkboxes element (drupal:3459246, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. |
| 3.1.2 — Language of Parts | AA | 9 active (0 detailed, 9 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 9 active issues tagged to this criterion: 0 detailed, 9 metadata-only inventory. Tracker statuses: Active: 6, Needs work: 3. Target evidence states: unknown: 9. Examples: Views containing content not in the page's language need to add tags which mark the lan… (drupal:2496223, Active); DateList and date range inline form errors are repeated (drupal:2827034, Needs work); Links in language switcher block do not conform to WCAG language-of-parts (drupal:3020305, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 3.2.3 — Consistent Navigation | AA | 3 active (0 detailed, 3 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 3 active issues tagged to this criterion: 0 detailed, 3 metadata-only inventory. Tracker statuses: Active: 1, Needs work: 2. Target evidence states: unknown: 3. Examples: Modules uninstall filter does not filter by machine name (drupal:2895388, Needs work); Make admin list filters behave more consistently. (drupal:3015494, Active); Scrolling problems when adding a block via layout builder (drupal:3209129, Needs work). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |
| 3.2.4 — Consistent Identification | AA | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 3.3.3 — Error Suggestion | AA | 1 active (1 detailed, 0 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 1 active issue tagged to this criterion: 1 detailed, 0 metadata-only inventory. Tracker statuses: Needs review: 1. Target evidence states: likely-affected: 1. Examples: Forms sidebar doesn't open with error links from Inline Form Errors module (drupal:3619127, Needs review). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. |
| 3.3.4 — Error Prevention (Legal, Financial, Data) | AA | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 3.3.8 — Accessible Authentication (Minimum) | AA | No active tagged issue | Not Evaluated (draft — reviewer must select an ACR result) | No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that the criterion is met; a reviewer must evaluate it and select an ACR result. |
| 4.1.3 — Status Messages | AA | 6 active (1 detailed, 5 inventory) | Not Evaluated (draft — reviewer must select an ACR result) | 6 active issues tagged to this criterion: 1 detailed, 5 metadata-only inventory. Tracker statuses: Active: 3, Needs review: 1, Needs work: 2. Target evidence states: likely-affected: 1, unknown: 5. Examples: Dropbutton should report open/closed state to assistive technology (drupal:2893663, Active); After enabling or disabling a view, convey changes to screen reader users. (drupal:2973116, Active); Convey AJAX progress messages to assistive technology. (drupal:2973140, Needs review). This is issue-queue evidence, not a conformance result; verify the barrier and select the ACR result. Inventory records have no comments, merge requests or commit analysis. |

## WCAG 2.2 Level AAA criteria

31 AAA criteria are outside the declared WCAG 2.2 AA target. They are not marked Supports or Not Applicable in this draft; a reviewer must decide whether to evaluate them or record a scope rationale.

## Functional performance, hardware, software and support documentation

These Section 508/ACR chapters are not evaluated by this web issue-evidence pipeline. They are shown so the draft has the complete ACR shape; a reviewer must evaluate them or mark Not Applicable with a rationale.

**Non-WCAG ACR chapters**

| Chapter | Criteria | Draft result | Remarks and explanations |
| --- | --- | --- | --- |
| functional_performance_criteria | 9 | Not Evaluated | Outside the web issue-evidence method's coverage. The pipeline collected issue/commit evidence only; no hardware, packaged software, functional-performance or support-documentation testing was performed. |
| hardware | 55 | Not Evaluated | Outside the web issue-evidence method's coverage. The pipeline collected issue/commit evidence only; no hardware, packaged software, functional-performance or support-documentation testing was performed. |
| software | 26 | Not Evaluated | Outside the web issue-evidence method's coverage. The pipeline collected issue/commit evidence only; no hardware, packaged software, functional-performance or support-documentation testing was performed. |
| support_documentation_and_services | 5 | Not Evaluated | Outside the web issue-evidence method's coverage. The pipeline collected issue/commit evidence only; no hardware, packaged software, functional-performance or support-documentation testing was performed. |

## ATAG 2.0 authoring evidence

ATAG 2.0 is a separate standard from WCAG and is not part of this ACR narrative. Drupal Core's authoring-tool evidence is reported separately, with Part A/Part B candidates and a WAI ATAG Report Tool JSON draft containing no conformance values.

See ../drupal-core-atag/ for the ATAG evidence report. It must not be copied into a WCAG criterion result.

## Active issue evidence and review actions

The evidence report lists all active issues and their source links. It distinguishes full-detail evidence from metadata-only inventory records. Use it to review the criterion remarks above, collect missing evidence and decide each ACR result.

- Use the generic templates/drupal-acr-template.md as the reusable ACR shell.
- Open ./index.html#issues and review the active issue evidence.
- For inventory records, read the source issue and collect the missing comments, merge requests and target evidence.
- Verify each criterion against the installed product; do not convert issue counts into Supports or Does Not Support.
- Complete the reviewer name, organization and approval record outside this generated draft.
- Replace every Not Evaluated result with a reviewed ACR result, or record the remaining evaluation gap.
- Remove the draft status only after independent review and sign-off.

## Limitations

- This is an issue-queue evidence narrative, not a WCAG-EM sample or a conformance test.
- Fixed and closed issues are excluded by policy; their absence is not evidence that a barrier is gone.
- The 398 inventory records have no comments/MRs/commit analysis; they are included for completeness, not as finished findings.
- No reproduction, assistive-technology testing, hardware testing or packaged-software testing is claimed.
- The product is a declared Drupal Core configuration; it is not every Drupal site.
- The draft does not establish legal compliance or a procurement-safe conformance claim.

## Sources

**Authoritative sources**

| Source | Link |
| --- | --- |
| Drupal Core Accessibility queue | [Drupal.org Accessibility issue queue](https://www.drupal.org/project/issues/search?text=&projects=Drupal+core&assigned=&submitted=&project_issue_followers=&status%5B%5D=Open&issue_tags_op=%3D&issue_tags=Accessibility) |
| WCAG 2.2 | [W3C WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/) |
| OpenACR | [GSA OpenACR](https://github.com/GSA/openacr) |
| ATAG 2.0 | [W3C ATAG 2.0](https://www.w3.org/TR/ATAG20/) |
| WAI ATAG Report Tool | [WAI ATAG Report Tool](https://www.w3.org/WAI/atag/report-tool/) |
