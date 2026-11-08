# Drupal CMS — ACR and AI context

**Status: human-maintained scope guidance, not evidence.**

## Product

Drupal CMS is a Drupal distribution assembled from Drupal Core plus recipes,
contributed modules, themes and configuration. Its ACR covers the distribution
as shipped, not Drupal Core alone and not every contrib project it contains.

## Relationship to Drupal Core

- Drupal Core is a parent dependency, not a conformance inheritance.
- A Core issue may affect Drupal CMS, but a Core conformance result is not
  automatically a Drupal CMS result.
- A Drupal CMS issue may come from a recipe, module, theme or integration.
- Cite both the distribution and the upstream component when the source is
  upstream.

## Component treatment

Use the same four Section 508 components. Web and Authoring Tool are normally
applicable; Electronic Documents and Software are normally Not Applicable unless
the distribution ships a distinct document or software product. Review the
actual recipe/module set before confirming.

## Authoring and issue references

The Drupal Core authoring rules apply, including `/admin`, `/user` and
login/reproduction steps. Also account for distribution-specific editorial
roles, content types, media and layout tools.

Reference issues with the source project, issue ID/URL and the distribution
version in which the component is shipped. Do not present a Core issue as a
Drupal CMS issue without checking that the component is included.

## ACR template and AI rules

Use [`../templates/drupal-acr-template.md`](../templates/drupal-acr-template.md).
For AI summaries, distinguish:

- **Drupal CMS distribution** — the product being assessed;
- **Drupal Core** — a parent component;
- **contrib recipe/module/theme** — an included component.

Do not carry a parent or component conformance claim into the distribution ACR.
Do not invent the recipe list, version or reviewers.

## References

- <https://www.section508.gov/test/>
- <https://ictbaseline.access-board.gov/>
- <https://www.section508.gov/buy/authoring-tools/>
