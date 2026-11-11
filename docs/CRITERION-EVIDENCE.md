# Criterion evidence beyond the issue queue

The active issue queue can establish **reported barriers**. It cannot establish
that a WCAG criterion is met. Absence of a tagged issue is not evidence of
Supports.

## States

| State | Required evidence |
|---|---|
| Reported barrier, unverified | Active issue-queue reports, separated by Web/Authoring Tool; no conformance result |
| Supports | Positive human-reviewed evidence: a test, code audit or documented implementation with a source and date |
| Not Applicable | A documented product-scope decision showing that the content or feature is absent |
| Not Evaluated | No positive evidence and no issue-queue evidence; a review gap |
| Does Not Support | Reviewed evidence that the majority of relevant functionality fails |

The issue-queue pipeline does not assign Supports, Partially Supports, Not
Applicable or Does Not Support. It records reported barriers and candidate
criterion relationships. A formal term requires the reviewed evidence below.

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

The Not Evaluated set is not a failure list. It is a review backlog. Prioritise:

1. criteria that apply to core web and authoring surfaces;
2. criteria with high disability impact;
3. criteria that may be Not Applicable because the feature is absent;
4. media criteria only where a player, live media or audio feature exists.

For Drupal Core, 1.2.1/1.2.3/1.2.4/1.2.5 are currently Not Applicable because the
relevant media player/live feature is absent. 2.2.1/2.2.2/2.3.1 are Not Evaluated
when no active issue is tagged; that is not a claim that they do not apply.

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

A review dashboard should show Supports, Partially Supports, Not Applicable and
Not Evaluated counts for each WCAG principle. This makes the positive evidence
visible without turning the issue count into a conformance score.

## Boundaries

- Supports requires positive evidence, not issue absence.
- Not Applicable requires a documented scope decision.
- The issue queue remains useful for finding barriers and prioritising review.
- Every final term remains a human publication decision.
