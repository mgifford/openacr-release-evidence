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
python3 -m pip install -e '.[yaml]'   # or: export PYTHONPATH=src
python3 -m unittest discover -s tests -v
python3 -m compileall -q src
```

If `python` is absent on your platform, use `python3`. Do not document a check
that fails on a clean checkout.

For report or UI changes, also:

- render at 320 CSS px (400% zoom equivalent) and confirm there is no
  horizontal scrolling;
- run the axe-core check and record the result;
- test keyboard-only operation, including the skip link and `<details>`;
- confirm the report is readable with JavaScript disabled;
- record manual screen-reader testing, or explicitly state that it was not done.

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
before enabling it. No AI is used in the current evidence report.
