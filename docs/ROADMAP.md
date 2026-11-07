# Roadmap / TODO

## Milestone 0: this starter

- [x] Separate product target from issue and tracker status
- [x] Drupal and GitHub issue-ID adapters
- [x] Strict `unknown` applicability default
- [x] Evidence URLs and basic deterministic hash
- [x] Browser review of draft evidence, static site, CI tests
- [x] Governance, security, AI, conformance and agent documentation
- [ ] Confirm permanent name, steward group, licence and private reporting route

## Milestone 1: defensible release applicability

- [ ] Build snapshot of **exact** Drupal Core release and main with tagged git refs
- [ ] Connect real issue + MR + comments + patch/backport histories
- [ ] Compare feature existence on main vs a pinned stable release
- [ ] Detect cherry-picks/backports with equivalent patch matching
- [ ] Require an explicit human verification pathway for `confirmed-*` status
- [ ] Add ambiguous/missing-data counterexamples and evaluation metrics
- [ ] Parse Composer lockfiles and enabled modules/themes/configurations
- [ ] Implement dependency graph and candidate evidence inheritance
- [ ] Run browser tests on real release fixtures with documented limitations

## Milestone 2: authoring and trustworthy export

- [ ] Pin GSA OpenACR schema/catalog and build complete schema-native draft
- [ ] Validate with GSA tools, round-trip import/edit/export in ACR Editor
- [ ] Add documented WCAG catalogs and applicable non-WCAG requirements
- [ ] Add editable decisions, reviewer identity and independently approved signoff
- [ ] Create publicly inspectable change history and disclosure metadata
- [ ] Export evidence supplement plus accessible HTML

## Milestone 3: interoperability and automation

- [ ] Production Drupal.org query/cursors/cache and GitLab MR support
- [ ] GitHub repository search/PR integration, Jira Cloud adapter with secure auth
- [ ] Scheduled incremental ingestion with checkpointing and rate-limit controls
- [ ] Opt-in Cloudflare AI summarization with robust model evaluation
- [ ] Publish release-targeted evidence only after human approval
- [ ] Accessibility evaluation of interface with disabled users
- [ ] Drupal CMS and LocalGov Drupal reference deployments and tests

## Revised Drupal-first priorities (November 2026)

1. Read Drupal.org classic issues and migrated GitLab work items through
   `drupalorg-cli`, with full comments and associated MRs. The current collector
   archives raw CLI output only; normalization is next.
2. Capture Drupal Core release tags, merged MR commit references, backports and
   target-specific regression evidence. Avoid deriving a release ACR from main.
3. Determine the installed Drupal Core version in Drupal CMS and LocalGov Drupal
   reference installations; capture Composer locks and enabled features.
4. Show scope-aware issue applicability and remaining evidence gaps in the UI.
5. Add human review and GSA-schema-valid OpenACR export.
6. Evaluate Cloudflare AI summaries after provenance and release logic work.

Future GitHub Issues and Jira sources are explicitly deferred; see
`docs/FUTURE-SOURCES.md`.
