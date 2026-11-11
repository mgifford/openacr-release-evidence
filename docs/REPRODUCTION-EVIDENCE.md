# Reproduction evidence

This layer keeps documented reproductions separate from active issue reports and
from conformance results.

## External Core Lab evidence

`config/reproduction-sources.json` imports a small set of records from
[Drupal Core Lab](https://github.com/mgifford/drupal-core-lab). Each target
report writes `reproduction-evidence.json` and displays a **Reproduction
evidence** section.

A record is external unless all of these are true:

- it was run against the exact OpenACR target commit;
- the release, profile, modules, themes and configuration are recorded;
- the task, expected behavior, observed behavior and result are recorded;
- the artifacts are available;
- a reviewer has checked the record.

External evidence remains `target_applicability: not-established` and
`target_verified: false`. It never becomes a target conformance result.

## Current example

Drupal Core Lab issue **#3619127** has a documented end-to-end reproduction:

- pinned Drupal Core commit;
- PHPUnit;
- Playwright mouse and keyboard walkthrough;
- axe-core;
- virtual screen reader;
- served-file diff;
- explicit limitations: no real VoiceOver/NVDA pass, one theme, Firefox
  unavailable, draft pending human review.

That evidence is linked in the report as external. It does **not** prove that the
same behavior occurs on `11.4.12` or `12.0.0-alpha1`.

Other imported records are marked `lab-evidence-present-not-reviewed` when the
Core Lab index records a tested commit but no end-to-end result has been reviewed
for this project.

## Target reproduction record

A future target-specific record should add:

- exact release and target commit;
- Drupal installation profile;
- enabled modules and themes;
- browser and screen reader versions;
- user task and reproduction steps;
- expected and observed behavior;
- axe/ACT rule results, if any;
- Guidepup or other screen-reader automation output;
- screenshot/trace/test artifact;
- test date and identity;
- result and limitations;
- reviewer and review date.

Automated tools provide partial evaluation coverage. They do not establish a
complete WCAG criterion result.

## Guidepup

Guidepup can exercise keyboard and screen-reader interaction. A Guidepup run is
target-specific behavioral evidence; it is not an ACT/axe rule and is not assumed
for every criterion. No Guidepup run is claimed until its environment, task,
output and review are recorded.

## Boundaries

- No external record is target verification.
- No reproduction record is automatically a conformance result.
- No fix commit is behavioural verification.
- No issue creation date proves when a barrier was introduced.
- No source reference is invented.
