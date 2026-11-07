# AGENTS.md: tests

- Fixtures are synthetic unless explicitly sourced and attributed. Real Drupal
  fixtures must record their source URL and retrieval time.
- Keep the default suite network-free. Live CLI/API checks are separate opt-in
  checks, not unit tests.
- Include negative cases: closed issue not verified, fix only on a newer branch,
  report after the release date, missing source, conflicting evidence, unknown
  release, invalid manifest, placeholder target, injection strings and invalid
  JSON from the CLI.
- Test the documented applicability matrix, including:
  - fix contained in the tag + closed-fixed → `confirmed-fixed` with caveat;
  - fix only on a newer branch → `likely-affected`;
  - open report before release → `likely-affected`;
  - open report after release → `unknown`;
  - feature absent → `not-introduced`;
  - component outside the manifest → `not-in-scope`.
- Test the published `evidence_digest` by recomputing it from the exported
  artifact, not from private inputs.
- Do not write tests that assert a WCAG conformance label from issue counts.
- Test output paths and relative links under GitHub Pages subpaths, 320 px
  reflow, `<script>`-free report output, heading order, table captions and
  internal anchors.
- Test that untrusted text is escaped and that invalid URLs are not linked.
- Do not overwrite raw historical snapshots in tests; use temporary directories.
