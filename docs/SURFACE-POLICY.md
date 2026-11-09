# Surface policy: Web vs Authoring Tool

The ACR reports Web and Authoring Tool separately because they are different
surfaces with different users. Surface classification must not depend only on
whether an issue title contains `/admin` or “login.”

## Policy files

### `config/surface-policy.json`

- `issue_overrides` — explicit issue-ID to `web` or `authoring`. Highest
  priority. Use this when the issue explicitly states its surface or when a
  component is genuinely mixed.
- `themes` — theme-component mapping:
  - `olivero`: web
  - `claro`: authoring
  - `default_admin`: authoring
  - `admin theme`: authoring
- `authoring_components` — modules/components that are part of administration
  or authoring:
  `navigation.module`, `toolbar`, CKEditor, media library, Layout Builder,
  Views UI, Field UI, `content_moderation.module`, `workflows`,
  `dblog.module`, admin themes.
- `authoring_terms` — explicit phrases such as “admin toolbar”,
  “administration interface”, “media library”, “provide authors with tools”,
  FieldWidget.
- `issue_overrides` also covers the three 1.2.2 caption/transcript issues:
  they are authoring-tool support, not public web playback.

Priority order:

1. explicit issue override;
2. theme mapping;
3. authoring component mapping;
4. `/admin` path;
5. `/user` account path;
6. explicit authoring term;
7. login/reproduction step;
8. web default.

### `config/release-changes.json`

Curated per-release-line theme/component availability. This is the place to
record changes such as:

- Drupal 10/11: Olivero is a front-end theme.
- Drupal 11: Default Admin is available in the 11.4 target.
- Drupal 12: Olivero and other front-end themes are removed; Olivero-only issues
  are out of scope for 12.x targets.

Source links point to the Drupal release notes and project queues. Update this
file when a release adds or removes a theme, module or subsystem that changes
surface interpretation. It is intentionally reviewed human data, not scraped
HTML.

## Mixed components

A component name alone does not always decide the surface:

- `taxonomy.module` can be public term pages or the admin Taxonomy overview.
- `views.module` can render a public view or an administrative listing.
- `javascript` can be a public interaction or tabledrag in the admin UI.

For those, add an issue override with the reason in the PR, or improve the
component/term policy. Do not silently treat the whole module as one surface.

## Workflow for release changes

1. Check the Drupal release notes and the affected project queue.
2. Update `config/release-changes.json` with the added/removed theme or module.
3. Update `config/surface-policy.json` if the component surface changes.
4. Add or update an issue override for ambiguous reports.
5. Regenerate the collection/analysis and inspect the ACR Web/Authoring split.
6. Add a regression test for the new mapping.

## Limitations

- The current collection is the Drupal Core Accessibility queue. A theme’s
  project queue (for example Olivero) is not yet collected; a future adapter
  must scope those issues to the distribution or theme ACR.
- An issue can affect both surfaces. The current field is a primary-surface
  classification; the remarks should state the boundary.
- Release notes are prose. The registry is curated and cited rather than parsed
  automatically so a release-note rewrite cannot silently change an ACR.
