# Drupal.org CLI and GitLab integration

## Scope

Drupal.org and `git.drupalcode.org` are the primary evidence sources. GitHub
hosts this project and its CI but does not supply Drupal Core issue data. Jira
and GitHub Issues remain deferred.

## Why use mglaman/drupalorg-cli

[mglaman/drupalorg-cli](https://github.com/mglaman/drupalorg-cli) combines
Drupal.org REST and Drupal GitLab access and handles projects whose issue queues
have migrated to GitLab work items. It is a **CLI dependency**, not a library
contract. Pin the version when automating; this repository validated **0.15.0**
on 2026-11-07.

The CLI needs PHP 8.1+, cURL and Git. A local validation install can use a
temporary Composer home so nothing is added to the repository:

```sh
export COMPOSER_HOME="$(mktemp -d)"
composer global require mglaman/drupalorg-cli --no-interaction
export ACR_DRUPALORG_BIN="$COMPOSER_HOME/vendor/bin/drupalorg"
"$ACR_DRUPALORG_BIN" --version
```

## Skills and command discovery

```sh
drupalorg list
drupalorg skill:get
drupalorg skill:get drupalorg-cli --full
```

Retrieve skills from the installed CLI rather than copying stale command text
into `AGENTS.md`.

## Verified read-only commands (0.15.0)

| Command | Notes |
| --- | --- |
| `issue:show <nid> --format=json --with-comments` | JSON issue, body, timestamps and comments. `--with-comments` is required; it is not the default. |
| `issue:search <project> <text> --format=json` | Title-keyword search. It does not filter by accessibility tag. |
| `mr:list <nid> --state=all --format=json` | **The default is `--state=opened`.** Use `--state=all` for merged and closed MRs. |
| `mr:show <nid> <iid> --format=json` | MR state, head SHA, pipeline and linked work items. |
| `mr:diff`, `mr:files`, `mr:logs` | Review aids; not used for release classification. |
| `project:releases <project> --format=json` | Release listing; not a git tag listing. |
| `project:contains <project> <sha> --format=json` | Branches/tags containing a commit; agrees with the GitLab refs API. |
| `project:issues <project> --format=json` | Project issue listing; no accessibility-tag filter. |

Output formats are `text`, `json`, `md` and `llm`. This pipeline uses `json` for
machine processing and keeps the raw output private.

## Collection design

- **Discovery** uses one filtered Drupal.org REST request for a project and
  taxonomy term (Accessibility = term 1101), sorted by last change.
- **Per-issue detail** uses `issue:show --format=json --with-comments` because it
  already handles classic issues and GitLab work items, and returns comments.
- **MR metadata** uses `mr:list --state=all --format=json`.
- **Release containment** uses the public GitLab API
  (`/repository/commits/<sha>/refs`) and a cached commit index, not one CLI call
  per commit.
- A failed MR listing is preserved as a warning. It is not evidence that no MR
  exists.

## Read-only allowlist

The bridge permits only:

`issue:show`, `issue:search`, `mr:list`, `mr:show`, `mr:diff`, `mr:files`,
`mr:logs`, `project:releases`, `project:release-notes`, `project:contains`,
`project:issues`.

It rejects unknown commands, arguments beginning with `-`, and flags outside a
short allowlist (`--with-comments`, `--state=…`, `--limit=…`, and similar). It
never calls `issue:apply`, `issue:checkout`, `issue:branch`,
`issue:setup-remote`, `issue:comment` or any other mutating command.

## Drupal status mapping

The current queue uses codes that differ from older documentation:

| Code | Label |
| --- | --- |
| 1 | Active |
| 2 | Fixed |
| 3 | Closed (duplicate) |
| 4 | Postponed |
| 5 | Closed (won't fix) |
| 6 | Closed (works as designed) |
| 7 | Closed (fixed) |
| 8 | Needs review |
| 13 | Needs work |
| 14 | Reviewed & tested by the community |
| 15 | Patch (to be ported) |
| 16 | Postponed (maintainer needs more info) |
| 17 | Closed (outdated) |
| 18 | Closed (cannot reproduce) |

In particular, **8 is not “closed fixed”**. The tracker label is metadata only;
it is never treated as release applicability.

## Identifiers and migration

A migrated issue's GitLab IID is scoped to its project. Do not merge records
because numeric identifiers match. The normalized record keeps the source
project, NID and URL; a future work-item adapter must use
`drupal:<project>:<iid>`.

DrupalBot may appear as the author of a migrated issue; the historical author is
in the migrated description. Do not treat DrupalBot as the original reporter.

## AI and contribution policy

Follow Drupal.org's current
[policy on AI-assisted contributions](https://www.drupal.org/docs/develop/issues/issue-procedures-and-etiquette/policy-on-the-use-of-ai-when-contributing-to-drupal).
This collector does not post summaries, edit issues or modify merge requests.
No AI is used in the current report.

## Limitations

- The CLI output schema is not a stability guarantee; pin the version and keep
  fixtures for the shapes you depend on.
- Unauthenticated GitLab/Drupal.org rate limits apply. Collection is sequential
  and cached.
- Commit matching relies on issue numbers in commit messages. Fixes without an
  issue number, configuration-only fixes and contributed-module fixes need
  separate evidence.
- A successful pipeline is not evidence of a behavioural fix.
