# Deferred source integrations

**Current scope:** Drupal Core, Drupal CMS and LocalGov Drupal, with data from
Drupal.org and Drupal's GitLab instance. GitHub is used for hosting and CI only.

**Future, not implemented:** GitHub Issues, Jira and arbitrary GitLab instances.
They may supply evidence for other software products, but should not dictate the
schema now.

## Future adapter contract

A new adapter must emit the normalized issue shape used by
`normalize_drupal_issue` (or an equivalent versioned schema):

- source system and source project;
- source-scoped stable ID and original URL;
- title, description HTML and script-free text;
- labels/tags, normalized workflow state and the original raw status;
- created/updated timestamps in UTC;
- comments with IDs, authors, timestamps and content hashes;
- related change objects (MRs, PRs, commits) with stable URLs and states;
- candidate WCAG criteria only from explicit source tags, not model inference;
- provenance: retrieval time, adapter, adapter version, content hash and a
  private raw reference.

Source assumptions that must be explicit in each adapter:

- Identifiers may be project-scoped; never merge records on numeric equality.
- Access controls differ; private data must stay out of public artifacts.
- State transitions and deleted/edited content must not be reconstructed by
  guesswork.
- Pagination and rate limits must be bounded and cached.
- An adapter must never infer a conformance result from issue status or counts.

Before adding a new tracker, demonstrate real demand and add fixtures covering
ambiguous IDs, access controls, state transitions, pagination and version scope.
Private tracker material must never enter GitHub Pages automatically.
