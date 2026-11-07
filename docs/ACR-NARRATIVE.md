# ACR narrative

Each target exports:

- `acr.html` — static, no-JavaScript narrative
- `acr.md` — editable Markdown source

This is a human-readable companion to the validated OpenACR YAML. It follows the
shape of an ACR: product information, term definitions, scope and method,
executive summary, WCAG 2.2 A/AA remarks, non-WCAG chapters, ATAG separation,
reviewer actions, limitations and sources.

## What it does not do

It assigns **no ACR result**. Every criterion is **Not Evaluated** until a named
reviewer completes the evaluation. Issue counts are described as triage evidence;
they are never converted into `Supports`, `Partially Supports` or
`Does Not Support`.

The narrative does **not** claim:

- that a criterion is met because no issue is tagged;
- that an issue count is a severity or conformance score;
- that an issue was reproduced against an installed Drupal target;
- that manual, keyboard, screen-reader, zoom or assistive-technology testing was
  performed;
- that hardware, packaged software, functional-performance or support
  documentation was evaluated.

## Structure

1. **Product information** — product, version, target ref, support status,
   report date, draft status, placeholder reviewer, assessment ID and standards
   baseline.
2. **ACR result terms** — definitions for Supports, Partially Supports, Does Not
   Support, Not Applicable and Not Evaluated. Only Not Evaluated is used.
3. **Scope and method** — active statuses, full-queue pagination, detailed vs
   metadata-only inventory, no reproduction, no AI.
4. **Executive summary** — active issue counts, status distribution, largest
   explicitly tagged criterion clusters and unmapped issues.
5. **WCAG 2.2 Level A and AA** — one row per catalog criterion with:
   - criterion number and title;
   - level;
   - active issue evidence count and detail level;
   - draft result (`Not Evaluated`);
   - remarks and explanations with statuses, target evidence states, examples
     and the explicit warning that this is not a conformance result.
6. **AAA** — outside the declared AA target; reviewer must decide whether to
   evaluate or record a scope rationale.
7. **Functional performance, hardware, software and support documentation** —
   outside the web issue-evidence method’s coverage; reviewer must evaluate or
   mark Not Applicable with a rationale.
8. **ATAG** — separate standard; links to the ATAG evidence, never copied into a
   WCAG criterion.
9. **Review actions** — collect missing evidence, verify the product, select each
   ACR result, complete reviewer identity and approval, remove the draft status.
10. **Limitations and sources** — active-only scope, no reproduction, inventory
    limits, source links.

## Relationship to OpenACR and ATAG

- **OpenACR YAML** is the machine-readable, schema/catalog-validated draft. It
  currently contains all 182 criteria with no adherence values.
- **ACR narrative** is the human-readable explanation for reviewers. It does
  not change the YAML or supply a term.
- **ATAG evidence** is a separate authoring-tool report. It is not part of the
  ACR WCAG chapters.

All three must be reviewed by a person. A schema-valid file or a complete
narrative is not a conformance claim.

## Review workflow

1. Read the executive summary and scope.
2. For each criterion with active issues, open `index.html#issues` and review the
   source issues.
3. For metadata-only inventory issues, collect comments, merge requests and
   target evidence before relying on them.
4. Verify the criterion against the installed product, with the declared scope.
5. Select the ACR result and write a specific remark that names the evidence and
   the limitation.
6. Replace the placeholder reviewer and complete the approval record outside the
   generated draft.
7. Remove the draft statement only after independent review and sign-off.

## References

The structure follows common ACR reporting practice; **OpenACR is the
machine-readable format** and the schema/catalog pinned in this repository.

- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [GSA OpenACR](https://github.com/GSA/openacr)
