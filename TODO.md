# TODO

Open work for OpenACR Release Evidence. This is a working list, not a promise of
coverage. The generated ACR remains a draft.

## Accessibility impact knowledge layer

- [ ] Human-review all 86 proposed WCAG 2.2 impact descriptions.
- [ ] Resolve overlapping affected-group assignments where one criterion has
      several functional needs.
- [ ] Complete Section 508 FPC crosswalks for the 50 criteria currently marked
      `reviewed-no-mapping`, only where the relationship is defensible.
- [ ] Keep 2.3.1 explicitly linked to photosensitive epilepsy even though the
      legacy FPC crosswalk has no matching category.
- [ ] Verify the Section 508 mapping against the original Section508.gov source.
- [ ] Establish EN 301 549 V3.2.1 clause and functional-performance relationships.
- [ ] Establish EN 301 549 V4.1.1 relationships separately; do not copy V3.2.1.
- [ ] Verify the exact published ETSI editions and distinguish technical editions
      from EU legal harmonisation/citation.
- [ ] Add reviewed provenance for every mapping (source, reviewer, date).
- [ ] Keep all impact records `proposed` until human review is recorded.
- [ ] Add an independent consumer fixture proving the data can be read without
      Drupal-specific code.

## Conformance and ACR

- [ ] Obtain a named human reviewer for `config/surface-assessments.json`.
- [ ] Confirm the project-asserted Web/Authoring assessment basis.
- [ ] Keep every non-Not-Applicable criterion Not Evaluated until a reviewer
      records reviewed evidence; do not derive adherence from issue presence or
      absence.
- [ ] Keep Does Not Support unused unless explicit broad-failure evidence is added.
- [ ] Record a reviewed positive-evidence path before any Supports value is
      emitted.
- [ ] Recheck every N/A claim against the exact product, especially media,
      Electronic Documents and Software.
- [ ] Remove the project-asserted N/A review state only after human sign-off.
- [ ] Reconcile historical `AUDIT.md` statements with the current policy.

## Reproduction and automation

- [ ] Add target-specific reproduction records for a representative sample.
- [ ] Record exact target commit, profile, modules, themes, browser, AT versions,
      task, observed behavior, artifacts and reviewer.
- [ ] Distinguish external Drupal Core Lab evidence from target verification.
- [ ] Run and record axe-core results against the target; do not treat a clean
      scan as conformance.
- [ ] Run and record Guidepup checks for keyboard/screen-reader tasks.
- [ ] Add automated reproduction for at least one complete finding.

## Report usability (2026-11-12 review)

- [x] Separate Drupal.org workflow status from release applicability in the
      report, issue index and issue detail.
- [x] Add a generated plain-language summary with audience-specific next steps.
- [x] Add definitions for reported issue, release applicability, verified
      problem, fix included and not yet determined.
- [x] Remove automatic Supports/Partially Supports from the ACR narrative and
      OpenACR draft.
- [ ] Split the report into overview, issues, sources, method and criteria pages
      while preserving anchors.
- [ ] Add progressive-enhancement filters for applicability, component and
      criterion.
- [ ] Group the issue table by verified / probably affected / needs checking /
      out of scope / fix included.
- [ ] Test the revised summary and labels with representative readers.
- [ ] Record keyboard, screen-reader, 320 px, forced-colors and no-JavaScript
      checks for the revised layout.

## Component history

- [x] Add deterministic release inventory extraction and four exact-tag
      inventories.
- [x] Add curated Olivero/Claro/Gin/Default Admin lineage records.
- [x] Add deterministic issue-to-component association helpers.
- [ ] Collect contributed Olivero, Claro and Gin issue queues.
- [ ] Add reviewed lineage records for module moves, not only themes.
- [ ] Connect component presence and lineage to the release applicability
      classification without inheriting predecessor issues.

## Developer experience

- [ ] Add verified source-file references only where evidence exists.
- [ ] Connect fix commits and merge requests to release applicability.
- [ ] Keep component navigation and restoration actions current.
- [ ] Improve verification-state filtering without JavaScript.

## Products

- [ ] Build the Drupal CMS distribution pilot:
  - exact release and Composer lockfile;
  - included module/theme/recipe inventory;
  - component queue collection;
  - target manifest, reports and ACR;
  - do not inherit Core conformance.
- [ ] Build the LocalGov Drupal pilot with its component queues.
- [ ] Document the generic and Drupal-specific parts of the architecture.

## AI and maintenance

- [ ] Establish the human-reviewed AI evaluation dataset.
- [ ] Compare current Hugging Face and Cloudflare outputs with the same evidence.
- [ ] Add deterministic quality checks and a judge that is not another model-only
      authority.
- [ ] Keep AI out of applicability and conformance decisions.
- [ ] Review `data/accessibility-impact/` when W3C, Section 508 or EN 301 549
      sources change.
- [ ] Regenerate `reports/reference-data-coverage.md` after any data change.

## Session record

- [x] Record the durable decisions and corrections in `docs/SESSION-LEARNINGS.md`.
- [x] Keep the deferred work here rather than implying it is complete.

## Documentation

- [ ] Keep `AGENTS.md`, README, `AUDIT.md`, `docs/` and the generated reports
      consistent.
- [ ] Document any publication-policy or JavaScript change before implementing it.
- [ ] Keep the TODO list current; remove completed items rather than accumulating
      stale claims.
