# Developer evidence index

Each target report includes a static component index and per-issue developer
state. This is an index over collected evidence, not a severity ranking or a
remediation assignment.

## Component index

Findings are grouped by the component recorded on Drupal.org. For each component
the report shows:

- all issue IDs and links to their canonical anchors;
- likely-affected count;
- unknown applicability count;
- issues with merge requests;
- issues still needing target reproduction.

The component name is the tracker value. It is not a claim about the responsible
team or source file.

## Per-issue state

The issue index and issue records add:

- **Next action** — collect evidence, reproduce, review a merge request, verify a
  fix’s behaviour, or resolve applicability;
- **Verification** — needs target reproduction, external lab evidence, or an
  external reproduction that is still not target-verified.

These are derived from collected fields only. The report does not invent source
files, code ownership, severity or fix status.

## Example actions

| Evidence state | Next action |
|---|---|
| Metadata-only inventory | Collect comments, MRs and commit evidence |
| MR exists, fix not contained | Review merge request and reproduce |
| MR exists, fix contained | Verify fix behaviour on target |
| Likely affected, no MR | Reproduce on target |
| Unknown applicability | Resolve applicability and evidence |

## Boundaries

- A merge request is not proof of a fix.
- Commit inclusion is not behavioural verification.
- External Core Lab reproduction is not target verification.
- Missing evidence is not a failed test.
- The issue tracker remains the source of truth for ownership and priority.
