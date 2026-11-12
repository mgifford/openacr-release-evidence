# Report usability and correctness review

**Status: Phases 1–5 implemented on 2026-11-12. Phase 6 proposed.**

This review responds to reviewer feedback on the published release reports. It
records the problems found in the current generator, the smallest safe changes
made, and what remains for later phases.

The underlying data model is unchanged except where the conformance policy was
wrong. Existing issue records, source links, applicability values, digests and
OpenACR schema validation are preserved.

## The five most consequential problems

### 1. The report did not explain what "evidence" meant

**Symptom.** The same word covered an issue report, a merge request, a contained
commit and a reproduced barrier. Readers could not tell how strongly any claim
was supported.

**Where it originated.** `docs/CONFORMANCE-POLICY.md` and
`docs/EVIDENCE-MODEL.md` used precise but scattered definitions. The report's
first screen went straight to metadata and counts.

**Change made.** Added a "How to read this report" section near the top with
definitions for reported issue, source information, release applicability,
verified problem, fix included, verified fix, not yet determined and
conformance determination. See [`REPORT-TERMINOLOGY.md`](REPORT-TERMINOLOGY.md).
The report itself now says a report is not proof and an included fix is not a
verified fix.

### 2. Issue workflow status was presented like a grade, and release applicability was easy to miss

**Symptom.** "Needs work" and "Unknown" looked like contradictory evaluations.
The issue table's "Tracker status" and "Release applicability" columns were
adjacent but not explained.

**Where it originated.** `src/acr_evidence/report.py`: `_issue_index`,
`_issue_article`, `_summary_table`, `_status_table`; labels in
`src/acr_evidence/wcag.py`.

**Change made.**

- The table now has separate `Drupal.org status` and `Applies to this release?`
  columns.
- Every status cell includes a plain explanation ("open on Drupal.org; not a
  severity grade", "being worked on; not a release finding").
- Every applicability cell has a "Why this state" and "What to do next" column.
- The issue detail repeats both labels with their meanings.
- The summary tables are now titled "Applies to this release?" and
  "Drupal.org status", with captions that say neither is an accessibility grade.
- The label `Unknown (insufficient target-specific evidence)` is now
  `Not yet determined`. The machine value remains `unknown`.

### 3. There was no plain-language summary, and the first screen was methodology

**Symptom.** The report opened with assessment scope and a large metadata list.
The "Evidence summary" was mostly counts and did not say what to do.

**Where it originated.** `render_report` section order in
`src/acr_evidence/report.py`; the old summary was `_metric_grid` plus two tables.

**Change made.** A generated summary now appears immediately after the page
header. It answers:

- What release is this?
- What was collected?
- What probably affects this release?
- What has actually been verified?
- What remains uncertain?
- What should maintainers, site builders, evaluators and procurement readers do
  next?

The summary is derived from `findings` and `summary.by_applicability`, not
hardcoded. When nothing has been reproduced it says so. When no fix has been
behaviourally verified it says so. It also reports exact-release component
counts from `data/component-inventory/` and explains that removed themes are a
scope change, not a fix.

**Actual example, Drupal Core 12.0.0-beta2 (2026-11-10 collection):**

> This report tracks accessibility issues reported against Drupal Core and asks
> whether they affect 12.0.0-beta2. It is a starting point for investigation,
> not an accessibility certification.
>
> We collected 432 active accessibility issues. 30 issues probably affect this
> release, 0 issues are verified problems in this release, and 402 issues are
> not yet determined.
>
> No reported problem has been reproduced against this release, so the report
> cannot call any issue a verified problem. No fix has been tested and confirmed
> to resolve a barrier in this release.
>
> **What we actually know**
> - 30 issues probably affect this release based on reports and code checks, but
>   were not reproduced.
> - 402 issues are not yet determined. That means we have not checked whether
>   they affect this release; it does not mean the release is accessible or
>   inaccessible.
> - 0 issues have been reproduced on this release.
> - 0 findings have a fix included in the release; inclusion is not proof that
>   the barrier is gone.
>
> **Component scope in this release.** This exact release bundles 67 modules and
> 3 themes. The standard installation profile enables 36 modules and 1 theme;
> its default theme is Default Admin and its admin theme is Default Admin. Claro
> and Olivero left Core in 12.0.0-beta1 and are now maintained as contributed
> projects. Their absence is a scope change, not evidence that their reported
> barriers were fixed.

The last paragraph is generated from the inventory and lineage records, not
written by hand into the template.

### 4. `Unknown` had no reason, no grouping and no next step

**Symptom.** 402 of 432 beta2 findings said "Unknown (insufficient
target-specific evidence)". Readers could not tell whether more data collection
or actual testing was needed.

