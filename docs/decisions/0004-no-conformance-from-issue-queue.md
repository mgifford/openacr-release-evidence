# 0004: Do not derive conformance from issue-queue presence or absence

- **Status:** accepted, 2026-11-12
- **Supersedes in part:** the 2026-11-12 surface-assessment policy that mapped
  known issues to `Partially Supports` and empty assessed surfaces to `Supports`

## Context

The ACR narrative and OpenACR draft previously converted issue-queue state into
conformance terms:

- an active issue on an assessed surface produced `Partially Supports`;
- an assessed surface with no active issue produced `Supports`.

The project's own policy says an issue report is not a reproduction, a closed
issue is not a release fix, and absence of a reported issue is not evidence of
support. The generated values contradicted that policy. Reviewer feedback also
found the resulting labels hard to interpret.

## Decision

1. No adherence value is generated from issue-queue presence or absence.
2. A reported issue is listed as a potential barrier in the report, not as a
   conformance finding.
3. `Not Evaluated` is the default for every non-`Not Applicable` criterion in the
   narrative.
4. The OpenACR draft leaves non-`Not Applicable` adherence values unset. A
   `component_scope` extension marks Web and Authoring Tool `unassessed`.
5. `Not Applicable` still requires a documented product-scope basis.
6. `Does Not Support` still requires explicit broad-failure evidence in the
   policy and is not emitted automatically.
7. A human reviewer may record `Supports` or `Partially Supports` only with
   reviewed evidence. The automated pipeline does not emit either.

## Consequences

- The generated OpenACR draft no longer looks like a partially completed
  conformance evaluation. It is a scope-validated skeleton with unset values.
- The narrative is longer in `Not Evaluated` rows; that is intentional honesty.
- Issue-queue evidence remains available in the report, criterion-evidence
  ledger and machine-readable artifacts.
- The existing schema, catalog and `evidence_digest` algorithm are unchanged.
- `openacr-validate --strict` still fails by design until a human reviewer
  completes the values and replaces the placeholder author.

## Tests

- `tests/test_surface_assessment.py`
- `tests/test_openacr_standard.py`
- `tests/test_acr_narrative.py`
- `tests/test_report.py`

## Documentation

- `docs/CONFORMANCE-POLICY.md`
- `docs/EVIDENCE-MODEL.md`
- `docs/REPORT-TERMINOLOGY.md`
- `docs/REPORT-USABILITY-REVIEW.md`
- `AGENTS.md`
