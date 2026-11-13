# Accessibility issue provenance

**Status: deterministic changed-path association is implemented for the
detailed merge-request subset. Inventory-only issues still have no changed-path
evidence, so most associations remain metadata or title based.**

This page explains how the project decides which component an issue belongs to,
and why that decision is not the same as release applicability or a conformance
result.

## Why component association is hard

Drupal.org gives every issue a `component` field, but the field is a tracker
category, not a stable product identity. Examples in the 2026-11-10 collection:

- 25 issues use the generic `Admin theme` component. That could mean Claro,
  Default Admin, Gin or another admin theme.
- A Claro landmark issue is filed under `markup`, not `Claro theme`.
- A Default Admin focus issue is filed under `Admin theme`.
- A Gin issue may be copied to a new Core issue with a different component.
- A removed theme's issues stay in the Core queue with their old status.

The component field is a useful signal. It is not proof.

## Signals, strongest to weakest

| Signal | Association level | What it proves |
| --- | --- | --- |
| Changed file path in the issue's merge request or commit, e.g. `core/themes/default_admin/...` | `verified-source-code` | The change touches that component's code. It does not prove the issue reproduces in a release. |
| Tracker component exactly matches a machine name, or a curated unambiguous alias | `explicit-metadata` | The source tracker identifies the component. It can still be a cross-component issue. |
| Issue title or description explicitly names the component | `strong-candidate` | The text points to the component. Needs source review. |
| Generic component label or keyword only | `weak-inferred` | A lead. Do not use for a report conclusion. |
| No usable signal | `unknown` | No association. |

LLM output is never treated as a verified association. If a model suggests one,
it is a candidate that a human must check against source.

## Implemented helper

`src/acr_evidence/provenance.py`:

```python
from acr_evidence.provenance import associate_issue

result = associate_issue(
    issue,
    changed_paths=["core/themes/default_admin/css/base/elements.css"],
    known_components={("theme", "default_admin"), ("theme", "claro")},
)
```

It returns zero or more associations and a primary association. An issue that
spans two components gets two associations and **one** issue identity. The
helper does not set release applicability, severity or conformance.

Path mapping is deliberately narrow:

- `core/modules/<name>/` → module `<name>`
- `core/themes/<name>/` → theme `<name>`
- `core/profiles/<name>/` → profile `<name>`
- `core/lib/...` → no component attribution

## Candidate provenance record

```json
{
  "issue_id": "drupal:3636027",
  "source_url": "https://www.drupal.org/project/drupal/issues/3636027",
  "associations": [
    {
      "type": "theme",
      "component": "default_admin",
      "level": "strong-candidate",
      "basis": "title-mention",
      "evidence": ["title:default_admin"]
    }
  ],
  "primary": {
    "type": "theme",
    "component": "default_admin",
    "level": "strong-candidate",
    "basis": "title-mention",
    "evidence": ["title:default_admin"]
  },
  "multiple": false
}
```

The association level is not a probability. It is a description of the evidence
type.

## Investigation samples

These samples were checked during the component-history investigation. They show
why issue status and component labels are not enough.

| Issue | Tracker status | Component field | Evidence found | Association | Applicability |
| --- | --- | --- | --- | --- | --- |
| [drupal:3348552](https://www.drupal.org/project/drupal/issues/3348552) Olivero pager ellipsis | Needs review | `theme system` | Title and description name Olivero; Core 11.4.12 and contributed Olivero 2.0.0 pager templates both keep the ellipsis markup | strong candidate | Probably affects 10.6.21, 11.4.12 and 12.0.0-alpha1; not in Core at beta2; likely in contributed Olivero 2.0.0, unverified |
| [drupal:3159933](https://www.drupal.org/project/drupal/issues/3159933) Claro status landmark | Needs work | `markup` | Title names Claro; Core 11.4.12 template uses `role="contentinfo"`; contributed Claro 3.0.0 uses alert/status roles | strong candidate | Probably affects 10.6.21–12.0.0-alpha1 Core; not in Core at beta2; possibly corrected in contributed Claro 3.0.0, unverified |
| [drupal:3636027](https://www.drupal.org/project/drupal/issues/3636027) active local task contrast | Needs review | `Admin theme` | Issue says it was opened in the Gin queue as work item 3506311; Default Admin is the Core successor | strong candidate; lineage explains why Default Admin is the successor, but the Core issue still needs reproduction | Probably affects 12.0.0-beta2; Gin relationship noted, not inherited |
| [drupal:3636643](https://www.drupal.org/project/drupal/issues/3636643) target size | Active | `Admin theme` | Issue says it was opened in the Gin queue as work item 3506334; no MR collected | strong candidate | Probably affects 12.0.0-beta2; no reproduction |
| [drupal:3619127](https://www.drupal.org/project/drupal/issues/3619127) sidebar error links | Needs review | `Admin theme` | Issue body describes Default Admin's sidebar; MR 16895 is open | strong candidate | Probably affects 12.0.0-beta2; not reproduced |
| [drupal:3621109](https://www.drupal.org/project/drupal/issues/3621109) skip link contrast | Closed (fixed) | `Admin theme` | Fix commits exist on 11.4.x and 12.0.x; containment differs by branch | explicit metadata + commit containment | Fix included in 11.4.12 and 12.0.0-beta2 via different commits; behaviour not tested |

`probably affects` is the project's `likely-affected` state. None of these samples
is a verified problem. None is a conformance result.

## Cross-component issues

Some issues genuinely span modules or themes:

- a form API issue that affects every theme's form rendering;
- an Olivero pager template that overrides a Views/system template;
- a Claro CSS rule copied into Default Admin;
- a dialog issue in `javascript` that manifests in several themes.

The model keeps one issue record and multiple associations. Do not duplicate the
issue in the report just because it touches several components. The report should
show the primary association and list the others as related components.

## What is available now

`acr-evidence issue-provenance` reads the public GitLab changes API for every
merge request already recorded in the collection. It stores only public `core/`
file paths, not diffs or file contents, and writes
`reports/<target>/issue-provenance.json`.

The 2026-11-10 snapshot produced:

- 33 issues with merge requests;
- 46 merge requests;
- 33 issues with at least one changed core path;
- 29 `verified-source-code` associations and 4 `strong-candidate`
  associations.

Test-only paths are excluded from association: a change under
`core/modules/foo/tests` often means a test covers the issue, not that the
defect belongs to `foo`. The raw paths remain in the provenance JSON for audit.

The release report shows the primary changed-path associations in each detailed
issue record and links to the provenance JSON. It labels the field
“Changed-path association (evidence only)”.

## What this does not establish

- It identifies code that changed, not the release where the barrier exists.
- Inventory-only issues have no changed-path evidence; they still need comments,
  merge requests and target testing.
- A title or description mention remains a strong candidate, not verified code.
- A merged merge request is not proof that the barrier is resolved.
- The association is target-independent; `present_in_bundled_release` and
  `installed_by_standard_profile` are separate flags in the target artifact.

## Next steps

1. Add a reviewed component alias map for tracker labels.
2. Use the provenance artifact in criterion evidence and component filters.
3. Collect contributed-project merge requests for moved components.
4. Keep the raw diffs private; only paths and derived associations are public.
5. Re-run the provenance command after the collection changes; the cache is
   six hours and `--refresh` forces retrieval.
6. Keep one issue identity across components.
