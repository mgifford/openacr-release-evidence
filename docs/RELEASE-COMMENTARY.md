# Between-release accessibility commentary

The active ACR answers “what is still reported in this target?” The
between-release ledger answers a different question:

> Is a closed fix present in a newer release line but absent from this target?

These are separate evidence records. A closed issue never changes an active
criterion result and never increases or decreases the active issue count.

## Build the ledger

```sh
acr-evidence release-ledger \
  --project drupal \
  --targets config/drupal-core-targets.json \
  --release-changes config/release-changes.json \
  --output reports/release-ledger.json \
  --cache-dir .cache/acr-evidence
```

It collects recently changed **closed-fixed** Accessibility issues and checks
commit containment in every declared target. The weekly workflow runs it before
the ACR generation, but the step is marked optional so a tracker outage cannot
block the active-issue report.

## States

| State | Meaning |
|---|---|
| `included` | A fix commit is contained in that target |
| `not-included` | A fix commit exists but is absent from that target |
| `not-established` | No contained commit was found; do not call it a backport |
| `removed` | The component/theme is not in that release; a scope change, not a fix |

`not-established` is not “fixed elsewhere.” It is an explicit evidence gap.

## ACR output

Each target ACR gets a separate section:

**Between-release fix notes (not active-issue results)**

It lists closed-fixed issues where a newer target contains the fix and the
selected target does not, or where a theme/component was removed. The section
does not modify the criterion tables or the active issue counts.

Example wording:

> Fixed in `12.0.x`; not included in `11.4.12` at this snapshot. A future
> backport may occur, but it is not established here.

## Drupal 10, 11 and 12

- A fix in Drupal 12 is not assumed to be in Drupal 11 or 10.
- A commit may be on `main`, `12.x`, `11.x` or a release tag; each target is
  checked separately.
- If a fix is in 12 only, the 10 and 11 ACRs can say it is available in 12 and
  not in this target. They must not say it will be backported.
- If a future backport appears, the next ledger snapshot changes the state.

## Olivero and removed components

Drupal 12 no longer ships Olivero or Claro. Their issues are:

- in scope for the release lines that still ship the theme;
- `removed` for the release line that does not;
- never “fixed” merely because the theme is absent.

Theme project queues are not part of the Core collection. A theme’s own ACR is
still required.

## Release notes

Release notes are used for release identity, candidate issue links and
theme/module changes. They are not parsed as proof of a fix. A release-note link
is only a candidate until the issue status, Accessibility tag, commit and target
containment agree.

Source: <https://www.drupal.org/project/drupal/releases>

## Limitations

- Only recently closed-fixed issues in the collection window are covered.
- A closed issue with no commit in the index is `not-established`.
- Commit inclusion is not behavioural verification or independent reproduction.
- The ledger is not published as a conformance result.
- A removed component is a scope change, not a remediation.
