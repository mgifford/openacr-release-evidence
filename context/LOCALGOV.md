# LocalGov Drupal — ACR and AI context

**Status: human-maintained scope guidance, not evidence.**

## Product

LocalGov Drupal is a Drupal distribution for local government websites, built
from Drupal Core plus LocalGov modules, themes, recipes and contributed
components. Its ACR covers the distribution and the services it ships.

## Relationship to Drupal Core

- Drupal Core is a parent dependency; its ACR is not inherited.
- LocalGov-specific content types, navigation, service pages, search and
  editorial workflows need their own evidence.
- A Core or contrib issue affects this ACR only if the component is in the
  evaluated distribution.

## Component treatment

Web and Authoring Tool are normally applicable. Electronic Documents and
Software are normally Not Applicable unless the distribution ships a distinct
document authoring/management product or installed software. Review the actual
distribution before confirming.

## Authoring and issue references

Apply the `/admin`, `/user` and login/reproduction rules. Local government
authors may have different roles and publishing workflows; record the role and
surface. Reference the source project, issue ID/URL and the LocalGov release.

Do not describe council content or a public service page as an authoring-tool
result unless the barrier occurs in the authoring interface.

## ACR template and AI rules

Use [`../templates/drupal-acr-template.md`](../templates/drupal-acr-template.md).
Distinguish LocalGov Drupal, Drupal Core and contrib components in every claim.
Do not inherit a Core or contrib ACR result, and do not invent a council
deployment, content set or reviewer.

## References

- <https://www.section508.gov/test/>
- <https://ictbaseline.access-board.gov/>
- <https://www.section508.gov/buy/authoring-tools/>
