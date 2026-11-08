# CKEditor in Drupal — ACR and AI context

**Status: human-maintained scope guidance, not evidence.**

## Product

CKEditor is an authoring tool embedded in Drupal Core's editorial interface.
There are two distinct scopes:

1. **CKEditor upstream** — the editor project and its plugins.
2. **Drupal integration** — the Drupal module, configuration, templates and
   editor plugins shipped with Drupal.

An ACR must state which scope it covers. Drupal Core's ACR treats the CKEditor
integration as part of the **Authoring Tool** component; it does not inherit an
upstream CKEditor ACR.

## Component treatment

| Component | Treatment |
|---|---|
| Web | The rendered content produced through the editor is web content; assess the front-end separately. |
| Electronic Documents | Normally Not Applicable unless the product exports/edits standalone documents. |
| Software | Normally Not Applicable; CKEditor is embedded web authoring software. |
| Authoring Tool | Primary component; the editor UI, toolbar, dialogs, source editing and Drupal integration. |

These are scope recommendations, not final conformance results.

## Authoring and issue references

- `/admin`, `/user` and login/reproduction paths are authoring surfaces.
- The editor UI is authoring even when the resulting content is public web.
- Distinguish an upstream CKEditor issue from a Drupal integration issue.
- Reference the upstream project/issue and the Drupal issue/commit when both are
  involved; do not attribute an upstream-only issue to Drupal Core.
- State the Drupal and CKEditor versions and the plugin set.

## ACR template and AI rules

Use [`../templates/drupal-acr-template.md`](../templates/drupal-acr-template.md).
For AI summaries:

- do not merge upstream CKEditor and Drupal integration findings;
- do not claim that a Drupal Core result covers CKEditor upstream;
- do not invent plugin coverage or editor-version evidence;
- keep the authoring-tool and web boundaries explicit.

## References

- <https://www.section508.gov/test/>
- <https://ictbaseline.access-board.gov/>
- <https://www.section508.gov/buy/authoring-tools/>
- <https://www.access-board.gov/ict/#504-authoring-tools>
