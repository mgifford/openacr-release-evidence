# Report usability validation

**Status: internal Phase 6 validation completed 2026-11-12.**

This is an expert, scripted validation of the revised report structure. It is
**not** a study with representative disabled readers, and it is not a WCAG
conformance audit. It checks whether the information architecture supports the
tasks the reports claim to support and records the accessibility checks that
were actually run.

Build under test: `drupal-core-12.0.0-beta2` and `drupal-core-11.4.12` generated
reports from the 2026-11-10 collection snapshot. Browser: Google Chrome
157.0.8103.52 on macOS.

## What was checked

### Reading tasks

Each task was performed against the generated static pages with no JavaScript.

| Task | What the reader needed to find | Result | Evidence |
| --- | --- | --- | --- |
| T1. Understand the release | Release identity, how many issues probably apply, whether any problem is verified, and what to do next | **Pass** | Overview summary says 30 probably affect beta2, 0 verified problems, 402 not determined, and gives audience-specific actions |
| T2. Explain “not determined” | Why 402 issues are not determined, without reading the methodology | **Pass** | Selecting “Needs checking” shows only that group; the reason box reports 402, with 394 basic metadata records and 8 reported after the release was cut |
| T3. Read one issue | Separate Drupal.org status from release applicability, plus a next step | **Pass** | `drupal:3636027` shows “Drupal.org status: Needs review”, “Applies to this release?: Not yet determined”, a reason and a next step |
| T4. Compare component changes | What left or changed between two releases | **Pass** | Sources page compares beta2 with alpha1: Claro and Olivero removed, Default Admin experimental → stable, default/admin theme changed |
| T5. Follow a moved component | Where Claro/Olivero went and the evidence | **Pass** | Lineage table says “Removed from Core in 12.0.0-beta1”, links the issue/commit evidence, and marks the record unreviewed |
| T6. Decide whether a fix is verified | Whether any issue has a verified fix in beta2 | **Pass** | The fix-included group is `(0)`, has an explicit empty state, and the summary says no fix has been tested and confirmed |

T6 deliberately checks the honest empty state. The active snapshot has no
`confirmed-fixed` finding for beta2; a test fixture with one exists in
`tests/test_report.py` for the fix-included label.

### Accessibility checks

| Check | Result | Notes |
| --- | --- | --- |
| axe-core 4.x, WCAG 2.0/2.1/2.2 A/AA tags | **0 violations** on all six pages at 1280 px and at 320 px | Automated coverage only, not conformance |
| 400% reflow equivalent | **Pass** | 320 CSS px viewport on `index`, `issues`, `criteria`, `sources`, `method` and `acr`; `scrollWidth == clientWidth`, no page-level horizontal scroll. Wide tables scroll inside labelled regions |
| Keyboard: skip link | **Pass** | First Tab on the overview focuses “Skip to main content” (`href="#main"`) |
| Keyboard: page navigation | **Pass** | Tab order is skip link → breadcrumb → page navigation → supporting outputs → content; no trap |
| Keyboard: issue filter | **Pass** | Arrow keys move within the radio group; selecting “Verified” hides the other groups in the CSS-only filter |
| Keyboard: disclosure | **Pass** | Enter opens the first `<details>` on the issues page |
| Accessible names | **Pass (structure)** | Accessibility tree exposes names such as “All issues (432)”, “Probably affects this release (30)” and “Needs checking (402)” for the filter radios |
| Reduced motion | **Pass** | With `prefers-reduced-motion: reduce`, `scroll-behavior` computes to `auto` |
| Forced colors | **Partial** | Emulation matches `(forced-colors: active)` and borders remain visible. A real Windows forced-colors/high-contrast check was not performed |
| Screen reader | **Not performed** | No VoiceOver/NVDA/JAWS session was run. The accessibility tree was inspected only |

## Problems found and fixed

1. **The overview linked “component inventory and sources” to the issue
   component index, not the new component history.** Fixed: the summary now
   links directly to `sources.html#component-changes` with the label “See the
   component inventory, changes and lineage”.
2. **A full component jump list added 80 tab stops before the inventory table.**
   Fixed: the jump list is now a native `<details><summary>Jump to a
   component</summary>` disclosure, so it adds one keyboard stop and opens on
   demand.
3. **Forced-colors borders were not explicitly declared for the filter, group
   and jump-list containers.** Fixed by adding them to the existing
   `@media(forced-colors: active)` border rule. A real Windows check remains.

## Remaining validation gaps

- No representative disabled readers participated. The task results show that
  the information is findable; they do not prove comprehension for the target
  audiences.
- No real screen-reader session was run. The AX-tree check is structural.
- Forced-colors was emulated, not tested on Windows high-contrast mode.
- 400% was represented by a 320 CSS px viewport, not a physical browser zoom
  session at 400%.
- `issues.html` remains large; the filter groups help, but the page still
  contains every canonical issue record.
- Component changes compare with the previous declared target that has an
  inventory. They do not show every intermediate release.
- Component lineage records remain `unreviewed`.

## Next step

Run the same six tasks with at least one Drupal maintainer, one site builder and
one accessibility evaluator, then record their comprehension and navigation
problems. After that, add the changed-file-path provenance step so some
issue-to-component associations can move from candidate to
`verified-source-code`.
