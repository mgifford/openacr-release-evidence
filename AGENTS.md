# AGENTS.md: repository-wide rules

This repository supplies **release-scoped accessibility evidence**, not a
conformance certification. These instructions apply to humans and AI agents.
More specific `AGENTS.md` files under `src/`, `src/acr_evidence/adapters/`,
`web/`, and `tests/` also apply.

## Non-negotiable boundaries

1. Never infer a WCAG `Supports` decision from absent issues, closed issues,
   successful automated tests, or a model response.
2. Preserve both tracker status and **target-specific** applicability; never
   conflate a fix on `main` with a fix in an older release.
3. Upstream evidence may flow into a downstream product, but upstream
   conformance judgments must not be inherited automatically.
4. Every finding needs a stable source URL/identifier, an observation timestamp,
   and a declared target. Empty or unverifiable evidence means `unknown`.
5. Any model-derived wording is a suggestion. Keep source text untrusted, do
   not execute tracker content, and require human review of all ACR claims.
6. Do not invent reviewers, test results, affected versions, or release tags.
7. Never publish private Jira data, tokens, raw sensitive issue content, raw
   CLI output, or unpublished drafts to GitHub Pages.
8. Report missing scope and test coverage explicitly. Do not produce an
   accessibility percentage or call this pipeline a WCAG conformance test.
9. Test the site with keyboard and automated checks; automated checks alone do
   not establish conformance.
10. Name uncertainties and limitations in documentation and user-facing text.
11. Every published artifact must be verifiable from its own contents: its
    `evidence_digest` must be reproducible without private inputs. The input
    manifest digest is separate.
12. Placeholder target values (`TEMPLATE`, `SET-A-REAL`, `EXAMPLE`, `UNVERIFIED`,
    `TODO`, `CHANGEME`) are rejected unless `"synthetic": true` is explicit.
13. Commit inclusion is evidence of code inclusion only. `confirmed-fixed`
    requires a contained fix commit and a closed-fixed tracker, remains
    `unreviewed`, and must carry the behavioural-verification caveat.

## Engineering conventions

- Prefer the standard library, small modules, deterministic output and explicit
  schemas/contracts. Keep adapters isolated from assessment logic.
- Use stable IDs and preserve original upstream values in `raw` only when
  storing them privately; public exports should be minimal and reviewed.
- Do not add a dependency without a justification and licence check.
- Respect API rate limits, use timeouts/retries, never hardcode API secrets.
- Avoid untrusted HTML injection and external CDN dependencies. The static
  report must be usable without JavaScript.
- Write tests for regressions, particularly negative applicability cases.
- Do not silently make synthetic fixtures appear to describe a real release.
- When changing applicability enums or status labels, update `model.py`, tests,
  `docs/EVIDENCE-MODEL.md`, the report labels and any UI filter together.
- Do not change the digest algorithm or schema version without an ADR and a
  migration note.

## Required checks before PR

The package uses a `src/` layout. Run from the repository root:

```sh
python3 -m pip install -e '.[openacr]'   # or: export PYTHONPATH=src
python3 -m unittest discover -s tests -v
python3 -m compileall -q src
```

If `python` is absent on your platform, use `python3`. Do not document a check
that fails on a clean checkout.

External reproduction evidence (for example Drupal Core Lab) must remain separate from target verification and conformance. A record is `target_verified` only after exact target/config/result review. Guidepup and axe coverage are partial evidence, never automatic Supports.

The separate release-transition ledger may collect recently closed-fixed issues. It never changes active-issue counts or criterion results. A fix is `included` only when a commit is contained in that exact target; otherwise use `not-included`, `not-established` or `removed`. Never describe a Drupal 12 fix as a Drupal 10/11 fix without containment evidence.

ACR evidence covers active, review-relevant statuses only: 1, 8, 13, 14 and 15.
Fixed/closed/postponed statuses are excluded; RTBC stays in until closed. Page
the full queue rather than taking the first API page. Inventory records must be
marked metadata-only and must not receive a release applicability conclusion.

For multi-target changes, update `config/drupal-core-targets.json`, every
target manifest, the matrix, and the tests together. A branch target is a
development result, never a release claim. Do not mix major-version branches in
a target's commit index. `parent_project` is a link, not permission to inherit
upstream conformance.

For Pages changes, keep the publication allowlist minimal and never add raw
evidence or `collection.json`/`analysis.json` to it. The workflow must continue
to reject private paths and client-side scripts.

