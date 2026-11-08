# Drupal Accessibility Conformance Report (ACR) — Template

**Status: DRAFT TEMPLATE — not an approved ACR.**

Use this as the reusable shell for a Drupal product or distribution. Replace every
bracketed value and complete the criterion table for the evaluated version.
Validate the machine-readable result with the OpenACR schema/catalog before
publication.

## Product information

| Field | Value |
|---|---|
| Product | [Product name] |
| Version / release | [Version] |
| Description | [Short product description] |
| Report date | [YYYY-MM-DD] |
| Last modified | [YYYY-MM-DD] |
| Author / reviewer | [Name, organization, contact] |
| Evaluation methods | [WCAG-EM sample, manual tests, assistive technologies, issue-queue review] |
| Standards baseline | WCAG 2.2 AA; Revised Section 508 |
| Repository / feedback | [URLs] |

## Component scope

Section 508 reporting for a Drupal web product normally uses four components.
Assess the two applicable components and explain the two not-applicable ones.

| Component | Proposed result | Explanation |
|---|---|---|
| Web | **Partially Supports** | [Explain the front-end barriers and the evidence. A Partially Supports result requires an explanation.] |
| Electronic Documents | **Not Applicable** | Drupal Core is a web content platform; it does not produce a standalone electronic-document product. Uploaded documents are delivered as web content. |
| Software | **Not Applicable** | Drupal Core is a web application; the Section 508 software chapter is not a separate installed/non-web product in this scope. |
| Authoring Tool | **Partially Supports** | [Explain the authoring-interface barriers and the evidence.] |

`Supports`, `Partially Supports`, `Does Not Support` and `Not Applicable` are
conformance labels. Every `Supports` and `Partially Supports` result needs a
specific explanation; `Not Applicable` needs a scope rationale.

> The proposed results above are placeholders for review. Do not publish them as
> final until the criterion-level evidence and explanations are complete.

## Classifying authoring vs web issues

Use explicit evidence, not guesswork:

- `/admin` in the reproduction path or steps → authoring interface.
- Drupal login paths `/user`, `/user/login` or `/user/password` → authoring
  interface.
- Reproduction requires logging in, an administrator account, or the authoring
  UI → authoring interface.
- All `/user` paths, including profiles such as `/user/1` and `/user/register`,
  are authoring/account surfaces for this classification.
- A public front-end page, anonymous view, or published content → web.

Some authoring interfaces can expose front-end content. Classify the issue by
where the barrier occurs; if both apply, record both and explain the boundary.
Record the classification basis (`admin-path`, `login-step`, or `default-web`)
so a reviewer can check it.

## Criterion table

Use the OpenACR catalog to list every applicable criterion. A template row:

| Criterion | Level | Web | Electronic Documents | Software | Authoring Tool | Remarks and explanations |
|---|---|---|---|---|---|---|
| 1.1.1 Non-text Content | A | Partially Supports | Not Applicable | Not Applicable | Partially Supports | [Explain the evidence, sample scope and remaining barriers.] |
| 1.2.4 Captions (Live) | AA | Not Applicable | Not Applicable | Not Applicable | Not Applicable | Drupal Core has no live audio/video feature. Evaluate the contrib Video or AblePlayer module separately. |
| 1.2.5 Audio Description (Prerecorded) | AA | Not Applicable | Not Applicable | Not Applicable | Not Applicable | Drupal Core has no core video player/audio-description feature. Evaluate contrib Video or AblePlayer separately. |

Do not infer `Supports` from an empty issue queue. A closed or missing issue is
not a completed evaluation.

## Required explanations

- **Partially Supports** — state which functionality fails, the sample scope,
  the affected component and the issue/evidence links.
- **Supports** — state the method and sample scope; explain why the result is
  being claimed.
- **Does Not Support** — state the failing functionality and evidence.
- **Not Applicable** — state why the component or criterion is outside the
  product scope.

## Review checklist

- [ ] Product/version/date and reviewer identity are complete.
- [ ] Web and Authoring Tool are assessed separately.
- [ ] Electronic Documents and Software have a scope rationale.
- [ ] Every criterion has a result and explanation, or is explicitly blocked.
- [ ] Partially Supports and Supports explanations are specific.
- [ ] Issue classifications are based on `/admin`, login/reproduction steps or
      public front-end evidence.
- [ ] No issue count is presented as a conformance score.
- [ ] The result is serialized as OpenACR and validated.
- [ ] An independent reviewer has signed off.

## Section 508 references

- <https://www.section508.gov/test/>
- <https://ictbaseline.access-board.gov/>
- <https://www.section508.gov/buy/authoring-tools/>
- <https://www.access-board.gov/ict/#504-authoring-tools>
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [OpenACR](https://github.com/GSA/openacr)