**Where it originated.** `src/acr_evidence/release.py` already records a `basis`
value per finding, but the report only showed the reason in the long issue
article. The index showed no reason.

**Change made.** `_state_reason()` maps the existing `basis` and
`evidence_status` to a plain reason, and `_next_action()` recommends a
proportional step. Examples:

| Basis | Report reason | Next step |
| --- | --- | --- |
| `inventory-only` | Only basic issue information was collected; comments, merge requests and commits were not reviewed. | Collect the issue discussion and merge-request evidence, then check this release. |
| `tracker-report` | An open report exists, but nobody has reproduced it on this release. | Try to reproduce the reported barrier on this release. |
| `git-non-inclusion` | Matching fix commits exist but are not included in this release. | Review the merge request and try to reproduce the barrier. |
| `report-after-release` | The issue was reported after this release was cut; it may be a later regression. | Check the component and reproduce before assigning applicability. |
| `code-presence` | The affected component or feature is absent from this release. | No action for this release; the component is not present. |

The index and the issue detail both show the reason and the next step.

Phase 4 then grouped the issue index by applicability:

1. Verified problems
2. Probably affects this release
3. Fix included, not behaviourally verified
4. Needs checking
5. Not present or outside this report

Each group has its own explanation and count. A CSS-only radio filter hides
groups that do not match the selected state; all groups remain in the document
without JavaScript. `issues.html` also reports why issues are not determined:
for beta2, 394 are basic metadata records and 8 were reported after the release
was cut.

### 5. The pipeline generated unsupported conformance conclusions

**Symptom.** The ACR narrative and OpenACR draft converted report presence or
absence into `Partially Supports` and `Supports`.

**Where it originated.** `src/acr_evidence/surface_assessment.py`:

```python
elif _surface_issues(issues, surface):
    results[name] = "Partially Supports"
elif (surfaces.get(name) or {}).get("status") == "assessed":
    results[name] = "Supports"
```

This contradicts the project's own policy statement that absence is not support
and issue tags are not conformance results. It also contradicted
`docs/CONFORMANCE-POLICY.md`, which already said "Never auto-fill `Supports`".

**Change made.** The automatic mapping was removed:

- `criterion_results()` returns `Not Evaluated` for Web and Authoring Tool unless
  there is explicit broad-failure evidence in the policy.
- `component_results()` returns `Not Evaluated` for Web and Authoring Tool.
- Documented feature absence still produces `Not Applicable`.
- The OpenACR draft leaves every non-`Not Applicable` adherence value unset. The
  `component_scope` entries are marked `unassessed`.
- The ACR narrative shows `Not Evaluated` and lists reported issues as potential
  barriers, not conformance findings.
- The ACR still uses the OpenACR terms and still validates against the pinned
  schema and catalog.

At this snapshot the beta2 draft has **184 `not-applicable` adherence values and
no `supports`, `partially-supports` or `does-not-support` values**. The
`not-applicable` values are documented media/product-scope exclusions, not
queue-derived results.

## What moved, was renamed, or was omitted

| Before | After | Why |
| --- | --- | --- |
| Assessment scope was the first content section | Summary and "How to read" are first; release details are later | Readers need the conclusion and definitions before metadata |
| "Evidence summary" with counts | "What this report says about …" plus "Summary details" | Make the takeaway explicit and keep counts as supporting detail |
| "Tracker status" | "Drupal.org status" | Name the source system and separate it from release evidence |
| "Release applicability" as a bare state | "Applies to this release?" plus reason and next step | Explain the state instead of just labelling it |
| "Unknown (insufficient target-specific evidence)" | "Not yet determined" | Plain language; the machine value is unchanged |
| "Likely affected" | "Probably affects this release (not reproduced)" | Say what was and was not done |
| "Fix included in release (not independently verified)" | "Fix included in this release (not behaviourally verified)" | Commit inclusion is not a behavioural fix |
| Automatic `Supports` / `Partially Supports` | Unset OpenACR values and `Not Evaluated` narrative | Unsupported conformance conclusions |
| Long metadata list before the summary | Complete metadata is on `sources.html` | Traceability is preserved without dominating the overview |
| One long `index.html` | Six pages: overview, issues, criteria, sources, method, ACR | Each reader can start at the right level of detail |
| Inventory counts only | Sources page adds component changes and lineage | Component movement is visible without inferring fixes or inherited issues |

