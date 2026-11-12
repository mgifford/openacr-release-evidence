# Session learnings

Date: 2026-11-12

This is a durable record of decisions, corrections and process lessons from the
session that added the criterion-evidence, impact-data and human-impact layers.
It is context for maintainers, not a replacement for `AGENTS.md`, `TODO.md` or
the current code.

## Durable product decisions

1. **The issue queue is a known-barrier register, not a conformance result.**
   A tagged issue is reported evidence; it does not prove reproduction or a
   criterion-level outcome.
2. **Surface assessment policy is explicit.**
   `config/surface-assessments.json` records the project-asserted Web/Authoring
   assessment. Known issue → Partially Supports; assessed surface with no known
   issue → Supports; documented feature absence → Not Applicable; Does Not
   Support only with explicit broad-failure evidence.
3. **Absence alone is not support.** Supports depends on the declared surface
   assessment, not on an empty issue queue or a clean automated scan.
4. **N/A needs a factual basis.**
   Electronic Documents/Software and 1.2.1/1.2.3/1.2.4/1.2.5/1.4.2 are excluded
   for documented feature/product absence, not because no issue was tagged.
5. **N/A rationale belongs once in the introduction and audit table**, not
   repeated in every criterion row. Criterion-specific media explanations remain
   with their rows.
6. **Every WCAG 2.2 criterion needs a user-impact description.**
   The impact dataset has 86 active records plus historical 4.1.1. Generic
   descriptions are independent of Drupal issues and release evidence.
7. **Imported mappings remain provisional.**
   Section 508 covers 36/86 criteria. EN 301 549 relationships are pending. A
   missing crosswalk is not evidence of no impact.
8. **Global statistics are context, not Drupal estimates.**
   WHO figures are overlapping populations with definitions and limitations.
   Never multiply them by installations, page loads or users.
9. **Automated coverage is partial evaluation.**
   Axe/ACT mappings show where checks are possible; `result: not-recorded` is not
   a pass. 1.3.2 has no ACT/axe mapping. Guidepup is a separate behavioral method,
   not an assumed result.
10. **External Core Lab evidence is not target verification.**
    A reproduction on a pinned lab commit does not prove the selected release.
11. **OpenACR and the ACR remain drafts.**
    No user-impact mapping, issue tag or automated result becomes a formal
    conformance decision automatically.
12. **The report stays static and JavaScript-free.**
    Native anchors, `<details>` and generated navigation are used instead of
    SkipTo or client-side components.

## Corrections made during the session

- The initial evidence/conformance separation overcorrected: every criterion
  became Not Evaluated. That was truthful but not useful. The surface-assessment
  policy was added so known issues produce Partially Supports and assessed
  surfaces can produce Supports.
- A known issue must be **Partially Supports**, not Supports. Supports means the
  criterion is met, not that a barrier is known.
- “No active issue” is not Supports by itself; it needs the declared assessment.
- `Partially Supports` must never be inferred from a tag alone without the
  documented policy and draft caveat.
- 1.3.2 is not covered by axe/ACT; its Support result rests on the assessment, not
  automation.
- 1.4.2 belongs with the native-media N/A scope.
- 4.1.1 is historical in WCAG 2.2 and must not appear as active.
- The non-WCAG chapter labels needed full names; raw IDs were unhelpful.
- Component-wide N/A text was duplicated in every row and was consolidated.
- External reproduction evidence was initially at risk of being read as target
  verification; it is now explicitly `target_verified: false`.
- Report regeneration must happen after code changes; CI caught stale ACR/ATAG
  artifacts. Always regenerate all target reports and compare.
- Branch work must start from the latest `main` and check open PRs first; several
  conflicts came from regenerated report files.
- OpenACR `not-evaluated` is rejected for A/AA; use unset/omitted adherence where
  appropriate and keep documented N/A values.
- A schema-valid OpenACR file can still be incomplete; validation is not review.

## Process lessons

- Read `AGENTS.md`, `ACCESSIBILITY.md`, current code and open PRs before editing.
- Keep generated evidence and generic impact data separate.
- Preserve issue IDs, source URLs and release applicability.
- Use deterministic checked-in data and offline generation.
- Run tests, regenerate reports, validate OpenACR, run axe/reflow and compare
  artifacts before opening a PR.
- Do not add a client-side dependency for navigation that native HTML can provide.
- Record uncertainty in data and report wording; do not smooth it away.
- Update `TODO.md` when work is deferred rather than implying completion.

## Still open

See [`TODO.md`](../TODO.md), especially:

- human review of all 86 impact descriptions;
- remaining Section 508 and EN 301 549 crosswalks;
- target-specific reproduction;
- Drupal CMS and LocalGov pilots;
- AI provider evaluation and human judge;
- reconciliation of historical audit language.