The ACR applies the declared surface-assessment policy: a known issue on an
assessed surface is `Partially Supports`; an assessed surface with no known issue
is `Supports`; documented feature absence is `Not Applicable`; `Does Not Support`
requires explicit broad-failure evidence and is not emitted automatically. The
policy and its project-asserted basis live in `config/surface-assessments.json`.
Issue tags alone never establish a result, and absence alone never establishes
support. The criterion-evidence ledger records reported barriers,
candidate mappings, verification gaps and unreviewed relationships separately. Mark every derived value as draft, state
that no issue was reproduced against the target, and require human confirmation.
`/admin`, Drupal `/user` login paths, the component mapping in
`config/surface-policy.json` and login/reproduction cues classify the authoring
surface; otherwise default to web. Component mappings (for example
`navigation.module`, `content_moderation.module`, `dblog.module`) take precedence
over title-only guesses. Theme mappings and per-release theme changes live in
`config/surface-policy.json` and `config/release-changes.json`. Use issue-specific
overrides for mixed components such as `taxonomy.module` or `javascript`. All `/user` paths, including
`/user/1`, are authoring/account surfaces. Never infer Supports from an empty
issue queue, never remove the draft disclaimer.

Accessibility impact data lives in `data/accessibility-impact/`. It is proposed editorial synthesis with source links, not conformance evidence. Do not promote `proposed` records to `reviewed` without human review, and do not treat a missing standards crosswalk as proof of no impact.

ATAG evidence is separate from WCAG/OpenACR. The `atag` tag marks a reported
authoring-tool issue, not an ATAG result. Do not infer Part A/B from a component
name or issue title: only an explicit ATAG Part tag or a documented human-reviewed
mapping may assign a Part. Do not populate ATAG results automatically, and do not
inherit ATAG conclusions into OpenACR (or the reverse). The WAI ATAG Report Tool
JSON must keep every criterion `Not checked` until a human reviewer edits it.

OpenACR exports must remain valid against the pinned schema and catalog. They
apply the same surface-assessment policy, mark the file draft, and require human
confirmation; do not use `not-evaluated` for A/AA. Do not replace the placeholder
reviewer until a human has reviewed the file.
Keep the vendored standards pinned and attributed.

For report or UI changes, also:

- render at 320 CSS px (400% zoom equivalent) and confirm there is no
  horizontal scrolling;
- run the axe-core check and record the result;
- test keyboard-only operation, including the skip link and `<details>`;
- confirm the report is readable with JavaScript disabled;
- record manual screen-reader testing, or explicitly state that it was not done.

Weekly snapshots must open a review PR; never auto-deploy an unreviewed
snapshot. Merging the weekly PR is the publication review event.

Document changes to semantics in `docs/EVIDENCE-MODEL.md`, changes to risk or
editorial decisions in `docs/CONFORMANCE-POLICY.md`, and consequential design
changes in `docs/decisions/`. Keep `AUDIT.md` current for known defects.

## Drupal-first data collection

Review `docs/DRUPALORG-CLI.md` and
`src/acr_evidence/adapters/AGENTS.md`. The primary sources are Drupal.org and
Drupal's GitLab. GitHub and Jira issue integration remain deferred; do not spend
initial PRs on them. Drupal issue NIDs and GitLab work-item IIDs must be scoped
to their Drupal project.

Verified CLI facts (0.15.0):

- `issue:show` needs `--with-comments` to return discussion;
- `mr:list` defaults to **opened** MRs; pass `--state=all`;
- status **7** is “Closed (fixed)”; status **8** is “Needs review”;
- the bridge is read-only and its command/flag allowlist must not be widened to
  mutating commands.

Do not copy long `drupalorg-cli` command references into this file; defer to the
installed CLI skills and `docs/DRUPALORG-CLI.md`.

## AI

AI is optional and off by default. It must never make applicability or
conformance decisions, approve findings or invent evidence. If an AI provider is
added, keep a no-AI path, validate structured responses, record provider/model/
prompt version/input hash/date, and evaluate against gold-standard Drupal issues
before enabling it. AI is never used to assign applicability or conformance; optional
criterion-summary prose is validated and falls back to deterministic text.

Human-maintained ACR/AI context lives in `context/` (`DRUPAL.md`, `DRUPAL-CMS.md`,
`LOCALGOV.md`, `CKEDITOR.md`). It is scope/wording guidance, never evidence. Pass
the matching context to the weekly model and record its hash; never merge one
product's context or conformance result into another's.

Optional ACR criterion summaries are model-assisted drafts cached by issue-content
hash. Hugging Face is the default; Cloudflare Workers AI is an opt-in comparison/
fallback provider with separate credentials and output cache. Only accepted, validated summaries may be used; rejected or failed output
falls back to deterministic issue-title text. They never replace issue references
or human review.

Weekly AI summaries are optional and off by default. The facts and diff are
deterministic; only changed/new/no-longer-active issues are sent to the model,
and the model is skipped when there is no activity. AI may write only an
executive summary. Validate every number and issue ID against the facts, reject
conformance language, record provenance, and fall back to the deterministic
digest on failure. The weekly executive summary must never modify
OpenACR or the ACR narrative. The separate, validated criterion-summary cache may
supply draft ACR paragraphs as described above; it never supplies issue
references, statistics or a final conformance result.
