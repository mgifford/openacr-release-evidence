# Accessibility statement for this project

Target: WCAG 2.2 Level AA. This is an **intent and work plan**, not a conformance
claim. The generated static report uses semantic headings, lists, tables with
captions, native links and `<details>`, visible focus styles, system colours, no
colour-only status and no JavaScript requirement.

## Automated verification performed (2026-11-08)

- axe-core, Chromium headless, 1280 px: **0 violations** on the landing page,
  the complete matrix page, the Drupal Core 12.0.0-alpha1 target report, the
  ACR narrative and the ATAG 2.0 authoring evidence report.
- 320 CSS px viewport: no horizontal scrolling (`scrollWidth` = 320) on the
  landing page, matrix page, target report, ACR narrative and ATAG report.
  Wide tables are in focusable scroll regions.
- The release finder uses CSS-only radio filters; all five release cards remain
  in the document, and all are visible without CSS `:has()` support. The exact
  version index remains usable without JavaScript.
- No `<script>` is present in the generated homepage, matrix, target report,
  ACR or ATAG report. JavaScript payload is zero. The cross-release matrix is a
  two-dimensional data table in a focusable, horizontally scrollable region;
  the page itself does not overflow.
- Keyboard: the skip link is the first focusable item and moves focus to
  `<main>` (`tabindex="-1"`); native radio filters, links, tables in focusable
  scroll regions and `<details>` all work without a script.
- JavaScript disabled: the release finder, all five release cards, all 428 issue
  records, the issue/criterion indexes and the complete matrix remain in the
  HTML; no script is required. The explorer remains a separate legacy page.
- Internal anchors: all matrix/report anchors resolve; headings do not skip
  levels; tables have captions and header scopes; the ATAG report uses lists
  rather than a wide table.
- 158 offline tests pass, including release-finder, matrix-preservation,
  target-policy, report-index and ACR-navigation tests.

These results do **not** establish conformance. axe-core covers only a subset of
WCAG and cannot judge usefulness, focus order, reading order or real assistive
technology behaviour.

## Not yet tested

- Screen-reader testing (NVDA/Firefox, VoiceOver/Safari).
- Manual keyboard testing across browsers and platforms.
- Real browser zoom (320 px CSS reflow was simulated; 400% equivalent).
- Forced-colors/high-contrast and reduced-motion testing on the report.
- Dynamic updates and error states in the older JavaScript explorer.
- Matrix scrolling with a real assistive technology (keyboard scrolling in the
  focusable region was checked, not screen-reader table navigation).
- The assessed Drupal 11.4.12 release itself; this project does not claim to have
  tested Drupal’s accessibility.
- Manual completion and sign-off of the ACR narrative; every criterion is
  still `Not Evaluated`.
- Commit, comment and merge-request evidence for the 398 metadata-only inventory
  issues; their records are source/status/component/version only.
- Live WAI ATAG Report Tool editing/export and release-scoped ATAG
  applicability (import was verified), and the ATAG report’s screen-reader
  navigation.

Before production: test the above, record results and outstanding issues in the
tracker, and add an independently accessible reporting route. The UI must not
require colour or charts to understand evidence statuses.

Accessibility issues should identify the tested environment and reproduction
steps and be included in the same public prioritisation workflow as other bugs.
