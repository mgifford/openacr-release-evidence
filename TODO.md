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
- [ ] Reconcile Supports/Partially Supports results with the criterion-evidence
      ledger and the known-barrier register.
- [ ] Keep Does Not Support unused unless explicit broad-failure evidence is added.
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

## Documentation

- [ ] Keep `AGENTS.md`, README, `AUDIT.md`, `docs/` and the generated reports
      consistent.
- [ ] Document any publication-policy or JavaScript change before implementing it.
- [ ] Keep the TODO list current; remove completed items rather than accumulating
      stale claims.
