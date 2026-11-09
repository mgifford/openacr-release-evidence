# Drupal Core 12.0.0-beta2 — Draft Accessibility Conformance Report (ACR) Narrative

_Issue-tagged criteria use a draft Partially Supports result based on the open Drupal issue queue; criteria without a tagged issue remain Not Evaluated._

This document converts the active issue evidence into an ACR narrative. It is deliberately not a completed ACR: criteria with active tagged issues use a draft Partially Supports result from the open issue queue, while criteria without a tagged issue remain Not Evaluated. No issue was reproduced against this release, and a named reviewer must approve the report.

## Product information

**Product and report identification**

| Field | Value |
| --- | --- |
| Product | Drupal Core |
| Version / release | 12.0.0-beta2 |
| Target ref | 12.0.0-beta2 (tag) |
| Support status | pre-release |
| Report date | 2026-11-09 |
| Report status | DRAFT — not approved for publication |
| Prepared by | Unassigned reviewer (draft) |
| Assessment identifier | drupal-core-12.0.0-beta2 |
| Standards baseline | WCAG 2.2 AA, Section 508 (revised, 2017) |

## Component scope and proposed result

These are proposed component-level labels for review, not final ACR terms. Criteria with active tagged issues carry a draft Partially Supports result; criteria without a tagged issue remain Not Evaluated.

**Section 508 component scope**

| Component | Proposed result | Evidence | Rationale |
| --- | --- | --- | --- |
| Web | Partially Supports (proposed) | 417 active findings classified as front-end/web | Partially Supports is proposed because active front-end accessibility issues exist in the published evidence. This label needs a specific explanation and independent review. |
| Electronic Documents | Not Applicable (proposed) | No core electronic-document product | Not Applicable is proposed: Drupal Core is a web CMS, not a standalone electronic-document authoring or playback product. Uploaded documents are delivered as web content. |
| Software | Not Applicable (proposed) | No packaged/non-web software product | Not Applicable is proposed: Drupal Core is web software. The Section 508 software chapter is not a separate installed application in this scope. |
| Authoring Tool | Partially Supports (proposed) | 13 active findings classified as authoring/admin UI | Partially Supports is proposed because active authoring-interface issues exist. The /admin, Drupal /user account paths and login/reproduction cues are the classification basis; a reviewer must confirm. |

Supports, Partially Supports and Not Applicable are conformance labels. A proposed Partially Supports result requires an explanation; a proposed Supports result must also be explained. The ACR template records this structure for reuse.

Reading the tables: Open issue reports are treated as reported barrier evidence; no issue was reproduced against this release. Inventory records have no comments, merge requests or commit analysis. Issue-tagged criteria use draft Partially Supports for Web and Authoring Tool; criteria without a tagged issue remain Not Evaluated. Electronic Documents and Software are Not Applicable because Drupal Core does not ship a standalone electronic-document or packaged software product in this scope.

Surface counts are draft classification evidence. Inventory-only records have no collected descriptions/comments and default to Web; add explicit issue-queue guidance or tags to improve the authoring/web split. A Web result can include barriers that also affect the authoring interface; the per-component remarks identify the classified evidence.

Some Web/Authoring paragraphs are model-assisted draft summaries generated from the cited issue evidence. They are suggestions for human review, not conformance conclusions; the issue list, statistics and references remain the source record.

## Draft status and ACR result terms

ACR result terms are defined here so the draft uses the same vocabulary as a completed ACR. Issue-tagged criteria use draft Partially Supports; criteria without a tagged issue remain Not Evaluated. A reviewer must confirm every term after evaluating the product.

**ACR result terms used in review**

| Term | Meaning |
| --- | --- |
| Supports | The product has at least one method of meeting the criterion, and the reviewer has evidence that it works for the evaluated scope. |
| Partially Supports | Some product functionality meets the criterion; other functionality does not, and the reviewer can explain the boundary. |
| Does Not Support | The majority of product functionality does not meet the criterion. |
| Not Applicable | The criterion is not relevant to the product, and the reviewer records why. |
| Not Evaluated | No active tagged issue and no other evidence supports a per-criterion term. Absence of a tagged issue is not evidence of support. |

## Scope and evaluation method

The evidence collection covers active, review-relevant Drupal Core Accessibility issues: Active, Needs review, Needs work, RTBC and Patch. Fixed, closed and postponed issues are excluded. The snapshot contains 430 active findings, of which 195 carry at least one explicit WCAG issue tag.

32 findings have full comments and merge-request evidence; 398 are metadata-only inventory records. The inventory records identify active issues but do not include comments, merge requests or commit analysis. All findings are unreviewed.

- Discovery pages the complete Accessibility queue; it does not stop at the first API page.
- WCAG tags are candidate relevance signals from the issue queue, not conformance determinations.
- No issue was reproduced against an installed Drupal target in this pass.
- Open issue reports are treated as draft barrier evidence; they are not a release reproduction.
- No keyboard, screen-reader, zoom, reduced-motion or forced-colors testing of the product is claimed.
- No AI was used to assign applicability or an ACR result.

## Executive summary

The active queue contains 430 issues. Tracker states are: Active: 236, Needs review: 15, Needs work: 174, Reviewed & tested by the community: 5. 32 issues have detailed evidence and 398 are inventory-only. The queue is a triage input, not an accessibility score.

The largest explicitly tagged criterion clusters are listed below. A count reflects issue tagging, not severity or conformance.

- WCAG 4.1.2: 39 active issues
- WCAG 1.3.1: 23 active issues
- WCAG 3.3.1: 18 active issues
- WCAG 1.4.11: 17 active issues
- WCAG 1.1.1: 12 active issues
- WCAG 2.4.3: 9 active issues
- WCAG 2.5.3: 9 active issues
- WCAG 3.1.2: 9 active issues

235 active findings have no WCAG criterion tag. They remain in the evidence report and may still describe accessibility barriers; no criterion is inferred from their prose.

## WCAG 2.2 Level A criteria

**Table 1: Success Criteria, Level A**

