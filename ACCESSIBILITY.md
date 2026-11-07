# Accessibility statement for this project

Target: WCAG 2.2 Level AA. This is an **intent and work plan**, not a conformance
claim. The generated static report uses semantic headings, lists, tables with
captions, native links and `<details>`, visible focus styles, system colours, no
colour-only status and no JavaScript requirement.

## Automated verification performed (2026-11-07)

- axe-core 4.13.0, Chromium headless, 1280 px: **0 violations** on the landing
  page, all five Drupal Core target reports and the synthetic explorer.
- 320 CSS px viewport: no horizontal scrolling (`scrollWidth` = 320) on the
  landing page, target reports and explorer. The cross-release matrix is a
  two-dimensional data table in a focusable, horizontally scrollable region;
  the page itself does not overflow.
- Keyboard: the skip link moves focus to `<main>` (`tabindex="-1"`); `<details>`
  toggles with Enter; the report has no script.
- JavaScript disabled: the report renders its full content; the explorer shows a
  `<noscript>` message and links to `evidence.json`.
- Internal anchors: all matrix/report anchors resolve; headings do not skip
  levels; tables have captions and header scopes.
- 70 offline tests pass, including landing/matrix and target-policy tests.

These results do **not** establish conformance. axe-core covers only a subset of
WCAG and cannot judge usefulness, focus order, reading order or real assistive
technology behaviour.

## Not yet tested

- Screen-reader testing (NVDA/Firefox, VoiceOver/Safari).
- Manual keyboard testing across browsers and platforms.
- 200% and 400% browser zoom (320 px CSS reflow was simulated).
- Forced-colors/high-contrast and reduced-motion testing on the report.
- Dynamic updates and error states in the older JavaScript explorer.
- Matrix scrolling with a real assistive technology (keyboard scrolling in the
  focusable region was checked, not screen-reader table navigation).
- The assessed Drupal 11.4.12 release itself; this project does not claim to have
  tested Drupal’s accessibility.

Before production: test the above, record results and outstanding issues in the
tracker, and add an independently accessible reporting route. The UI must not
require colour or charts to understand evidence statuses.

Accessibility issues should identify the tested environment and reproduction
steps and be included in the same public prioritisation workflow as other bugs.
