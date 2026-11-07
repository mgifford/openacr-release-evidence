# OpenACR export and human review

Each target report can export a machine-readable **draft** OpenACR YAML file.
The file is validated against the Civicactions/GSA OpenACR 0.1.0 schema and the
pinned VPAT 2.5 WCAG 2.2 + Revised Section 508 catalog.

It is a review skeleton, not an approved ACR.

## Pinned standard

Vendored under `src/acr_evidence/standards/openacr/`:

| Item | Value |
| --- | --- |
| Source | https://github.com/Civicactions/openacr (fork of GSA/openacr) |
| Ref | `ca-main` |
| Commit | `d6d18a93d8b043f7edfec13834f2d6b9557c5dbd` |
| Schema | `openacr-0.1.0.json` |
| Catalog | `2.5-edition-wcag-2.2-508-en.yaml` |
| License | CC0/public domain; W3C data under the W3C license (see vendored `LICENSE.md`) |

Update the vendored files only from a new pinned commit and record the change in
the vendored README.

## Commands

Requires the `openacr` extra (`jsonschema` plus PyYAML):

```sh
python3 -m pip install -e '.[openacr]'

# Export one target
acr-evidence openacr-export \
  --analysis reports/drupal-core-11.4.12/analysis.json \
  --output reports/drupal-core-11.4.12

# Validate an edited file
acr-evidence openacr-validate --file reports/drupal-core-11.4.12/openacr.yaml

# Validate a reviewed, non-draft file
acr-evidence openacr-validate --file reports/drupal-core-11.4.12/openacr.yaml --strict
```

`acr-evidence report` and `acr-evidence multi` run the export automatically and
write:

- `openacr.yaml`
- `openacr-validation.json`

The report page links both files.

## What the draft contains

- A title marked **DRAFT**.
- Product name/version/description from the target.
- A placeholder author:
  - name: `Unassigned reviewer (draft)`
  - email: `reviewer@example.invalid`
- Report and last-modified dates from the evidence artifact.
- Draft notes, honest evaluation methods, legal disclaimer, repository and
  feedback links.
- The pinned catalog name.
- All seven catalog chapters and all **182** catalog criteria, in catalog order.
- Chapter-level draft notes linking the evidence report.
- No `components`, no `adherence` levels and no `not-evaluated` values.
- Extension fields `draft`, `target` and `standard_source` for provenance. The
  0.1.0 schema permits additional properties; the official editor may ignore
  them.

The absence of adherence values is intentional. The evidence pipeline has not
performed a WCAG evaluation, and `not-evaluated` is restricted to AAA in this
catalog. A human must select the applicable components and values.

## Validation

`openacr-validation.json` records:

- JSON Schema validation (`jsonschema`, draft-07).
- Catalog validation: chapter IDs, criterion numbers, component definitions,
  component support per criterion, adherence terms.
- Completeness: every catalog criterion is present.
- Policy: `not-evaluated` is rejected for Level A/AA.
- For `--strict`: `draft: false`, a real reviewer name/email, and populated
  components/adherence for every non-disabled criterion.

A valid draft result means **the document structure is valid**, not that any
accessibility claim is true.

On 2026-11-07 all five target drafts were also checked with the official
`@civicactions/openacr` 0.3.11 CLI using the vendored catalog; each returned
`Valid!`. That is a structural/schema/catalog check, not an accessibility review.

## Human review workflow

1. Open the target report and its `openacr.yaml`.
2. Replace the placeholder author with an accountable reviewer and contact.
3. Review the report’s issue evidence and verification gaps for each criterion.
4. Select applicable components (for Drupal Core web UI, usually `web`).
5. Set `adherence.level` only from the catalog terms:
   `supports`, `partially-supports`, `does-not-support`, `not-applicable`, or
   `not-evaluated` for AAA only.
6. Add remarks under `adherence.notes` explaining the evidence and gaps.
7. Set `draft: false` only after review.
8. Run `acr-evidence openacr-validate --file openacr.yaml`, then `--strict`.
9. Submit the reviewed YAML and report for independent approval. The
   [OpenACR editor](https://gsa.github.io/openacr-editor/) can be used for
   authoring; round-trip import/export compatibility is still to be verified.

A reviewer must not treat a populated file as approved merely because it
validates. Validation checks structure, not truthfulness or test coverage.

## Deliberately not done

- Round-trip import/edit/export in the Civicactions/GSA ACR editor has not been
  tested. The YAML is schema/catalog-valid, but editor compatibility is a
  separate verification step.
- No WCAG conformance values are generated automatically.
- No hardware/software/FPC scope decisions are made automatically.
- The EU catalog is not included; the pinned catalog is WCAG 2.2 + Section 508.
- The GSA ACR Editor currently accepts the 2.1 catalog surface; this 2.2-catalog
  draft may not import there. The Civicactions/GSA CLI validates it, but editor
  round-trip remains a separate verification step.
- ATAG 2.0 is not serialized into OpenACR WCAG chapters. See
  [`docs/ATAG-EVIDENCE.md`](ATAG-EVIDENCE.md); the OpenACR notes link to the ATAG
  report and the `authoring-tool` component is left for human review.
- Parent-linked contributed-project ACRs (Claro, Olivero, Drupal CMS, LocalGov)
  are future work.

## CI and publication

CI installs the `openacr` extra, regenerates each target report and compares the
committed `openacr.yaml`/`openacr-validation.json` byte-for-byte. The Pages
workflow publishes these files with the report. Publication remains a human
decision; the weekly workflow opens a review PR rather than auto-publishing.
