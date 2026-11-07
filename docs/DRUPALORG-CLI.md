# Drupal.org CLI and GitLab integration

## Scope of the first implementation

Drupal.org and `git.drupalcode.org` are the **primary issue and change sources**.
This project is not a general Jira or GitHub tracker aggregator in this phase.
GitHub hosts this project and its CI, but **does not supply Drupal Core issue data**.
The code may later accept issue adapters for other trackers; this is not a promise
of current support.

## Why use mglaman/drupalorg-cli

[mglaman/drupalorg-cli](https://github.com/mglaman/drupalorg-cli) already combines
Drupal.org REST and Drupal GitLab REST access. Its README documents automatic
recognition of Drupal projects whose issue queues have migrated to GitLab work
items. It exposes project releases, issue details, related MR lists, MR state,
commit containment and GitLab pipelines. It also publishes agent-oriented
instructions with its installed version.

We should avoid duplicating its issue-source migration logic when practical.
It is a **CLI dependency**, not a library interface with a stability guarantee.
Pin the CLI release in CI when automated collection is introduced.

## Installation and skill discovery

The CLI needs PHP 8.1+, cURL and Git. Follow its README for installation.
Check the installed version's supported commands:

```sh
drupalorg list
drupalorg skill:get
drupalorg skill:get drupalorg-cli --full
drupalorg skill:get drupalorg-issue-search
drupalorg skill:get drupalorg-work-on-issue
```

The CLI's `skill:install` adds an agent skill discovery stub to `.claude/skills/`.
It is optional for this repository. Agents must retrieve skills from the installed
CLI instead of copying potentially outdated instruction text into AGENTS.md.

## Read-only collection

```sh
# Classic Drupal Core issue; includes its MR list if available
acr-evidence collect-drupal --issue 3619127 \
  --output private-evidence/core-3619127.json

# GitLab work item, project-scoped. A bare IID is not globally unique.
acr-evidence collect-drupal --issue 'ai_context#3586157' \
  --output private-evidence/ai-context-3586157.json

# Version listing (raw CLI output, no release claims)
acr-evidence drupal-releases --project drupal \
  --output private-evidence/core-releases.json
```

The new `collect-drupal` bridge uses `issue:show` and `mr:list` with `--format=llm`
and archives their output. **It does not yet parse the CLI's rich output into the
normalized evidence model.** Raw outputs are private review material, excluded
from Git and public previews. The previous `fetch-drupal` command remains as a
legacy direct Drupal.org API reader for explicit IDs, not as migration-aware
production ingestion.

If MR listing fails, the snapshot preserves a warning. It does not infer that
there is no MR. The bridge never calls commands that create branches, modify
issues, apply patches or change remote repositories.

## Release analysis plan

1. Capture the target Drupal Core release tag and immutable commit SHA.
2. Capture the relevant issue, full discussion and related MR metadata.
3. Collect `mr:show`, relevant diffs and merge SHA where available.
4. Use `project:contains` and local Git ancestry as **inclusion signals**.
5. Check for cherry-picked backports and equivalent patches.
6. Verify functionality against the **installed release**, not just a merged MR.
7. Record `confirmed-affected`, `confirmed-fixed`, `not-introduced`, or `unknown`
   only when there is corresponding target-specific evidence.

Do not confuse "MR merged", "pipeline passed", "issue fixed", "commit in tag"
and "barrier resolved in this installed release".

## GitLab migration and identifiers

The [Drupal.org GitLab issues guide](https://www.drupal.org/docs/develop/issues/gitlab-issues-for-drupalorg-projects)
notes that migrated NIDs become GitLab IIDs in each project. The ID is therefore
**not globally unique**. Use `drupal:<project>:<iid>` for new normalized IDs,
with the original URL and old NID stored as aliases. Do not merge records merely
because numeric identifiers match.

DrupalBot may appear as the author of a migrated issue; preserve the historical
author provenance documented in the migrated description rather than treating
DrupalBot as the original reporter.

## AI contribution policy

Follow Drupal.org's current [policy on AI-assisted contributions](https://www.drupal.org/docs/develop/issues/issue-procedures-and-etiquette/policy-on-the-use-of-ai-when-contributing-to-drupal).
The CLI skills document how contributors should read threads and disclose AI
assistance. This evidence collector does not automatically post any summaries,
update issue descriptions, or modify merge requests.
