# Adapter agent instructions

- Drupal.org and git.drupalcode.org are the only first-phase issue systems.
- Prefer documented drupalorg-cli read commands, preserving raw output and errors.
- Run `drupalorg skill:get drupalorg-cli --full` when the CLI is installed before
  depending on command semantics; do not assume a static skill copy is current.
- Never call `issue:apply`, `issue:checkout`, `issue:branch`, `issue:setup-remote`,
  or other mutating commands as part of evidence collection.
- Project-scoped GitLab IID is not a globally unique Drupal issue ID.
- Do not publish raw CLI output or encode tracker status as release applicability.
- Never claim merged MRs or successful CI establish release-level accessibility.
- Add fixture tests for new response formats and failure conditions.
