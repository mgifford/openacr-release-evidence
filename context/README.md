# Drupal ecosystem context for ACR and AI summaries

These files are human-maintained **scope and wording notes**, not evidence.
They tell a reviewer or summarizer how to describe a product in an ACR. The
evidence remains the normalized Drupal collection and issue links.

| File | Product |
|---|---|
| `DRUPAL.md` | Drupal Core |
| `DRUPAL-CMS.md` | Drupal CMS distribution |
| `LOCALGOV.md` | LocalGov Drupal distribution |
| `CKEDITOR.md` | CKEditor in Drupal |

Use one file per product. Do not merge their conformance results. A distribution
or editor that embeds Drupal Core is a separate product with its own scope,
version and ACR.

The reusable ACR shell is [`../templates/drupal-acr-template.md`](../templates/drupal-acr-template.md).

## How the context is used

- It is passed to the optional weekly Hugging Face summary as human-authored
  project context.
- It is a place to record scope, component mapping, terminology and issue
  reference rules.
- It never overrides the deterministic facts or the validator.
- It is not evidence that a criterion is met.