| Criteria | Conformance Level | Remarks and Explanations |
| --- | --- | --- |
| [1.1.1 Non-text Content](https://www.w3.org/TR/WCAG22/#non-text-content) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Reported web barriers include: Add GUI to configure the site's logo alt attribute; Media alt text not available in Views; Find a way to differentiate different media types in the administrative media library grid view.   Authoring Tool:  Reported authoring barriers include: Do not use a CSS-only required marker in forms per WCAG 2.0.   Evidence:  12 active issues tagged to this criterion: 1 detailed, 11 metadata-only inventory. Tracker statuses: Active: 7, Needs work: 5. Target evidence states: likely-affected: 1, unknown: 11.   Examples:  [Add GUI to configure the site's logo alt attribute (drupal:2780293, Needs work)](https://www.drupal.org/project/drupal/issues/2780293) ;  [Do not use a CSS-only required marker in forms per WCAG 2.0 (drupal:2921627, Needs work)](https://www.drupal.org/project/drupal/issues/2921627) ;  [Media alt text not available in Views (drupal:2960415, Active)](https://www.drupal.org/project/drupal/issues/2960415)   All issue references:  [1.1.1 reference list](#ref-1-1-1) |
| [1.2.1 Audio-only and Video-only (Prerecorded)](https://www.w3.org/TR/WCAG22/#audio-only-and-video-only-prerecorded) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.2.2 Captions (Prerecorded)](https://www.w3.org/TR/WCAG22/#captions-prerecorded) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle to manage transcripts and captions for videos due to missing tools. Authoring tools lack fields and formatters for WebVTT files and track elements.   Authoring Tool:  No issues classified for authoring tools.   Evidence:  3 active issues tagged to this criterion: 0 detailed, 3 metadata-only inventory. Tracker statuses: Active: 1, Needs work: 2. Target evidence states: unknown: 3.   Examples:  [Provide authors with tools to manage transcripts and captions/subtitles for l… (drupal:3002770, Active)](https://www.drupal.org/project/drupal/issues/3002770) ;  [Provide a FieldType and FieldWidget to represent a WebVTT file for the HTML t… (drupal:3056714, Needs work)](https://www.drupal.org/project/drupal/issues/3056714) ;  [Update audio and video file field formatters to include track elements (drupal:3057144, Needs work)](https://www.drupal.org/project/drupal/issues/3057144)   All issue references:  [1.2.2 reference list](#ref-1-2-2) |
| [1.2.3 Audio Description or Media Alternative (Prerecorded)](https://www.w3.org/TR/WCAG22/#audio-description-or-media-alternative-prerecorded) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.3.1 Info and Relationships](https://www.w3.org/TR/WCAG22/#info-and-relationships) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may encounter issues with form fields missing required attributes, unclear asterisk markers, and inaccessible system messages. Assistive technologies might struggle with empty regions and missing fieldset titles.   Authoring Tool:  Authors might face challenges with pager templates failing accessibility tests, particularly with the use of ellipsis, which can misstructure lists.   Evidence:  23 active issues tagged to this criterion: 3 detailed, 20 metadata-only inventory. Tracker statuses: Active: 7, Needs review: 1, Needs work: 15. Target evidence states: likely-affected: 3, unknown: 20.   Examples:  [Allow a custom HTML element to be selected for a grouping field (drupal:1383696, Needs work)](https://www.drupal.org/project/drupal/issues/1383696) ;  [#description_display broken for details elements (drupal:2443815, Needs work)](https://www.drupal.org/project/drupal/issues/2443815) ;  [[Meta] Set the required state for all fields in Core in the Accessibility Obj… (drupal:2852874, Active)](https://www.drupal.org/project/drupal/issues/2852874)   All issue references:  [1.3.1 reference list](#ref-1-3-1) |
| [1.3.2 Meaningful Sequence](https://www.w3.org/TR/WCAG22/#meaningful-sequence) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.3.3 Sensory Characteristics](https://www.w3.org/TR/WCAG22/#sensory-characteristics) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users with visual disabilities may struggle to find and access submenu items in the footer due to their distance from top-level menu items.   Authoring Tool:  No issues classified for authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: unknown: 1.   Examples:  [Top-level menu items in the footer region are too far away from their submenu… (drupal:3531948, Needs work)](https://www.drupal.org/project/drupal/issues/3531948)   All issue references:  [1.3.3 reference list](#ref-1-3-3) |
| [1.4.1 Use of Color](https://www.w3.org/TR/WCAG22/#use-of-color) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle with style state select as a button bar and tabledrag due to lack of accessible visual feedback. The severity column icons and 'unpublished' entity style are also inaccessible.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  7 active issues tagged to this criterion: 0 detailed, 7 metadata-only inventory. Tracker statuses: Active: 2, Needs work: 5. Target evidence states: unknown: 7.   Examples:  [Style state select as a button bar (drupal:2863052, Active)](https://www.drupal.org/project/drupal/issues/2863052) ;  [Add an exposed filter to the Taxonomy overview view page (drupal:2975863, Needs work)](https://www.drupal.org/project/drupal/issues/2975863) ;  [Improve accessibility of Views table sortable columns (drupal:3038386, Needs work)](https://www.drupal.org/project/drupal/issues/3038386)   All issue references:  [1.4.1 reference list](#ref-1-4-1) |
| [1.4.2 Audio Control](https://www.w3.org/TR/WCAG22/#audio-control) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.1.1 Keyboard](https://www.w3.org/TR/WCAG22/#keyboard) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle with navigating dialogues and contextual links, and may have difficulty with keyboard navigation and focus management. Datepickers and hotkeys may also lack accessibility, impacting users who rely on these features.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  8 active issues tagged to this criterion: 1 detailed, 7 metadata-only inventory. Tracker statuses: Active: 6, Needs review: 1, Needs work: 1. Target evidence states: likely-affected: 1, unknown: 7.   Examples:  [Return to tab position when exiting dialog opened from contextual link (drupal:2915762, Needs work)](https://www.drupal.org/project/drupal/issues/2915762) ;  [508 Compliance - Tooltips not displayed for keyboard navigation (drupal:2933984, Active)](https://www.drupal.org/project/drupal/issues/2933984) ;  [Re-evaluate whether Contextual Links are the best interaction for configuring… (drupal:3042516, Active)](https://www.drupal.org/project/drupal/issues/3042516)   All issue references:  [2.1.1 reference list](#ref-2-1-1) |
| [2.1.2 No Keyboard Trap](https://www.w3.org/TR/WCAG22/#no-keyboard-trap) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may encounter a keyboard trap when accessing a toolbar sub-menu, making it difficult to navigate away without using a mouse.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Active: 1. Target evidence states: unknown: 1.   Examples:  [Accessing a toolbar sub-menu seems to result in a keyboard trap (drupal:3559162, Active)](https://www.drupal.org/project/drupal/issues/3559162)   All issue references:  [2.1.2 reference list](#ref-2-1-2) |
| [2.1.4 Character Key Shortcuts](https://www.w3.org/TR/WCAG22/#character-key-shortcuts) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may face barriers if they rely on keyboard navigation, as Drupal core lacks an API for hotkeys, potentially making navigation less accessible.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Active: 1. Target evidence states: unknown: 1.   Examples:  [Add an API for hotkeys to Drupal core (drupal:3532392, Active)](https://www.drupal.org/project/drupal/issues/3532392)   All issue references:  [2.1.4 reference list](#ref-2-1-4) |
| [2.2.1 Timing Adjustable](https://www.w3.org/TR/WCAG22/#timing-adjustable) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.2.2 Pause, Stop, Hide](https://www.w3.org/TR/WCAG22/#pause-stop-hide) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users with motion sensitivity may experience disorientation or seizures due to animations that do not respect their preference for reduced motion.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Active: 1. Target evidence states: unknown: 1.   Examples:  [[policy, no patch] Use "prefers-reduced-motion" media query to disable animat… (drupal:2928103, Active)](https://www.drupal.org/project/drupal/issues/2928103)   All issue references:  [2.2.2 reference list](#ref-2-2-2) |
| [2.3.1 Three Flashes or Below Threshold](https://www.w3.org/TR/WCAG22/#three-flashes-or-below-threshold) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users with motion sensitivity may encounter animations that trigger their symptoms, as the site does not use the 'prefers-reduced-motion' media query to disable animations.   Authoring Tool:  No issues classified for authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Active: 1. Target evidence states: unknown: 1.   Examples:  [[policy, no patch] Use "prefers-reduced-motion" media query to disable animat… (drupal:2928103, Active)](https://www.drupal.org/project/drupal/issues/2928103)   All issue references:  [2.3.1 reference list](#ref-2-3-1) |
| [2.4.1 Bypass Blocks](https://www.w3.org/TR/WCAG22/#bypass-blocks) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may encounter broken link anchors for form elements with validation errors, making it difficult to navigate to specific error messages.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 1 detailed, 0 metadata-only inventory. Tracker statuses: Needs review: 1. Target evidence states: likely-affected: 1.   Examples:  [Use $element['#attributes]['id'] instead of $element['#id'] to create a link… (drupal:3557245, Needs review)](https://www.drupal.org/project/drupal/issues/3557245)   All issue references:  [2.4.1 reference list](#ref-2-4-1) |
| [2.4.2 Page Titled](https://www.w3.org/TR/WCAG22/#page-titled) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle with understanding page titles that lack context, making it hard to orient themselves within the site structure.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  2 active issues tagged to this criterion: 0 detailed, 2 metadata-only inventory. Tracker statuses: Needs work: 2. Target evidence states: unknown: 2.   Examples:  [Allow global tokens (and therefore page numbers) in display title (drupal:2509716, Needs work)](https://www.drupal.org/project/drupal/issues/2509716) ;  [Page title should contextualize the local navigation (drupal:3370946, Needs work)](https://www.drupal.org/project/drupal/issues/3370946)   All issue references:  [2.4.2 reference list](#ref-2-4-2) |
| [2.4.3 Focus Order](https://www.w3.org/TR/WCAG22/#focus-order) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may face issues with focus management, such as controls within hidden content becoming focusable, and losing focus when interacting with certain elements like table headers or off-canvas dialogs.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  9 active issues tagged to this criterion: 0 detailed, 9 metadata-only inventory. Tracker statuses: Active: 9. Target evidence states: unknown: 9.   Examples:  [Make sure controls within hidden content are not focusable (drupal:2925295, Active)](https://www.drupal.org/project/drupal/issues/2925295) ;  [When enabling or disabling a block, don't move the focus to the top of the page (drupal:2973114, Active)](https://www.drupal.org/project/drupal/issues/2973114) ;  [Return focus to point of action when the off-canvas dialog closes (drupal:3019849, Active)](https://www.drupal.org/project/drupal/issues/3019849)   All issue references:  [2.4.3 reference list](#ref-2-4-3) |
| [2.4.4 Link Purpose (In Context)](https://www.w3.org/TR/WCAG22/#link-purpose-in-context) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle with links like "Add new comment" and "@count comments" due to lack of descriptive text, hindering understanding and navigation.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  2 active issues tagged to this criterion: 0 detailed, 2 metadata-only inventory. Tracker statuses: Needs work: 2. Target evidence states: unknown: 2.   Examples:  ["Add new comment" and "@count comments" links are not following accessibility… (drupal:2922435, Needs work)](https://www.drupal.org/project/drupal/issues/2922435) ;  [Make the link descriptions more descriptive, helpful, and clear. (drupal:3439721, Needs work)](https://www.drupal.org/project/drupal/issues/3439721)   All issue references:  [2.4.4 reference list](#ref-2-4-4) |
| [2.5.1 Pointer Gestures](https://www.w3.org/TR/WCAG22/#pointer-gestures) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Reported web barriers include: Research accessibility of drag-and-drop grid interfaces.; Modernize tabledrag accessibility..   Authoring Tool:  No authoring-classified issue is tagged in this snapshot; the Authoring Tool result is proposed from the overall issue queue and needs review.   Evidence:  2 active issues tagged to this criterion: 0 detailed, 2 metadata-only inventory. Tracker statuses: Active: 2. Target evidence states: unknown: 2.   Examples:  [Research accessibility of drag-and-drop grid interfaces. (drupal:2920006, Active)](https://www.drupal.org/project/drupal/issues/2920006) ;  [Modernize tabledrag accessibility. (drupal:3027229, Active)](https://www.drupal.org/project/drupal/issues/3027229)   All issue references:  [2.5.1 reference list](#ref-2-5-1) |
| [2.5.2 Pointer Cancellation](https://www.w3.org/TR/WCAG22/#pointer-cancellation) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may face issues with right-click functionality and JavaScript behaviors, particularly with Ajax submissions and pointer cancellation, hindering their ability to interact with the site effectively.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  4 active issues tagged to this criterion: 0 detailed, 4 metadata-only inventory. Tracker statuses: Active: 1, Needs work: 3. Target evidence states: unknown: 4.   Examples:  [Right click should not submit buttons with Ajax behaviors (drupal:2616184, Needs work)](https://www.drupal.org/project/drupal/issues/2616184) ;  [Assess JavaScript behaviours for WCAG 2.1 Pointer Cancellation (drupal:2958654, Needs work)](https://www.drupal.org/project/drupal/issues/2958654) ;  [Replace javascript event listeners which use "down" events in the ajax component (drupal:2960840, Active)](https://www.drupal.org/project/drupal/issues/2960840)   All issue references:  [2.5.2 reference list](#ref-2-5-2) |
| [2.5.3 Label in Name](https://www.w3.org/TR/WCAG22/#label-in-name) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle with links and buttons that lack sufficient context, especially when using speech recognition. For example, the 'Extend' button in the navigation menu has an accessible name that starts with 'Extend' rather than the visible label, potentially causing mismatches in commands.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  9 active issues tagged to this criterion: 1 detailed, 8 metadata-only inventory. Tracker statuses: Active: 6, Needs review: 1, Needs work: 2. Target evidence states: likely-affected: 1, unknown: 8.   Examples:  [Link labels generated by the Entity List Builder should provide more context… (drupal:2960828, Needs work)](https://www.drupal.org/project/drupal/issues/2960828) ;  [Provide better context in accessible names of EntityOperation views plugin dr… (drupal:2973124, Needs work)](https://www.drupal.org/project/drupal/issues/2973124) ;  [Assess Drupal core for WCAG success criterion 2.5.3 Label in Name (drupal:3015239, Active)](https://www.drupal.org/project/drupal/issues/3015239)   All issue references:  [2.5.3 reference list](#ref-2-5-3) |
| [2.5.4 Motion Actuation](https://www.w3.org/TR/WCAG22/#motion-actuation) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.1.1 Language of Page](https://www.w3.org/TR/WCAG22/#language-of-page) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.2.1 On Focus](https://www.w3.org/TR/WCAG22/#on-focus) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle with redundant aural interfaces and jumpy focus in select fields, affecting navigation and interaction. Keyboard users might also lose focus when selecting table headers.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  3 active issues tagged to this criterion: 0 detailed, 3 metadata-only inventory. Tracker statuses: Active: 3. Target evidence states: unknown: 3.   Examples:  [Redundant aural interface and the general interaction with CKEditor toolbar c… (drupal:3506324, Active)](https://www.drupal.org/project/drupal/issues/3506324) ;  [Selecting a column in a table header by keyboard drops the focus (drupal:3506339, Active)](https://www.drupal.org/project/drupal/issues/3506339) ;  [Select field in modal dialog has jumpy focus (drupal:3611769, Active)](https://www.drupal.org/project/drupal/issues/3611769)   All issue references:  [3.2.1 reference list](#ref-3-2-1) |
| [3.2.2 On Input](https://www.w3.org/TR/WCAG22/#on-input) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.2.6 Consistent Help](https://www.w3.org/TR/WCAG22/#consistent-help) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.3.1 Error Identification](https://www.w3.org/TR/WCAG22/#error-identification) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may encounter issues with file uploads lacking progress indicators, form validation errors not being properly announced, and server-side validation causing focus and screen reader problems. Screen reader users might also miss inline errors and media library widget errors.   Authoring Tool:  No issues are classified for the authoring tool.   Evidence:  18 active issues tagged to this criterion: 2 detailed, 16 metadata-only inventory. Tracker statuses: Active: 4, Needs review: 1, Needs work: 13. Target evidence states: likely-affected: 2, unknown: 16.   Examples:  [The file upload field needs a progress indicator that expresses to screen rea… (drupal:2089703, Needs work)](https://www.drupal.org/project/drupal/issues/2089703) ;  [Error highlighting and reporting problems for the current password on the use… (drupal:2455933, Needs work)](https://www.drupal.org/project/drupal/issues/2455933) ;  [Inline Errors not shown for container elements (drupal:2560467, Needs work)](https://www.drupal.org/project/drupal/issues/2560467)   All issue references:  [3.3.1 reference list](#ref-3-3-1) |
| [3.3.2 Labels or Instructions](https://www.w3.org/TR/WCAG22/#labels-or-instructions) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle with form elements on grouped exposed filters lacking accessible names, inconsistent field labeling, and unclear required field indicators. CKEditor 5 text areas also lack appropriate aria-labels for screen readers.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  7 active issues tagged to this criterion: 0 detailed, 7 metadata-only inventory. Tracker statuses: Active: 2, Needs work: 5. Target evidence states: unknown: 7.   Examples:  [Elements on grouped exposed filters configuration form are missing accessible… (drupal:2608212, Needs work)](https://www.drupal.org/project/drupal/issues/2608212) ;  [[Meta] Set the required state for all fields in Core in the Accessibility Obj… (drupal:2852874, Active)](https://www.drupal.org/project/drupal/issues/2852874) ;  [Admin list filter fields are inconsistently labelled. (drupal:2942037, Active)](https://www.drupal.org/project/drupal/issues/2942037)   All issue references:  [3.3.2 reference list](#ref-3-3-2) |
| [3.3.7 Redundant Entry](https://www.w3.org/TR/WCAG22/#redundant-entry) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [4.1.1 Parsing](https://www.w3.org/TR/WCAG22/#parsing) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [4.1.2 Name, Role, Value](https://www.w3.org/TR/WCAG22/#name-role-value) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may encounter issues with duplicate IDs, missing accessible names, and incorrect ARIA roles, hindering navigation and understanding of web content. Screen readers may struggle with dynamic changes and missing title attributes on buttons.   Authoring Tool:  Authors might face challenges with improperly structured pagers, leading to accessibility issues. Ensuring lists contain only allowed elements like <li> is crucial for correct list structure.   Evidence:  39 active issues tagged to this criterion: 2 detailed, 37 metadata-only inventory. Tracker statuses: Active: 17, Needs review: 1, Needs work: 21. Target evidence states: likely-affected: 2, unknown: 37.   Examples:  [Allow modules to classify blocks when defining them, so WAI-ARIA roles can au… (drupal:1402250, Needs work)](https://www.drupal.org/project/drupal/issues/1402250) ;  [Cached render elements can have duplicate HTML IDs (drupal:1852090, Needs work)](https://www.drupal.org/project/drupal/issues/1852090) ;  [Add "changed" hints to translation settings page (drupal:1854046, Needs work)](https://www.drupal.org/project/drupal/issues/1854046)   All issue references:  [4.1.2 reference list](#ref-4-1-2) |

## WCAG 2.2 Level AA criteria

**Table 2: Success Criteria, Level AA**

| Criteria | Conformance Level | Remarks and Explanations |
| --- | --- | --- |
| [1.2.4 Captions (Live)](https://www.w3.org/TR/WCAG22/#captions-live) | Web: Not Applicable; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Applicable | All components: Not Applicable for Drupal Core. Drupal Core does not provide live audio/video. Proposed Not Applicable for Core; evaluate the contrib Video or AblePlayer modules separately. |
| [1.2.5 Audio Description (Prerecorded)](https://www.w3.org/TR/WCAG22/#audio-description-prerecorded) | Web: Not Applicable; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Applicable | All components: Not Applicable for Drupal Core. Drupal Core does not provide a video player or audio-description feature. Proposed Not Applicable for Core; audio/video caption and description support belongs to contrib Video or AblePlayer. |
| [1.3.4 Orientation](https://www.w3.org/TR/WCAG22/#orientation) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may face issues with missing site manifest, hindering proper functioning of assistive technologies.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: unknown: 1.   Examples:  [Extend site information page to generate a manifest.json file (drupal:2698127, Needs work)](https://www.drupal.org/project/drupal/issues/2698127)   All issue references:  [1.3.4 reference list](#ref-1-3-4) |
| [1.3.5 Identify Input Purpose](https://www.w3.org/TR/WCAG22/#identify-input-purpose) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users with screen readers may face issues with autocomplete functionality, as the IME enhancement in Android stops autocomplete search events when typing English words.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  2 active issues tagged to this criterion: 0 detailed, 2 metadata-only inventory. Tracker statuses: Needs work: 2. Target evidence states: unknown: 2.   Examples:  [IME enhancement stops autocomplete search event in Android when typing an Eng… (drupal:2928820, Needs work)](https://www.drupal.org/project/drupal/issues/2928820) ;  [Provide a new library to replace jQuery UI autocomplete (drupal:3076171, Needs work)](https://www.drupal.org/project/drupal/issues/3076171)   All issue references:  [1.3.5 reference list](#ref-1-3-5) |
| [1.4.3 Contrast (Minimum)](https://www.w3.org/TR/WCAG22/#visual-audio-contrast-contrast) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.4.4 Resize text](https://www.w3.org/TR/WCAG22/#visual-audio-contrast-scale) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users with visual impairments may struggle with the indentation in hierarchical select lists, making it difficult to understand the structure.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: unknown: 1.   Examples:  [Improve indentation in hierarchical select lists (drupal:2384203, Needs work)](https://www.drupal.org/project/drupal/issues/2384203)   All issue references:  [1.4.4 reference list](#ref-1-4-4) |
| [1.4.5 Images of Text](https://www.w3.org/TR/WCAG22/#visual-audio-contrast-text-presentation) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.4.10 Reflow](https://www.w3.org/TR/WCAG22/#reflow) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle with dialogues and table content visibility when fully zoomed, and find it difficult to access action links on small screens.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  4 active issues tagged to this criterion: 0 detailed, 4 metadata-only inventory. Tracker statuses: Active: 2, Needs work: 2. Target evidence states: unknown: 4.   Examples:  [Dialogs sub-optimal when fully zoomed (drupal:2234745, Active)](https://www.drupal.org/project/drupal/issues/2234745) ;  [Add another responsive tables solution that doesn't hide content (drupal:2280035, Needs work)](https://www.drupal.org/project/drupal/issues/2280035) ;  [Re-wrap text in views interface when zooming in mobile (drupal:2313471, Active)](https://www.drupal.org/project/drupal/issues/2313471)   All issue references:  [1.4.10 reference list](#ref-1-4-10) |
| [1.4.11 Non-text Contrast](https://www.w3.org/TR/WCAG22/#non-text-contrast) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Reported web barriers include: Add new Splitbutton render element to eventually replace Dropbutton; Refine the layout selection UI; Improve icon color contrast for WCAG 2.1.   Authoring Tool:  Reported authoring barriers include: Expose triggering update of media metadata + thumbnail to end users; The active primary local task has a too low color contrast and shapeshifting compared to the….   Evidence:  17 active issues tagged to this criterion: 5 detailed, 12 metadata-only inventory. Tracker statuses: Active: 10, Needs review: 3, Needs work: 4. Target evidence states: likely-affected: 1, unknown: 16.   Examples:  [Add new Splitbutton render element to eventually replace Dropbutton (drupal:1899236, Needs work)](https://www.drupal.org/project/drupal/issues/1899236) ;  [Refine the layout selection UI (drupal:2848549, Active)](https://www.drupal.org/project/drupal/issues/2848549) ;  [Improve icon color contrast for WCAG 2.1 (drupal:2910102, Active)](https://www.drupal.org/project/drupal/issues/2910102)   All issue references:  [1.4.11 reference list](#ref-1-4-11) |
| [1.4.12 Text Spacing](https://www.w3.org/TR/WCAG22/#text-spacing) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may encounter an accessibility issue where page titles are truncated with an ellipsis, potentially making them unclear.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Active: 1. Target evidence states: unknown: 1.   Examples:  [Page title ellipsis accessibility issue (drupal:3623836, Active)](https://www.drupal.org/project/drupal/issues/3623836)   All issue references:  [1.4.12 reference list](#ref-1-4-12) |
| [1.4.13 Content on Hover or Focus](https://www.w3.org/TR/WCAG22/#content-on-hover-or-focus) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users with visual disabilities may struggle to find and access submenu items in the footer due to their distance from top-level menu items.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: unknown: 1.   Examples:  [Top-level menu items in the footer region are too far away from their submenu… (drupal:3531948, Needs work)](https://www.drupal.org/project/drupal/issues/3531948)   All issue references:  [1.4.13 reference list](#ref-1-4-13) |
| [2.4.5 Multiple Ways](https://www.w3.org/TR/WCAG22/#multiple-ways) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.4.6 Headings and Labels](https://www.w3.org/TR/WCAG22/#headings-and-labels) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle with visually-hidden block titles, misordered headings, and unclear local navigation, hindering understanding and navigation.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  4 active issues tagged to this criterion: 0 detailed, 4 metadata-only inventory. Tracker statuses: Active: 1, Needs work: 3. Target evidence states: unknown: 4.   Examples:  [Add option for visually-hidden block titles (drupal:2614950, Needs work)](https://www.drupal.org/project/drupal/issues/2614950) ;  [Allow wrapping field labels in a heading tag (drupal:3277785, Needs work)](https://www.drupal.org/project/drupal/issues/3277785) ;  [[ATAG] Text editor should alert user when headings are out of order (drupal:3293673, Active)](https://www.drupal.org/project/drupal/issues/3293673)   All issue references:  [2.4.6 reference list](#ref-2-4-6) |
| [2.4.7 Focus Visible](https://www.w3.org/TR/WCAG22/#focus-visible) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may encounter issues with improperly accessible tooltips, sticky table headers without un-sticky options, and visually hidden labels with links causing focus problems. Errors in link anchors can lead to incorrect navigation. Sidebar logo links sometimes lack focus indicators.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  7 active issues tagged to this criterion: 1 detailed, 6 metadata-only inventory. Tracker statuses: Active: 3, Needs review: 1, Needs work: 3. Target evidence states: likely-affected: 1, unknown: 6.   Examples:  [Build API to Replace Links using Title Attributes with Proper Accessible, The… (drupal:1919940, Needs work)](https://www.drupal.org/project/drupal/issues/1919940) ;  [Add option to un-sticky table headers to benefit assistive tech users (drupal:3163765, Needs work)](https://www.drupal.org/project/drupal/issues/3163765) ;  [[drupalImage] Scroll to last image when uploading multiple images (drupal:3272493, Active)](https://www.drupal.org/project/drupal/issues/3272493)   All issue references:  [2.4.7 reference list](#ref-2-4-7) |
| [2.4.11 Focus Not Obscured (Minimum)](https://www.w3.org/TR/WCAG22/#focus-not-obscured-minimum) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may face issues with focus styles in CKEditor 5, as it uses its own styles instead of the admin theme's, and top-level menus can obscure focused items in the sidebar, causing confusion.   Authoring Tool:  No issues classified for authoring tool.   Evidence:  2 active issues tagged to this criterion: 0 detailed, 2 metadata-only inventory. Tracker statuses: Active: 1, Needs work: 1. Target evidence states: unknown: 2.   Examples:  [CKEditor 5 has its own focus styles, should use the admin theme's (e.g. Claro's) (drupal:3272592, Needs work)](https://www.drupal.org/project/drupal/issues/3272592) ;  [Some top-level menus obscure unrelated focused items in sidebar (drupal:3573225, Active)](https://www.drupal.org/project/drupal/issues/3573225)   All issue references:  [2.4.11 reference list](#ref-2-4-11) |
| [2.5.7 Dragging Movements](https://www.w3.org/TR/WCAG22/#dragging-movements) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.5.8 Target Size (Minimum)](https://www.w3.org/TR/WCAG22/#target-size-minimum) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may face difficulty selecting all checkboxes one by one, leading to poor user experience.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 1 detailed, 0 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: likely-affected: 1.   Examples:  [Add a '#select_all' option for checkboxes element (drupal:3459246, Needs work)](https://www.drupal.org/project/drupal/issues/3459246)   All issue references:  [2.5.8 reference list](#ref-2-5-8) |
| [3.1.2 Language of Parts](https://www.w3.org/TR/WCAG22/#language-of-parts) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may encounter issues with language tagging, leading to content not being properly marked. This can affect screen reader users who rely on language cues.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  9 active issues tagged to this criterion: 0 detailed, 9 metadata-only inventory. Tracker statuses: Active: 6, Needs work: 3. Target evidence states: unknown: 9.   Examples:  [Views containing content not in the page's language need to add tags which ma… (drupal:2496223, Active)](https://www.drupal.org/project/drupal/issues/2496223) ;  [DateList and date range inline form errors are repeated (drupal:2827034, Needs work)](https://www.drupal.org/project/drupal/issues/2827034) ;  [Links in language switcher block do not conform to WCAG language-of-parts (drupal:3020305, Needs work)](https://www.drupal.org/project/drupal/issues/3020305)   All issue references:  [3.1.2 reference list](#ref-3-1-2) |
| [3.2.3 Consistent Navigation](https://www.w3.org/TR/WCAG22/#consistent-navigation) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle with inconsistent admin list filters and encounter scrolling issues when adding blocks via layout builder.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  3 active issues tagged to this criterion: 0 detailed, 3 metadata-only inventory. Tracker statuses: Active: 1, Needs work: 2. Target evidence states: unknown: 3.   Examples:  [Modules uninstall filter does not filter by machine name (drupal:2895388, Needs work)](https://www.drupal.org/project/drupal/issues/2895388) ;  [Make admin list filters behave more consistently. (drupal:3015494, Active)](https://www.drupal.org/project/drupal/issues/3015494) ;  [Scrolling problems when adding a block via layout builder (drupal:3209129, Needs work)](https://www.drupal.org/project/drupal/issues/3209129)   All issue references:  [3.2.3 reference list](#ref-3-2-3) |
| [3.2.4 Consistent Identification](https://www.w3.org/TR/WCAG22/#consistent-identification) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.3.3 Error Suggestion](https://www.w3.org/TR/WCAG22/#error-suggestion) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may encounter a barrier where error links from Inline Form Errors do not open the sidebar in Default Admin mode, preventing them from accessing invalid fields.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 1 detailed, 0 metadata-only inventory. Tracker statuses: Needs review: 1. Target evidence states: likely-affected: 1.   Examples:  [Forms sidebar doesn't open with error links from Inline Form Errors module (drupal:3619127, Needs review)](https://www.drupal.org/project/drupal/issues/3619127)   All issue references:  [3.3.3 reference list](#ref-3-3-3) |
| [3.3.4 Error Prevention (Legal, Financial, Data)](https://www.w3.org/TR/WCAG22/#error-prevention-legal-financial-data) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.3.8 Accessible Authentication (Minimum)](https://www.w3.org/TR/WCAG22/#accessible-authentication-minimum) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [4.1.3 Status Messages](https://www.w3.org/TR/WCAG22/#status-messages) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may face issues with dropbutton states not being reported to assistive technologies, and AJAX progress messages not being conveyed to screen readers. View changes and status messages also lack proper accessibility labels.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  6 active issues tagged to this criterion: 1 detailed, 5 metadata-only inventory. Tracker statuses: Active: 3, Needs review: 1, Needs work: 2. Target evidence states: likely-affected: 1, unknown: 5.   Examples:  [Dropbutton should report open/closed state to assistive technology (drupal:2893663, Active)](https://www.drupal.org/project/drupal/issues/2893663) ;  [After enabling or disabling a view, convey changes to screen reader users. (drupal:2973116, Active)](https://www.drupal.org/project/drupal/issues/2973116) ;  [Convey AJAX progress messages to assistive technology. (drupal:2973140, Needs review)](https://www.drupal.org/project/drupal/issues/2973140)   All issue references:  [4.1.3 reference list](#ref-4-1-3) |

## WCAG 2.2 Level AAA criteria

**Table 3: Success Criteria, Level AAA**

| Criteria | Conformance Level | Remarks and Explanations |
| --- | --- | --- |
| [1.2.6 Sign Language (Prerecorded)](https://www.w3.org/TR/WCAG22/#sign-language-prerecorded) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.2.7 Extended Audio Description (Prerecorded)](https://www.w3.org/TR/WCAG22/#extended-audio-description-prerecorded) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.2.8 Media Alternative (Prerecorded)](https://www.w3.org/TR/WCAG22/#media-alternative-prerecorded) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.2.9 Audio-only (Live)](https://www.w3.org/TR/WCAG22/#audio-only-live) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.3.6 Identify Purpose](https://www.w3.org/TR/WCAG22/#identify-purpose) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.4.6 Contrast (Enhanced)](https://www.w3.org/TR/WCAG22/#contrast-enhanced) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.4.7 Low or No Background Audio](https://www.w3.org/TR/WCAG22/#low-or-no-background-audio) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.4.8 Visual Presentation](https://www.w3.org/TR/WCAG22/#visual-presentation) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [1.4.9 Images of Text (No Exception)](https://www.w3.org/TR/WCAG22/#images-of-text-no-exception) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.1.3 Keyboard (No Exception)](https://www.w3.org/TR/WCAG22/#keyboard-no-exception) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.2.3 No Timing](https://www.w3.org/TR/WCAG22/#no-timing) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.2.4 Interruptions](https://www.w3.org/TR/WCAG22/#interruptions) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.2.5 Re-authenticating](https://www.w3.org/TR/WCAG22/#re-authenticating) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.2.6 Timeouts](https://www.w3.org/TR/WCAG22/#timeouts) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.3.2 Three Flashes](https://www.w3.org/TR/WCAG22/#three-flashes) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.3.3 Animation from Interactions](https://www.w3.org/TR/WCAG22/#animation-from-interactions) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.4.8 Location](https://www.w3.org/TR/WCAG22/#location) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.4.9 Link Purpose (Link Only)](https://www.w3.org/TR/WCAG22/#link-purpose-link-only) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may struggle to understand the purpose of links on the available updates page without descriptive link text.   Authoring Tool:  No issues classified for the authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: unknown: 1.   Examples:  [Improve link text on available updates page to address WCAG SC 2.4.9 Link pur… (drupal:3080853, Needs work)](https://www.drupal.org/project/drupal/issues/3080853)   All issue references:  [2.4.9 reference list](#ref-2-4-9) |
| [2.4.10 Section Headings](https://www.w3.org/TR/WCAG22/#section-headings) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.4.12 Focus Not Obscured (Enhanced)](https://www.w3.org/TR/WCAG22/#focus-not-obscured-enhanced) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.4.13 Focus Appearance](https://www.w3.org/TR/WCAG22/#focus-appearance) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may face issues with focus styles in CKEditor 5, as it uses its own styles instead of the admin theme's, potentially causing confusion.   Authoring Tool:  No issues classified for authoring tool.   Evidence:  1 active issue tagged to this criterion: 0 detailed, 1 metadata-only inventory. Tracker statuses: Needs work: 1. Target evidence states: unknown: 1.   Examples:  [CKEditor 5 has its own focus styles, should use the admin theme's (e.g. Claro's) (drupal:3272592, Needs work)](https://www.drupal.org/project/drupal/issues/3272592)   All issue references:  [2.4.13 reference list](#ref-2-4-13) |
| [2.5.5 Target Size (Enhanced)](https://www.w3.org/TR/WCAG22/#target-size-enhanced) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [2.5.6 Concurrent Input Mechanisms](https://www.w3.org/TR/WCAG22/#concurrent-input-mechanisms) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.1.3 Unusual Words](https://www.w3.org/TR/WCAG22/#unusual-words) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.1.4 Abbreviations](https://www.w3.org/TR/WCAG22/#abbreviations) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.1.5 Reading Level](https://www.w3.org/TR/WCAG22/#reading-level) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.1.6 Pronunciation](https://www.w3.org/TR/WCAG22/#pronunciation) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.2.5 Change on Request](https://www.w3.org/TR/WCAG22/#change-on-request) | Web: Partially Supports; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Partially Supports | Web:  Users may encounter issues as the jQuery UI dialog is being deprecated, requiring a transition to a native dialog element. This change aims to improve accessibility but may initially cause confusion or errors until fully implemented.   Authoring Tool:  No issues classified for the authoring tool related to this change.   Evidence:  1 active issue tagged to this criterion: 1 detailed, 0 metadata-only inventory. Tracker statuses: Needs review: 1. Target evidence states: likely-affected: 1.   Examples:  [Add a native dialog element using HTMX to deprecate the jQuery UI dialog (drupal:2158943, Needs review)](https://www.drupal.org/project/drupal/issues/2158943)   All issue references:  [3.2.5 reference list](#ref-3-2-5) |
| [3.3.5 Help](https://www.w3.org/TR/WCAG22/#help) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.3.6 Error Prevention (All)](https://www.w3.org/TR/WCAG22/#error-prevention-all) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |
| [3.3.9 Accessible Authentication (Enhanced)](https://www.w3.org/TR/WCAG22/#accessible-authentication-enhanced) | Web: Not Evaluated; Electronic Documents: Not Applicable; Software: Not Applicable; Authoring Tool: Not Evaluated | Web: No active tagged issue; remains Not Evaluated. Authoring Tool: No active tagged issue; remains Not Evaluated. Evidence: No active tagged issue in this snapshot. |

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
- Record scope and wording notes in context/DRUPAL.md (or the matching product context file); context is not evidence.
- Open ./index.html#issues and review the active issue evidence.
- For inventory records, read the source issue and collect the missing comments, merge requests and target evidence.
- Verify each criterion against the installed product; do not treat an issue count as a severity or percentage.
- Complete the reviewer name, organization and approval record outside this generated draft.
- Replace every Not Evaluated result with a reviewed ACR result, or record the remaining evaluation gap.
- Confirm the proposed Partially Supports results for issue-tagged criteria or record why the queue evidence is insufficient.
- Remove the draft status only after independent review and sign-off.

## Limitations

- This is an issue-queue evidence narrative, not a WCAG-EM sample or a conformance test.
- Fixed and closed issues are excluded by policy; their absence is not evidence that a barrier is gone.
- The 398 inventory records have no comments/MRs/commit analysis; they are included for completeness, not as finished findings.
- No reproduction, assistive-technology testing, hardware testing or packaged-software testing is claimed.
- The product is a declared Drupal Core configuration; it is not every Drupal site.
- The draft does not establish legal compliance or a procurement-safe conformance claim.

## References

Every Drupal.org issue cited in the criterion tables is listed below by criterion. Each link goes to the public issue where the barrier is discussed.

### 1.1.1 — Non-text Content

- [drupal:2780293 — Add GUI to configure the site's logo alt attribute (Needs work)](https://www.drupal.org/project/drupal/issues/2780293)
- [drupal:2921627 — Do not use a CSS-only required marker in forms per WCAG 2.0 (Needs work)](https://www.drupal.org/project/drupal/issues/2921627)
- [drupal:2960415 — Media alt text not available in Views (Active)](https://www.drupal.org/project/drupal/issues/2960415)
- [drupal:2986117 — Find a way to differentiate different media types in the administrative media library grid view (Active)](https://www.drupal.org/project/drupal/issues/2986117)
- [drupal:3050928 — Allow content authors to define location for long description in CKEditor image plugin (Active)](https://www.drupal.org/project/drupal/issues/3050928)
- [drupal:3087535 — In WYSIWYG embed modal for existing images, the alt text field should have a default value instead of placeholder text (Needs work)](https://www.drupal.org/project/drupal/issues/3087535)
- [drupal:3171916 — Add Help for Image Fields (Active)](https://www.drupal.org/project/drupal/issues/3171916)
- [drupal:3230231 — image field alt help/description should distinguish between decorative & meaningful images (Active)](https://www.drupal.org/project/drupal/issues/3230231)
- [drupal:3232414 — Image Media thumbnail alt text cannot be changed without reuploading the image (Needs work)](https://www.drupal.org/project/drupal/issues/3232414)
- [drupal:3272325 — Password suggestions are hidden from screenreaders (Needs work)](https://www.drupal.org/project/drupal/issues/3272325)
- [drupal:3304479 — Improve accessibility of layout preview icons (Active)](https://www.drupal.org/project/drupal/issues/3304479)
- [drupal:3444209 — [Regression] Password recommendations are not being announced to screenreader users (Active)](https://www.drupal.org/project/drupal/issues/3444209)

### 1.2.2 — Captions (Prerecorded)

- [drupal:3002770 — Provide authors with tools to manage transcripts and captions/subtitles for local video and audio (Active)](https://www.drupal.org/project/drupal/issues/3002770)
- [drupal:3056714 — Provide a FieldType and FieldWidget to represent a WebVTT file for the HTML track element (Needs work)](https://www.drupal.org/project/drupal/issues/3056714)
- [drupal:3057144 — Update audio and video file field formatters to include track elements (Needs work)](https://www.drupal.org/project/drupal/issues/3057144)

### 1.3.1 — Info and Relationships

- [drupal:1383696 — Allow a custom HTML element to be selected for a grouping field (Needs work)](https://www.drupal.org/project/drupal/issues/1383696)
- [drupal:2443815 — #description_display broken for details elements (Needs work)](https://www.drupal.org/project/drupal/issues/2443815)
- [drupal:2852874 — [Meta] Set the required state for all fields in Core in the Accessibility Object Model (AOM) (Active)](https://www.drupal.org/project/drupal/issues/2852874)
- [drupal:2921627 — Do not use a CSS-only required marker in forms per WCAG 2.0 (Needs work)](https://www.drupal.org/project/drupal/issues/2921627)
- [drupal:2937640 — Umami theme ignores placeholders and HTML replaced elements when checking for empty regions (Needs work)](https://www.drupal.org/project/drupal/issues/2937640)
- [drupal:2942404 — System messages should be accessible (Needs work)](https://www.drupal.org/project/drupal/issues/2942404)
- [drupal:2951317 — Radios element missing "required" attribute (Needs work)](https://www.drupal.org/project/drupal/issues/2951317)
- [drupal:3037446 — Forms with required fields marked by asterisk do not have text explaining what the asterisk means (Needs work)](https://www.drupal.org/project/drupal/issues/3037446)
- [drupal:3037625 — Duplicate label field when adding field w/o JS (Needs work)](https://www.drupal.org/project/drupal/issues/3037625)
- [drupal:3037725 — Convey successful outcome of add-section operation via assitive tech (Active)](https://www.drupal.org/project/drupal/issues/3037725)
- [drupal:3037726 — Convey successful outcome of add-block operation via assitive tech (Active)](https://www.drupal.org/project/drupal/issues/3037726)
- [drupal:3037730 — Convey outcome of remove-block operation via assistive tech (Active)](https://www.drupal.org/project/drupal/issues/3037730)
- [drupal:3037733 — Convey outcome of remove-section operation via assistive tech (Active)](https://www.drupal.org/project/drupal/issues/3037733)
- [drupal:3078334 — Datetime and Datelist elements should render as fieldsets (Needs work)](https://www.drupal.org/project/drupal/issues/3078334)
- [drupal:3081500 — Accessibility bugs with vertical tabs (Needs work)](https://www.drupal.org/project/drupal/issues/3081500)
- [drupal:3098857 — "drupal-live-announce" is not contained in a landmark. (Needs work)](https://www.drupal.org/project/drupal/issues/3098857)
- [drupal:3283883 — Fieldset should not create title element when title is empty (Needs work)](https://www.drupal.org/project/drupal/issues/3283883)
- [drupal:3296224 — Issues for Mac VoiceOver screenreader users when deleting characters in the comment subject field and using Safari (Active)](https://www.drupal.org/project/drupal/issues/3296224)
- [drupal:3301868 — Improve support for Voice Control with date fields (Active)](https://www.drupal.org/project/drupal/issues/3301868)
- [drupal:3348552 — Pager template fails accessibility tests for Ellipsis ("...") (Needs review)](https://www.drupal.org/project/drupal/issues/3348552)
- [drupal:3594809 — Use standard checkboxes on forms that require submission (Needs work)](https://www.drupal.org/project/drupal/issues/3594809)
- [drupal:3612047 — Empty table header on People admin page (Needs work)](https://www.drupal.org/project/drupal/issues/3612047)
- [drupal:893530 — Multi level (multirow) header for table FAPI element (Needs work)](https://www.drupal.org/project/drupal/issues/893530)

### 1.3.3 — Sensory Characteristics

- [drupal:3531948 — Top-level menu items in the footer region are too far away from their submenu items (Needs work)](https://www.drupal.org/project/drupal/issues/3531948)

### 1.3.4 — Orientation

- [drupal:2698127 — Extend site information page to generate a manifest.json file (Needs work)](https://www.drupal.org/project/drupal/issues/2698127)

### 1.3.5 — Identify Input Purpose

- [drupal:2928820 — IME enhancement stops autocomplete search event in Android when typing an English word (Needs work)](https://www.drupal.org/project/drupal/issues/2928820)
- [drupal:3076171 — Provide a new library to replace jQuery UI autocomplete (Needs work)](https://www.drupal.org/project/drupal/issues/3076171)

### 1.4.1 — Use of Color

- [drupal:2863052 — Style state select as a button bar (Active)](https://www.drupal.org/project/drupal/issues/2863052)
- [drupal:2975863 — Add an exposed filter to the Taxonomy overview view page (Needs work)](https://www.drupal.org/project/drupal/issues/2975863)
- [drupal:3038386 — Improve accessibility of Views table sortable columns (Needs work)](https://www.drupal.org/project/drupal/issues/3038386)
- [drupal:3059168 — Severity column icons on admin/reports/dblog are not accessible (Needs work)](https://www.drupal.org/project/drupal/issues/3059168)
- [drupal:3332668 — Tabledrag should provide quicker/smoother visual feedback when dragging (Needs work)](https://www.drupal.org/project/drupal/issues/3332668)
- [drupal:3426468 — Make the active menu item visually stand out more (Needs work)](https://www.drupal.org/project/drupal/issues/3426468)
- [drupal:867830 — "Unpublished" style of rendered entities is not accessible (and looks bad) (Active)](https://www.drupal.org/project/drupal/issues/867830)

### 1.4.10 — Reflow

- [drupal:2234745 — Dialogs sub-optimal when fully zoomed (Active)](https://www.drupal.org/project/drupal/issues/2234745)
- [drupal:2280035 — Add another responsive tables solution that doesn't hide content (Needs work)](https://www.drupal.org/project/drupal/issues/2280035)
- [drupal:2313471 — Re-wrap text in views interface when zooming in mobile (Active)](https://www.drupal.org/project/drupal/issues/2313471)
- [drupal:2574721 — Provide access to action links in the modules page on small screens (Needs work)](https://www.drupal.org/project/drupal/issues/2574721)

### 1.4.11 — Non-text Contrast

- [drupal:1899236 — Add new Splitbutton render element to eventually replace Dropbutton (Needs work)](https://www.drupal.org/project/drupal/issues/1899236)
- [drupal:2848549 — Refine the layout selection UI (Active)](https://www.drupal.org/project/drupal/issues/2848549)
- [drupal:2910102 — Improve icon color contrast for WCAG 2.1 (Active)](https://www.drupal.org/project/drupal/issues/2910102)
- [drupal:2975863 — Add an exposed filter to the Taxonomy overview view page (Needs work)](https://www.drupal.org/project/drupal/issues/2975863)
- [drupal:2983456 — Expose triggering update of media metadata + thumbnail to end users (Needs review)](https://www.drupal.org/project/drupal/issues/2983456)
- [drupal:3037742 — The toggle that makes Contextual Links visible at all times might not be sufficiently discoverable (Active)](https://www.drupal.org/project/drupal/issues/3037742)
- [drupal:3269342 — "Edit" cog icon for Field UI does not meet contrast minimums when in forced colors (Active)](https://www.drupal.org/project/drupal/issues/3269342)
- [drupal:3272592 — CKEditor 5 has its own focus styles, should use the admin theme's (e.g. Claro's) (Needs work)](https://www.drupal.org/project/drupal/issues/3272592)
- [drupal:3426468 — Make the active menu item visually stand out more (Needs work)](https://www.drupal.org/project/drupal/issues/3426468)
- [drupal:3631335 — The red accent color is too close to the error color (Active)](https://www.drupal.org/project/drupal/issues/3631335)
- [drupal:3634547 — [PP-1] Make CKEditor balloon tooltips respect Admin light or dark mode (Active)](https://www.drupal.org/project/drupal/issues/3634547)
- [drupal:3634562 — Media placeholder icons fail non-text contrast in the default admin theme's dark mode (Active)](https://www.drupal.org/project/drupal/issues/3634562)
- [drupal:3636027 — The active primary local task has a too low color contrast and shapeshifting compared to the active secondary local task (Needs review)](https://www.drupal.org/project/drupal/issues/3636027)
- [drupal:3636028 — The active accent color is not communicated (Needs review)](https://www.drupal.org/project/drupal/issues/3636028)
- [drupal:3636128 — In dark mode the switch component has a too low color contrast for most of the accent colors and is inconsistent to the light mode (Active)](https://www.drupal.org/project/drupal/issues/3636128)
- [drupal:3636143 — Regression: The toggle button border in the navigation sidebar has a too low color contrast in light mode (Active)](https://www.drupal.org/project/drupal/issues/3636143)
- [drupal:867830 — "Unpublished" style of rendered entities is not accessible (and looks bad) (Active)](https://www.drupal.org/project/drupal/issues/867830)

### 1.4.12 — Text Spacing

- [drupal:3623836 — Page title ellipsis accessibility issue (Active)](https://www.drupal.org/project/drupal/issues/3623836)

### 1.4.13 — Content on Hover or Focus

- [drupal:3531948 — Top-level menu items in the footer region are too far away from their submenu items (Needs work)](https://www.drupal.org/project/drupal/issues/3531948)

### 1.4.4 — Resize text

- [drupal:2384203 — Improve indentation in hierarchical select lists (Needs work)](https://www.drupal.org/project/drupal/issues/2384203)

### 2.1.1 — Keyboard

- [drupal:2915762 — Return to tab position when exiting dialog opened from contextual link (Needs work)](https://www.drupal.org/project/drupal/issues/2915762)
- [drupal:2933984 — 508 Compliance - Tooltips not displayed for keyboard navigation (Active)](https://www.drupal.org/project/drupal/issues/2933984)
- [drupal:3042516 — Re-evaluate whether Contextual Links are the best interaction for configuring/moving/deleting blocks in Layout Builder (Active)](https://www.drupal.org/project/drupal/issues/3042516)
- [drupal:3081515 — Add a new, accessible datepicker library to avoid using native browser datepickers for accessibility and consistency (Active)](https://www.drupal.org/project/drupal/issues/3081515)
- [drupal:3532392 — Add an API for hotkeys to Drupal core (Active)](https://www.drupal.org/project/drupal/issues/3532392)
- [drupal:3541688 — Focus does not move to submenu when opened by enter or space key (Active)](https://www.drupal.org/project/drupal/issues/3541688)
- [drupal:3541728 — Submenu opened with hover does not close by Escape key when another menu item has focus (Active)](https://www.drupal.org/project/drupal/issues/3541728)
- [drupal:3557245 — Use $element['#attributes]['id'] instead of $element['#id'] to create a link anchor (Needs review)](https://www.drupal.org/project/drupal/issues/3557245)

### 2.1.2 — No Keyboard Trap

- [drupal:3559162 — Accessing a toolbar sub-menu seems to result in a keyboard trap (Active)](https://www.drupal.org/project/drupal/issues/3559162)

### 2.1.4 — Character Key Shortcuts

- [drupal:3532392 — Add an API for hotkeys to Drupal core (Active)](https://www.drupal.org/project/drupal/issues/3532392)

### 2.2.2 — Pause, Stop, Hide

- [drupal:2928103 — [policy, no patch] Use "prefers-reduced-motion" media query to disable animations (Active)](https://www.drupal.org/project/drupal/issues/2928103)

### 2.3.1 — Three Flashes or Below Threshold

- [drupal:2928103 — [policy, no patch] Use "prefers-reduced-motion" media query to disable animations (Active)](https://www.drupal.org/project/drupal/issues/2928103)

### 2.4.1 — Bypass Blocks

- [drupal:3557245 — Use $element['#attributes]['id'] instead of $element['#id'] to create a link anchor (Needs review)](https://www.drupal.org/project/drupal/issues/3557245)

### 2.4.11 — Focus Not Obscured (Minimum)

- [drupal:3272592 — CKEditor 5 has its own focus styles, should use the admin theme's (e.g. Claro's) (Needs work)](https://www.drupal.org/project/drupal/issues/3272592)
- [drupal:3573225 — Some top-level menus obscure unrelated focused items in sidebar (Active)](https://www.drupal.org/project/drupal/issues/3573225)

### 2.4.13 — Focus Appearance

- [drupal:3272592 — CKEditor 5 has its own focus styles, should use the admin theme's (e.g. Claro's) (Needs work)](https://www.drupal.org/project/drupal/issues/3272592)

### 2.4.2 — Page Titled

- [drupal:2509716 — Allow global tokens (and therefore page numbers) in display title (Needs work)](https://www.drupal.org/project/drupal/issues/2509716)
- [drupal:3370946 — Page title should contextualize the local navigation (Needs work)](https://www.drupal.org/project/drupal/issues/3370946)

### 2.4.3 — Focus Order

- [drupal:2925295 — Make sure controls within hidden content are not focusable (Active)](https://www.drupal.org/project/drupal/issues/2925295)
- [drupal:2973114 — When enabling or disabling a block, don't move the focus to the top of the page (Active)](https://www.drupal.org/project/drupal/issues/2973114)
- [drupal:3019849 — Return focus to point of action when the off-canvas dialog closes (Active)](https://www.drupal.org/project/drupal/issues/3019849)
- [drupal:3042107 — Layout Builder actions are inconvenient to access via keyboard navigation (Active)](https://www.drupal.org/project/drupal/issues/3042107)
- [drupal:3044440 — Improve tab navigation by providing 'details' elements with a default value for #title (Active)](https://www.drupal.org/project/drupal/issues/3044440)
- [drupal:3053145 — Allow layout builder sections to be nested. (Active)](https://www.drupal.org/project/drupal/issues/3053145)
- [drupal:3395355 — With an open dialog modal also elements in the background are added to the accessibility object model (Active)](https://www.drupal.org/project/drupal/issues/3395355)
- [drupal:3506324 — Redundant aural interface and the general interaction with CKEditor toolbar configuration (Active)](https://www.drupal.org/project/drupal/issues/3506324)
- [drupal:3506339 — Selecting a column in a table header by keyboard drops the focus (Active)](https://www.drupal.org/project/drupal/issues/3506339)

### 2.4.4 — Link Purpose (In Context)

- [drupal:2922435 — "Add new comment" and "@count comments" links are not following accessibility good practices (Needs work)](https://www.drupal.org/project/drupal/issues/2922435)
- [drupal:3439721 — Make the link descriptions more descriptive, helpful, and clear. (Needs work)](https://www.drupal.org/project/drupal/issues/3439721)

### 2.4.6 — Headings and Labels

- [drupal:2614950 — Add option for visually-hidden block titles (Needs work)](https://www.drupal.org/project/drupal/issues/2614950)
- [drupal:3277785 — Allow wrapping field labels in a heading tag (Needs work)](https://www.drupal.org/project/drupal/issues/3277785)
- [drupal:3293673 — [ATAG] Text editor should alert user when headings are out of order (Active)](https://www.drupal.org/project/drupal/issues/3293673)
- [drupal:3370946 — Page title should contextualize the local navigation (Needs work)](https://www.drupal.org/project/drupal/issues/3370946)

### 2.4.7 — Focus Visible

- [drupal:1919940 — Build API to Replace Links using Title Attributes with Proper Accessible, Themable Tooltips (Needs work)](https://www.drupal.org/project/drupal/issues/1919940)
- [drupal:3163765 — Add option to un-sticky table headers to benefit assistive tech users (Needs work)](https://www.drupal.org/project/drupal/issues/3163765)
- [drupal:3272493 — [drupalImage] Scroll to last image when uploading multiple images (Active)](https://www.drupal.org/project/drupal/issues/3272493)
- [drupal:3272592 — CKEditor 5 has its own focus styles, should use the admin theme's (e.g. Claro's) (Needs work)](https://www.drupal.org/project/drupal/issues/3272592)
- [drupal:3273054 — Checkboxes of text formats in the filter section on the permissions page have visually hidden labels with links causing hidden focus states (Active)](https://www.drupal.org/project/drupal/issues/3273054)
- [drupal:3557245 — Use $element['#attributes]['id'] instead of $element['#id'] to create a link anchor (Needs review)](https://www.drupal.org/project/drupal/issues/3557245)
- [drupal:3574319 — Sidebar logo link sometimes lacks focus indicator (Active)](https://www.drupal.org/project/drupal/issues/3574319)

### 2.4.9 — Link Purpose (Link Only)

- [drupal:3080853 — Improve link text on available updates page to address WCAG SC 2.4.9 Link purpose (link only) (Needs work)](https://www.drupal.org/project/drupal/issues/3080853)

### 2.5.1 — Pointer Gestures

- [drupal:2920006 — Research accessibility of drag-and-drop grid interfaces. (Active)](https://www.drupal.org/project/drupal/issues/2920006)
- [drupal:3027229 — Modernize tabledrag accessibility. (Active)](https://www.drupal.org/project/drupal/issues/3027229)

### 2.5.2 — Pointer Cancellation

- [drupal:2616184 — Right click should not submit buttons with Ajax behaviors (Needs work)](https://www.drupal.org/project/drupal/issues/2616184)
- [drupal:2958654 — Assess JavaScript behaviours for WCAG 2.1 Pointer Cancellation (Needs work)](https://www.drupal.org/project/drupal/issues/2958654)
- [drupal:2960840 — Replace javascript event listeners which use "down" events in the ajax component (Active)](https://www.drupal.org/project/drupal/issues/2960840)
- [drupal:2968637 — Assess the reference to the mousedown event in the base class for render element plugins (Needs work)](https://www.drupal.org/project/drupal/issues/2968637)

### 2.5.3 — Label in Name

- [drupal:2960828 — Link labels generated by the Entity List Builder should provide more context for a11y (Needs work)](https://www.drupal.org/project/drupal/issues/2960828)
- [drupal:2973124 — Provide better context in accessible names of EntityOperation views plugin drop-button operations (Needs work)](https://www.drupal.org/project/drupal/issues/2973124)
- [drupal:3015239 — Assess Drupal core for WCAG success criterion 2.5.3 Label in Name (Active)](https://www.drupal.org/project/drupal/issues/3015239)
- [drupal:3083583 — [META] Discourage non-inclusive use of the HTML title attribute (Active)](https://www.drupal.org/project/drupal/issues/3083583)
- [drupal:3611421 — WCAG 2.5.3: Module lifecycle links aria-label diverges from visible text (Active)](https://www.drupal.org/project/drupal/issues/3611421)
- [drupal:3611425 — Navigation admin "Extend" button has hidden text before menu title (Needs review)](https://www.drupal.org/project/drupal/issues/3611425)
- [drupal:3611426 — WorkflowEditForm repeated Edit/Delete without disambiguation (Active)](https://www.drupal.org/project/drupal/issues/3611426)
- [drupal:3611428 — Comment admin repeated Edit links without disambiguation (Active)](https://www.drupal.org/project/drupal/issues/3611428)
- [drupal:3611429 — Config translation repeated Edit/Delete/Add without disambiguation (Active)](https://www.drupal.org/project/drupal/issues/3611429)

### 2.5.8 — Target Size (Minimum)

- [drupal:3459246 — Add a '#select_all' option for checkboxes element (Needs work)](https://www.drupal.org/project/drupal/issues/3459246)

### 3.1.2 — Language of Parts

- [drupal:2496223 — Views containing content not in the page's language need to add tags which mark the language of parts (Active)](https://www.drupal.org/project/drupal/issues/2496223)
- [drupal:2827034 — DateList and date range inline form errors are repeated (Needs work)](https://www.drupal.org/project/drupal/issues/2827034)
- [drupal:3020305 — Links in language switcher block do not conform to WCAG language-of-parts (Needs work)](https://www.drupal.org/project/drupal/issues/3020305)
- [drupal:3042984 — template_preprocess_username fails to set language attribute (Needs work)](https://www.drupal.org/project/drupal/issues/3042984)
- [drupal:3300836 — Untranslatable fields do not respect language of parts (Active)](https://www.drupal.org/project/drupal/issues/3300836)
- [drupal:3361370 — Untranslatable fields on translations of nodes are not marked for Language of Parts (Active)](https://www.drupal.org/project/drupal/issues/3361370)
- [drupal:3361375 — Untranslated field labels on translations of nodes are not marked for Language of Parts (Active)](https://www.drupal.org/project/drupal/issues/3361375)
- [drupal:3362791 — Untranslated translatable fields on translations of nodes are not marked for Language of Parts (Active)](https://www.drupal.org/project/drupal/issues/3362791)
- [drupal:82751 — Allow some HTML tags in node titles (Active)](https://www.drupal.org/project/drupal/issues/82751)

### 3.2.1 — On Focus

- [drupal:3506324 — Redundant aural interface and the general interaction with CKEditor toolbar configuration (Active)](https://www.drupal.org/project/drupal/issues/3506324)
- [drupal:3506339 — Selecting a column in a table header by keyboard drops the focus (Active)](https://www.drupal.org/project/drupal/issues/3506339)
- [drupal:3611769 — Select field in modal dialog has jumpy focus (Active)](https://www.drupal.org/project/drupal/issues/3611769)

### 3.2.3 — Consistent Navigation

- [drupal:2895388 — Modules uninstall filter does not filter by machine name (Needs work)](https://www.drupal.org/project/drupal/issues/2895388)
- [drupal:3015494 — Make admin list filters behave more consistently. (Active)](https://www.drupal.org/project/drupal/issues/3015494)
- [drupal:3209129 — Scrolling problems when adding a block via layout builder (Needs work)](https://www.drupal.org/project/drupal/issues/3209129)

### 3.2.5 — Change on Request

- [drupal:2158943 — Add a native dialog element using HTMX to deprecate the jQuery UI dialog (Needs review)](https://www.drupal.org/project/drupal/issues/2158943)

### 3.2.7 — WCAG criterion

- [drupal:2805197 — Provide screen-reader feedback when Views UI filterable options are updated (Needs work)](https://www.drupal.org/project/drupal/issues/2805197)

### 3.3.1 — Error Identification

- [drupal:2089703 — The file upload field needs a progress indicator that expresses to screen reading user agents when a file upload is finished (Needs work)](https://www.drupal.org/project/drupal/issues/2089703)
- [drupal:2455933 — Error highlighting and reporting problems for the current password on the user profile form (Needs work)](https://www.drupal.org/project/drupal/issues/2455933)
- [drupal:2560467 — Inline Errors not shown for container elements (Needs work)](https://www.drupal.org/project/drupal/issues/2560467)
- [drupal:2563173 — Display 'required' validation errors for form elements that do not provide a #title (Needs work)](https://www.drupal.org/project/drupal/issues/2563173)
- [drupal:2847425 — #states not affecting visibility/requirement of managed_file (Needs review)](https://www.drupal.org/project/drupal/issues/2847425)
- [drupal:2848307 — Inline errors not working on form table elements (Needs work)](https://www.drupal.org/project/drupal/issues/2848307)
- [drupal:3081526 — Add announcement after clicking 'Save and select' in the media library. (Needs work)](https://www.drupal.org/project/drupal/issues/3081526)
- [drupal:3083103 — Programmatically associate error messages with inputs (Needs work)](https://www.drupal.org/project/drupal/issues/3083103)
- [drupal:3087305 — Form validation error messages within the Media Library widget are not read by the screenreader (Needs work)](https://www.drupal.org/project/drupal/issues/3087305)
- [drupal:3087385 — If the user attempts to upload an incorrect file type through the media library modal, the error message is not read by the screenreader (Needs work)](https://www.drupal.org/project/drupal/issues/3087385)
- [drupal:3089402 — Drupal.Message should add 'Error message' prefixed to Drupal.announce error messages (Needs work)](https://www.drupal.org/project/drupal/issues/3089402)
- [drupal:3243173 — Form focus / screen reader issues related to server side form validation (Active)](https://www.drupal.org/project/drupal/issues/3243173)
- [drupal:3261571 — Prepend error to document.title when form submission fails (Active)](https://www.drupal.org/project/drupal/issues/3261571)
- [drupal:3271203 — [drupalImage] Announce image upload for screenreader users (Active)](https://www.drupal.org/project/drupal/issues/3271203)
- [drupal:3344778 — Form input errors should be announced via the aria-live region every time they occur (Active)](https://www.drupal.org/project/drupal/issues/3344778)
- [drupal:3600851 — [Meta] Set the invalid state for all fields in Core in the Accessibility Object Model (AOM) properly (Needs work)](https://www.drupal.org/project/drupal/issues/3600851)
- [drupal:3604037 — Indicate that grouping elements have child element errors for UX and a11y (Needs work)](https://www.drupal.org/project/drupal/issues/3604037)
- [drupal:736182 — Match States API required fields theming with Forms API (Needs work)](https://www.drupal.org/project/drupal/issues/736182)

### 3.3.2 — Labels or Instructions

- [drupal:2608212 — Elements on grouped exposed filters configuration form are missing accessible names (Needs work)](https://www.drupal.org/project/drupal/issues/2608212)
- [drupal:2852874 — [Meta] Set the required state for all fields in Core in the Accessibility Object Model (AOM) (Active)](https://www.drupal.org/project/drupal/issues/2852874)
- [drupal:2942037 — Admin list filter fields are inconsistently labelled. (Active)](https://www.drupal.org/project/drupal/issues/2942037)
- [drupal:3037446 — Forms with required fields marked by asterisk do not have text explaining what the asterisk means (Needs work)](https://www.drupal.org/project/drupal/issues/3037446)
- [drupal:3283883 — Fieldset should not create title element when title is empty (Needs work)](https://www.drupal.org/project/drupal/issues/3283883)
- [drupal:3426798 — CKEditor 5 text area doesn't have appropriate aria-label for screen reader (Needs work)](https://www.drupal.org/project/drupal/issues/3426798)
- [drupal:933004 — Test that all form elements have a #title for accessibility (Needs work)](https://www.drupal.org/project/drupal/issues/933004)

### 3.3.3 — Error Suggestion

- [drupal:3619127 — Forms sidebar doesn't open with error links from Inline Form Errors module (Needs review)](https://www.drupal.org/project/drupal/issues/3619127)

### 4.1.2 — Name, Role, Value

- [drupal:1402250 — Allow modules to classify blocks when defining them, so WAI-ARIA roles can automatically be added in the theme layer (Needs work)](https://www.drupal.org/project/drupal/issues/1402250)
- [drupal:1852090 — Cached render elements can have duplicate HTML IDs (Needs work)](https://www.drupal.org/project/drupal/issues/1852090)
- [drupal:1854046 — Add "changed" hints to translation settings page (Needs work)](https://www.drupal.org/project/drupal/issues/1854046)
- [drupal:2046529 — Add title attributes to buttons for Dragon users (Needs work)](https://www.drupal.org/project/drupal/issues/2046529)
- [drupal:2047089 — Content translation settings UI should leverage Drupal.announce() to inform screen reader users of dynamic changes (Active)](https://www.drupal.org/project/drupal/issues/2047089)
- [drupal:2079129 — Investigate how Dragon Naturally Speaking recognizes UI elements; test with a modal close button (Active)](https://www.drupal.org/project/drupal/issues/2079129)
- [drupal:2084603 — Addition of natural language to Article and Basic page links on Create Content page (Needs work)](https://www.drupal.org/project/drupal/issues/2084603)
- [drupal:2124405 — Take advantage of ARIA roles (specifically widget roles) to enrich the non-visual interface of Views (Active)](https://www.drupal.org/project/drupal/issues/2124405)
- [drupal:2290043 — Threaded Comments Should Use Heading Levels to Communicate Reply Depth (Active)](https://www.drupal.org/project/drupal/issues/2290043)
- [drupal:2305109 — Figure/Figcaption for Image Widget (Needs work)](https://www.drupal.org/project/drupal/issues/2305109)
- [drupal:2608212 — Elements on grouped exposed filters configuration form are missing accessible names (Needs work)](https://www.drupal.org/project/drupal/issues/2608212)
- [drupal:2719453 — Tableselect single radio button missing #title attribute and is not accessible (Needs work)](https://www.drupal.org/project/drupal/issues/2719453)
- [drupal:2805499 — Provide screen reader feedback when Views List is filtered by name or description (Needs work)](https://www.drupal.org/project/drupal/issues/2805499)
- [drupal:2822414 — Redesign the 'install profile selection' installer screen to allow for experimental profiles and more information (Needs work)](https://www.drupal.org/project/drupal/issues/2822414)
- [drupal:2863846 — File Field design update progress bar (Active)](https://www.drupal.org/project/drupal/issues/2863846)
- [drupal:2913378 — Bulk Action Results are not read by Screen Reader (Active)](https://www.drupal.org/project/drupal/issues/2913378)
- [drupal:2917777 — Improvements to the styling, grouping, etc. of the Layout Builder UI actions form (Active)](https://www.drupal.org/project/drupal/issues/2917777)
- [drupal:2962585 — Treat entity label as a row-level header in entity list tables (Active)](https://www.drupal.org/project/drupal/issues/2962585)
- [drupal:2974944 — Use a tri-state checkbox for tableselect widget. (Active)](https://www.drupal.org/project/drupal/issues/2974944)
- [drupal:2986517 — Document special 'title' key used for Tableselect checkbox labels (Active)](https://www.drupal.org/project/drupal/issues/2986517)
- [drupal:3028780 — Contextual links button should use aria-expanded instead of aria-pressed (Needs work)](https://www.drupal.org/project/drupal/issues/3028780)
- [drupal:3044440 — Improve tab navigation by providing 'details' elements with a default value for #title (Active)](https://www.drupal.org/project/drupal/issues/3044440)
- [drupal:3083181 — Menu blocks in Layout Builder get malformed aria-labelledby attribute (Needs work)](https://www.drupal.org/project/drupal/issues/3083181)
- [drupal:3087313 — In the media library modal, improve the labels on the media-type tabs for screen readers (Needs work)](https://www.drupal.org/project/drupal/issues/3087313)
- [drupal:3105316 — Add accessible names to theme region complementary landmarks (Needs work)](https://www.drupal.org/project/drupal/issues/3105316)
- [drupal:3208640 — <figure> elements with a role of group need an accessible label (Needs work)](https://www.drupal.org/project/drupal/issues/3208640)
- [drupal:3218877 — Labels do not have correct 'for' attribute if 'id' set in #attributes (Needs work)](https://www.drupal.org/project/drupal/issues/3218877)
- [drupal:3318394 — Block UI A11y errors identified with Axe + Nightwatch (Active)](https://www.drupal.org/project/drupal/issues/3318394)
- [drupal:3327459 — Use semantic markup instead of repeated hyphens to represent hierarchical taxonomy terms (Active)](https://www.drupal.org/project/drupal/issues/3327459)
- [drupal:3342811 — Add role="button" and spacebar trigger to <a class="use-ajax"> to behave like a button (Active)](https://www.drupal.org/project/drupal/issues/3342811)
- [drupal:3348552 — Pager template fails accessibility tests for Ellipsis ("...") (Needs review)](https://www.drupal.org/project/drupal/issues/3348552)
- [drupal:3459246 — Add a '#select_all' option for checkboxes element (Needs work)](https://www.drupal.org/project/drupal/issues/3459246)
- [drupal:3502292 — Ensures interactive controls are not nested (Active)](https://www.drupal.org/project/drupal/issues/3502292)
- [drupal:3545814 — Exposed filters with exposed operators are missing accessible names (Needs work)](https://www.drupal.org/project/drupal/issues/3545814)
- [drupal:3571628 — The aria-expanded attribute doesn't change once it became true on a node edit forms detail summary element (Needs work)](https://www.drupal.org/project/drupal/issues/3571628)
- [drupal:3606909 — Ensure interactive controls are not nested (Active)](https://www.drupal.org/project/drupal/issues/3606909)
- [drupal:675348 — META: Support HTML5 form input elements (Active)](https://www.drupal.org/project/drupal/issues/675348)
- [drupal:933004 — Test that all form elements have a #title for accessibility (Needs work)](https://www.drupal.org/project/drupal/issues/933004)
- [drupal:953034 — [meta] Themes improperly check renderable arrays when determining visibility (Needs work)](https://www.drupal.org/project/drupal/issues/953034)

### 4.1.3 — Status Messages

- [drupal:2893663 — Dropbutton should report open/closed state to assistive technology (Active)](https://www.drupal.org/project/drupal/issues/2893663)
- [drupal:2973116 — After enabling or disabling a view, convey changes to screen reader users. (Active)](https://www.drupal.org/project/drupal/issues/2973116)
- [drupal:2973140 — Convey AJAX progress messages to assistive technology. (Needs review)](https://www.drupal.org/project/drupal/issues/2973140)
- [drupal:3035435 — Make the show/hide row weights button more informative for assistive tech users. (Needs work)](https://www.drupal.org/project/drupal/issues/3035435)
- [drupal:3159933 — Status Message in Claro on theme install should have role="status" or similar instead of contentinfo (Needs work)](https://www.drupal.org/project/drupal/issues/3159933)
- [drupal:3360146 — Updates to AJAX view filters for assistive technology (Active)](https://www.drupal.org/project/drupal/issues/3360146)

## Sources

**Authoritative sources**

| Source | Link |
| --- | --- |
| Drupal Core Accessibility queue | [Drupal.org Accessibility issue queue](https://www.drupal.org/project/issues/search?text=&projects=Drupal+core&assigned=&submitted=&project_issue_followers=&status%5B%5D=Open&issue_tags_op=%3D&issue_tags=Accessibility) |
| WCAG 2.2 | [W3C WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/) |
| OpenACR | [GSA OpenACR](https://github.com/GSA/openacr) |
| ATAG 2.0 | [W3C ATAG 2.0](https://www.w3.org/TR/ATAG20/) |
| WAI ATAG Report Tool | [WAI ATAG Report Tool](https://www.w3.org/WAI/atag/report-tool/) |
