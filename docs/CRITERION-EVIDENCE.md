# Criterion evidence beyond the issue queue

The active issue queue can establish **reported barriers**. It cannot establish
that a WCAG criterion is met. Absence of a tagged issue is not evidence of
Supports.

## States

| State | Required evidence |
|---|---|
| Partially Supports | Reviewer-recorded partial evidence; not produced automatically from an issue report |
| Supports | Reviewer-recorded positive evidence: a test, code audit or documented implementation with a source and date; not produced from an empty queue |
| Does Not Support | Reviewed evidence that the majority of relevant functionality fails; not emitted automatically |
| Not Applicable | A documented product-scope decision showing that the content or feature is absent |
| Not Evaluated | No reviewed conformance evidence is recorded; this is the default for every non-Not-Applicable criterion |

The issue-queue attestation applies the declared surface assessment: known issue
-> potential barrier, not a conformance result; no known issue on an assessed
surface -> Not Evaluated, not Supports;
documented feature absence -> Not Applicable. Does Not Support requires explicit
broad-failure evidence. The evidence ledger records the underlying barriers.

## Evidence record

A future criterion-evidence ledger should record:

```json
{
  "criterion": "2.4.7",
  "target": "drupal-core-11.4.12",
  "state": "supports",
  "basis": "manual-test",
  "summary": "Focus indicators verified on the declared admin configuration.",
  "source_url": "https://...",
  "observed_at": "2026-11-11",
  "reviewer": "Named reviewer",
  "review_status": "reviewed",
  "limitations": "Declared configuration only."
}
```

No record may be generated from an empty queue or a model response.

## What to review first

The policy backlog is not a failure list. Prioritise:

1. criteria that apply to core web and authoring surfaces;
2. criteria with high disability impact;
3. criteria that may be Not Applicable because the feature is absent;
4. media criteria only where a player, live media or audio feature exists.

For Drupal Core, 1.2.1/1.2.3/1.2.4/1.2.5 are Not Applicable because the relevant
media player/live feature is absent. 2.2.1/2.2.2/2.3.1 remain Not Evaluated when
no reviewed evidence is recorded; an empty issue queue is not a pass.

## Automated evaluation coverage

Axe-core and W3C ACT rule mappings are treated as **partial evaluation
coverage**, not as a criterion-level result. They show that some part of a
criterion can be checked automatically; they do not show that the whole
criterion passes.

The mapping is vendored from [`mgifford/wcag-spine`](https://github.com/mgifford/wcag-spine)
into `config/wcag-automation-coverage.json` with its source date and axe-core
version. Each criterion-evidence record carries:

- `axe_rules`;
- `act_rules`;
- `coverage: partial | none`;
- `result: not-recorded`;
- `guidepup: method-available-not-recorded`.

Axe/ACT coverage remains separate from `conformance_result`. A clean axe run is
not a conformance claim. A recorded axe or Guidepup result would need its own
evidence record, target, environment, scope and limitations.

Guidepup can add behavioral screen-reader evidence for keyboard and focus tasks.
It is a separate test method, not an ACT/axe rule and not a mapping that can be
assumed for every criterion. No Guidepup run is claimed in the current snapshot.

## POUR summary

A review dashboard should show Not Applicable and Not Evaluated counts for each
WCAG principle. It must not count issue reports as Supports or Partially
Supports. This makes the positive evidence
visible without turning the issue count into a conformance score.

## Boundaries

- Supports requires positive evidence, not issue absence.
- Not Applicable requires a documented scope decision.
- The issue queue remains useful for finding barriers and prioritising review.
- Every final term remains a human publication decision.

## N/A claims need scrutiny

A Not Applicable result is a factual product-scope claim. It is not an empty-queue
fallback. The ACR lists each N/A claim with its basis and a review state.

Current N/A claims:

- Electronic Documents: no standalone electronic-document product.
- Software: no packaged non-web software product.
- Web/Authoring 1.2.1/1.2.3/1.2.4/1.2.5/1.4.2: no native media player,
  live-media feature or automatic audio control in Core.

Each claim must be checked against the declared product and confirmed by a human.
