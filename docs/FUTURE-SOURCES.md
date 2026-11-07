# Deferred source integrations

**Current scope:** Drupal Core, Drupal CMS and LocalGov Drupal, with data from
Drupal.org and Drupal's GitLab instance. GitHub is used for hosting and CI only.

**Future, not implemented:** GitHub Issues, Jira and arbitrary GitLab instances.
They may supply evidence for other software products, but should not dictate the
schema now. Keep source identifiers, original state, release applicability,
comments, code changes and evidence provenance separate. A new adapter should
never be able to infer a conformance result from issue status alone.

Before adding a new tracker, demonstrate real demand and add fixtures covering
ambiguous IDs, access controls, state transitions, pagination and version scope.
Private tracker material must never enter GitHub Pages automatically.
