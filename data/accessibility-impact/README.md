# Accessibility impact knowledge layer

This directory is a reusable, machine-readable description of who may be affected
by each WCAG 2.2 success criterion and what barrier they may encounter.

It is **not** a WCAG conformance dataset and **not** a Drupal issue dataset. It is
editorial synthesis linked to authoritative sources. Drupal release evidence is
kept separate.

## Layout

```text
schema/
  criterion-impact.schema.json
  groups.json
wcag/2.2/
  criteria.json          # 86 active WCAG 2.2 criteria
  historical.json        # 4.1.1, removed in WCAG 2.2
mappings/
  section508-fpc.json
  en301549-v3.2.1.json
  en301549-v4.1.1.json
sources.json
```

## Status and provenance

- All current descriptions are `proposed`, not reviewed.
- Each record has a W3C Understanding link.
- Section 508 categories come from the CivicActions/Section508.gov crosswalk.
- EN 301 549 files are present but `pending`; no clause relationship is asserted.
- No text is copied wholesale from W3C documents.

## Controlled vocabulary

`schema/groups.json` defines functional-need and affected-group identifiers.
Descriptions use those identifiers rather than free-text medical labels.

## Regenerate

```sh
PYTHONPATH=src python3 scripts/build_impact_data.py
PYTHONPATH=src python3 scripts/impact_coverage.py
```

The build is deterministic and offline. Generated files are checked in.

## Use outside this project

Consumers can read `wcag/2.2/criteria.json` directly or use
`acr_evidence.impact.get_criterion_impact()`. The data has no Drupal dependency.

## Limits

- A record is a proposed impact description, not a conformance result.
- A missing Section 508 category means the crosswalk has not established one.
- A pending EN 301 549 relationship is not evidence of no relationship.
- The descriptions need human accessibility review.
