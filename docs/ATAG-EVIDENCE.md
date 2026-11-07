# ATAG 2.0 authoring evidence

ATAG 2.0 is a separate standard from WCAG and OpenACR. It applies to authoring
tools: Part A covers accessibility of the authoring tool user interface; Part B
covers support for producing accessible content. Drupal Core’s content-editing
and administration interfaces are an authoring tool.

The pipeline keeps ATAG evidence separate from the WCAG release matrix and the
OpenACR draft. Neither standard inherits the other’s conclusions.

## Drupal tags and queues

The common Accessibility tag is taxonomy term **1101**. The ATAG tag is term
**5050** (`atag`). The issue queue filters are:

- [Accessibility queue](https://www.drupal.org/project/issues/search?text=&projects=&assigned=&submitted=&project_issue_followers=&issue_tags_op=%3D&issue_tags=Accessibility)
- [atag queue](https://www.drupal.org/project/issues/search?text=&projects=&assigned=&submitted=&project_issue_followers=&issue_tags_op=%3D&issue_tags=atag)

The current active snapshot contains 32 ATAG-tagged Drupal Core issues; all carry
the Accessibility tag. The report still checks for and reports any ATAG issue
that is missing the common tag, because it would otherwise disappear from the
Accessibility-only queue. The collection is scoped to the Drupal Core project;
contrib ATAG issues are not included. Fixed, closed and postponed ATAG issues are
excluded, consistent with the ACR active-issue policy.

The current snapshot contains 6 `[meta]` tracker issues. They are listed in a
separate meta/tracker section and are not counted as Part A/B bug evidence.

### Part A/B tags

The parser recognises, case-insensitively:

- generic: `atag`
- Part A: `atag-a`, `atag-part-a`, `ATAG Part A`, `atag 2.0 part a`
- Part B: `atag-b`, `atag-part-b`, `ATAG Part B`, `atag 2.0 part b`
- criterion: `atag-a.3.1.1`, `atag-b.2.3.1`

Explicit Part A/B tags take precedence. If the queue uses a different naming
convention, add it to `src/acr_evidence/atag.py` and a test.

## Classification order

1. Explicit Part A/B tags.
2. Curated `config/atag-scope.json` entries for particular issue IDs.
3. Component candidate mapping in
   `src/acr_evidence/standards/atag/component-scope.json` (for example
   `ckeditor.module` → Part A+B, `filter.module` → Part B, `toolbar` → Part A).
4. `ATAG-tagged, part not specified`.

`[meta]` tracker issues are kept separate: they are useful navigation, but they
are not counted as Part A/B bug evidence.

Component candidates are **triage hints**, not evidence that a criterion is met
or failed. They are labelled as candidates and remain `needs-triage`.

## Report

Current snapshot: 32 active ATAG-tagged issues, 6 meta/tracker issues, 8 Part A
component candidates, 20 Part B component candidates (overlapping), 4
unspecified, 0 explicit Part A/B issue tags and 0 missing Accessibility tags.
The meta tracker `2034909` is mapped to both parts in `config/atag-scope.json`
but is excluded from the bug counts.

`reports/drupal-core-atag/` contains:

- `index.html` — static, no-JavaScript ATAG evidence report with Part A/Part B
  explicit and candidate sections, unspecified issues, data-quality findings and
  limitations.
- `atag-evidence.json` — machine-readable issue/part/candidate classification.
- `atag-report.json` — WAI ATAG Report Tool JSON draft.
- `report.css`.

The landing page links the ATAG report separately from the WCAG reports.

## WAI ATAG Report Tool draft

`atag-report.json` follows the import shape used by the
[WAI ATAG Report Tool](https://www.w3.org/WAI/atag/report-tool/):

- `evaluationData` contains all **63** ATAG 2.0 success criteria;
- every `result` is **`Not checked`**;
- `meta` includes product name/version, a draft executive summary, a placeholder
  evaluator, conformance target `AA` and an evaluation ID.

A reviewer imports the JSON, replaces the placeholder evaluator fields, records
results and observations criterion by criterion, and exports the final ATAG
report from the tool.

Import was verified on 2026-11-07 in the live
[WAI ATAG Report Tool](https://www.w3.org/WAI/atag/report-tool/): the draft name,
website, evaluation ID and placeholder evaluator loaded, and the report page
showed **0 of 52 Level A/AA criteria reported** with all 52 **Not checked**
(AAA criteria are outside the AA summary). Export and sign-off remain human
steps.

## Commands

```sh
# Collect the Accessibility + atag sample
acr-evidence collect \
  --manifest config/drupal-core-atag.json \
  --output reports/drupal-core-atag/collection.json

# Render the evidence report and WAI JSON
acr-evidence atag-report \
  --collection reports/drupal-core-atag/collection.json \
  --output reports/drupal-core-atag
```

Weekly snapshots collect and render ATAG evidence before the multi-target
reports. CI regenerates `atag-report.json`/`atag-evidence.json` from the
committed collection and byte-compares them.

## Relationship to OpenACR

The OpenACR standard’s `authoring-tool` component is not automatically populated.
The OpenACR draft notes link to `../drupal-core-atag/index.html` and state that
ATAG criteria are out of scope for that file. A reviewer may use the ATAG evidence
to inform the authoring-tool component and remarks, but must not copy ATAG
conclusions into a WCAG conformance value.

## Limitations

- The queue currently uses a generic `atag` tag; most issues are component
  candidates or unspecified until Part A/B tags or curated mappings are added.
- The component mapping is editorial triage, not a conformance determination.
- No ATAG evaluation or assistive-technology testing was performed.
- ATAG behaviour can differ between releases; reproduce on the installed target.
- Import into the live WAI ATAG Report Tool was verified; human editing, export and sign-off were not performed.
- The ATAG data is vendored from the WAI ATAG Report Tool under the W3C Software
  Notice and License; see `src/acr_evidence/standards/atag/`.
