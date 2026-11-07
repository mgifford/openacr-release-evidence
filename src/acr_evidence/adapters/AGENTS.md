# Adapter agent instructions

- Drupal.org and git.drupalcode.org are the only first-phase issue systems.
- Prefer documented drupalorg-cli read commands, preserving raw output and
  errors. The bridge is allowlisted; do not widen it to mutating commands.
- Verified against drupalorg-cli 0.15.0 (2026-11-07):
  - `issue:show --format=json --with-comments` is required for discussion;
  - `mr:list --state=all` is required; the default returns opened MRs only;
  - `project:contains` and the GitLab refs API agree on tag/branch containment;
  - status 7 is “Closed (fixed)” and status 8 is “Needs review”.
- Run `drupalorg skill:get drupalorg-cli --full` when the CLI is installed
  before depending on new command semantics; do not assume a static copy is
  current.
- Never call `issue:apply`, `issue:checkout`, `issue:branch`,
  `issue:setup-remote`, `issue:comment` or other mutating commands as part of
  evidence collection.
- Project-scoped GitLab IID is not a globally unique Drupal issue ID.
- Do not publish raw CLI output or encode tracker status as release
  applicability.
- Never claim merged MRs or successful CI establish release-level accessibility.
- Preserve warnings: a failed MR listing is not evidence that no MR exists.
- Add offline fixture tests for new response formats and failure conditions.