Nothing was removed from the issue records, source links, criterion index,
component index or downloads.

## Component history integration

`sources.html` now contains the exact-release inventory table, a comparison with
the previous declared target, and the curated lineage records. The comparison is
package membership only; the lineage table states the per-release status of each
relationship and keeps every record `unreviewed`.

For 12.0.0-beta2 the page shows that Claro and Olivero were removed in
12.0.0-beta1, that Default Admin applies from 11.4.0, and that Claro code is
shared with Default Admin. It also says that removal is not a fix and that
adoption does not inherit predecessor issues.

## What is still not done

- The issue table is not yet filterable by applicability, component or criterion
  on the static page. The data attributes and values are present in the HTML, so
  a progressive-enhancement filter can be added without changing the data model.
- The split pages were checked with automated structure and link tests, axe-core
  and a 320 px viewport. Reader testing of the new navigation is still needed.
- The report is now split into overview, issues, criteria, sources and method
  pages. `issues.html` is still large because it contains every canonical issue
  record; per-issue pages or pagination are a later optimisation.
- `issues.html` still contains all 432 canonical issue records in one page.
  Per-issue pages or pagination are a later optimisation; grouping and the
  applicability filter are implemented.
- No manual screen-reader or keyboard test of the revised layout has been
  recorded in this session. Automated HTML structure tests and the existing
  no-JavaScript constraints pass.
- The `confirmed-fixed` machine value is retained for compatibility. Its report
  label is now explicit that it means code inclusion only.

## Checks run on the revised report

On 2026-11-12, the regenerated `reports/drupal-core-12.0.0-beta2/index.html` was
checked in headless Chrome at 320 × 900 CSS px:

- **Reflow:** on `index.html`, `issues.html`, `criteria.html`, `sources.html`,
  `method.html` and `acr.html`, `scrollWidth` and `clientWidth` were both 320.
  The wide issue and criteria tables are inside their own `role="region"` scroll
  containers.
- **axe-core 4.x:** 0 violations on all six pages for the WCAG 2.0/2.1/2.2 A/AA
  rule tags. This is automated coverage only, not a conformance result.
- **Keyboard:** the first Tab on the overview focused the skip link
  (`Skip to main content`, `href="#main"`). The native `<details>` elements and
  the grouped issue filter remain keyboard operable.
- **No JavaScript:** all five HTML navigation/evidence pages rendered their
  title, breadcrumb and content with JavaScript disabled.
- **Links:** a cross-page link checker resolved every relative link and
  fragment in all five targets; `tests/test_report.py` checks each page's
  in-page anchors.
- **Automated HTML tests:** headings, table captions, scoped headers and
  in-page anchors are covered by `tests/test_report.py`.

Manual screen-reader testing was **not** performed in this session. Forced-colors
and 400% browser-zoom manual checks were **not** performed beyond the 320 px
layout check. These remain Phase 6 work.

## Tests that protect this phase

- `tests/test_report.py` checks the two separate labels, the plain-language
  summary, the "not yet determined" wording, data-derived counts, and that no
  conformance term is emitted for issue evidence.
- `tests/test_surface_assessment.py` checks that a reported issue does not
  produce `Partially Supports`, an empty queue does not produce `Supports`, and
  documented feature absence still produces `Not Applicable`.
- `tests/test_openacr_standard.py` checks that non-`Not Applicable` adherence
  values are unset, `component_scope` is `unassessed`, and the draft still
  validates against the pinned schema and catalog.
- `tests/test_acr_narrative.py` checks that the narrative shows `Not Evaluated`
  for Web and Authoring Tool and no longer claims `Supports` from an empty queue.
