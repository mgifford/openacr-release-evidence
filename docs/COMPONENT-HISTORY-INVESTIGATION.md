# Drupal Core component history investigation

**Status: investigation and minimal inventory prototype implemented, 2026-11-12.**

This page summarises the component-history work that the release reports now
use. It is not a complete history of every Drupal Core extension. It records
what was verified from exact Git tags, what remains curated, and what the report
generator may safely say.

## Why this exists

A component can leave Drupal Core without its accessibility issues being fixed.
A component can enter Core from a contributed project without inheriting all of
that project's history. The release report must therefore distinguish:

- **bundled** — shipped in the Core release;
- **installed** — enabled by the standard profile, including dependency closure;
- **default** — the front-end and admin themes the profile sets;
- **contributed** — maintained outside Core after a move;
- **adopted** — code brought into Core from a contributed project.

A removal is a scope change. It is not a fix. An adoption is a code
relationship. It is not permission to inherit issues.

## Reproducible extraction

The prototype lives in `src/acr_evidence/inventory.py`. It reads
`core/modules/*/*.info.yml`, `core/themes/*/*.info.yml`,
`core/profiles/*/*.info.yml` and the standard profile's
`config/install/system.theme.yml` from an exact checkout. It does not use
release notes to infer counts.

```sh
git clone --filter=blob:none --no-checkout https://git.drupalcode.org/project/drupal.git drupal
cd drupal
git fetch --depth 1 origin refs/tags/11.4.12:refs/tags/11.4.12
git checkout 11.4.12

acr-evidence component-inventory \
  --source . --ref 11.4.12 \
  --commit "$(git rev-parse 11.4.12)" \
  --retrieved-at 2026-11-12T15:00:00Z \
  --output ../data/component-inventory/drupal-core-11.4.12.json
```

The committed inventories are in `data/component-inventory/`. Lineage records
are in `data/component-lineage/olivero-claro-gin-default-admin.json` and are
validated with:

```sh
acr-evidence lineage-check --file data/component-lineage/olivero-claro-gin-default-admin.json
```

`tests/test_inventory.py`, `tests/test_lineage.py` and
`tests/test_provenance.py` run offline.

## Verified counts

All counts are from the exact tags listed below, using the extraction script.
`modules` and `themes` are bundled extensions, not installed ones.

| Release | Modules | Themes | Profiles | Modules installed by standard | Themes installed by standard | Experimental modules/themes | Deprecated modules/themes | Default theme | Admin theme |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 10.6.21 | 79 | 5 | 3 | 39 | 2 | 2 / 0 | 8 / 0 | Olivero | Claro |
| 11.4.12 | 75 | 6 | 3 | 36 | 2 | 2 / 1 | 6 / 1 | Olivero | Claro |
| 12.0.0-alpha1 | 69 | 5 | 2 | 36 | 1 | 3 / 1 | 0 / 0 | Claro | Claro |
| 12.0.0-beta2 | 67 | 3 | 2 | 36 | 1 | 3 / 0 | 0 / 0 | Default Admin | Default Admin |

`profiles` excludes hidden test profiles. The 10.6.21 source tree contains
several hidden test profiles; they are not shipped profile choices.

### What changed between 11.4.12 and 12.0.0-beta2

Removed modules (9): `ban`, `contact`, `field_layout`, `history`, `search`,
`settings_tray`, `shortcut`, `telephone`, `toolbar`.

Added modules (1): `mailer`.

Net module change: −8.

Removed themes (3): `claro`, `olivero`, `stable9`.

The standard profile still installs the same 36 modules, but its theme scope
changes from Olivero + Claro to Default Admin. At 12.0.0-alpha1, Claro is still
present and is both the default and admin theme; Olivero is bundled but not
installed. At 12.0.0-beta2, Claro and Olivero are gone. Treating "12.0.x" as one
theme configuration is therefore wrong.

### Theme lifecycle from exact tags

| Theme | First bundled | Experimental until | Stable | First default | Removed |
| --- | --- | --- | --- | --- | --- |
| Claro | 8.8.0 | 9.3.0 (`experimental: true`) | 9.4.0 | 9.4.0 (admin) | 12.0.0-beta1 |
| Olivero | 9.1.0 | 9.2.0 (`experimental: true`) | 9.3.0 | 9.4.0 (front end) | 12.0.0-beta1 |
| Default Admin | 11.4.0 | 12.0.0-alpha1 (`lifecycle: experimental`) | 12.0.0-beta1 | 12.0.0-beta2 (default and admin) | — |

The removals were commits `8eaf82d7` (Claro, 2026-09-21) and `8d87e802`
(Olivero, 2026-09-19), both contained in 12.0.0-beta1 and 12.0.0-beta2. The
first tag in this comparison without them is 12.0.0-beta1, not beta2.

## Code continuity evidence

Blob IDs from Git trees were compared at matching relative paths. This is
deterministic evidence of shared code, not proof that a defect reproduces.

| Comparison | Common paths | Byte-identical blobs | Changed | Left-only | Right-only |
| --- | ---: | ---: | ---: | ---: | ---: |
| Core 11.4.12 Olivero vs contributed Olivero 2.0.0 | 300 | 265 | 35 | 3 | 68 |
| Core 11.4.12 Claro vs contributed Claro 3.0.0 | 468 | 419 | 49 | 23 | 9 |
| Core 12.0.0-beta2 Default Admin vs Gin 6.x | 460 | 230 | 230 | 167 | 182 |
| Core 12.0.0-beta2 Default Admin vs Gin 5.0.16 | 41 | 6 | 35 | 586 | 387 |
| Core 12.0.0-beta2 Default Admin vs Core 11.4.12 Claro | 303 | 136 | 167 | — | — |

The Gin 5.0.16 result is important: Gin 5.x is not a safe code proxy for
Default Admin. A Gin 5.x issue may or may not survive the refactor. Gin 6.x has
much more in common, but 230 changed paths still require per-issue review.

## What happened to Olivero and Claro issues

On 2026-11-12, the Drupal.org issue queues for the theme components showed:

| Component | Total issues in queue | Active (1/8/13/14/15) |
| --- | ---: | ---: |
| Claro theme | 527 | 1 |
| Olivero theme | 536 | 0 |
| Admin theme | 187 | 76 |

The Claro and Olivero theme queues are effectively closed, but closure is not
the same as a fix. The active accessibility-tagged issue collection uses the
generic `Admin theme` component, not the theme-specific components: 25 of the
432 collected issues are `Admin theme`, while none are `Claro theme` or
`Olivero theme`. The report therefore cannot infer a theme from the component
field alone.

The report now states that a removed theme is absent from the release and its
issues need separate contributed-project tracking. It does not mark them fixed.

## Olivero and Claro samples

These are investigation samples, not conformance results.

### Olivero pager ellipsis (`drupal:3348552`)

- Reported 2023-03-16; status Needs review; component `theme system`; MR 5245
  is open.
- The Olivero pager template at Core 11.4.12 and contributed Olivero 2.0.0
  differs only in Twig `include` syntax; both still render the ellipsis as
  `<li role="presentation">&hellip;</li>`.
- Applicability: probably affects 10.6.21, 11.4.12 and 12.0.0-alpha1; not part
  of Core at 12.0.0-beta2; likely relevant to contributed Olivero 2.0.0, but not
  reproduced there.
- Confidence: strong candidate for the Core copies; medium for the contributed
  copy because only the template was compared.

### Claro status message landmark (`drupal:3159933`)

- Reported 2020-07-17; status Needs work; component `markup`; no collected MR.
- Core 11.4.12 Claro uses `role="contentinfo"` for status messages.
- Contributed Claro 3.0.0 uses `role="alert"` for errors/warnings and
  `role="status"` otherwise. That looks like a correction, but there is no
  linked Core issue or merge request and no behavioural test.
- Applicability: probably affects 10.6.21, 11.4.12 and 12.0.0-alpha1 Core;
  absent from Core at 12.0.0-beta2; possibly corrected in contributed Claro
  3.0.0, unverified.
- Confidence: source-code association is verified; the fix status is a strong
  candidate only. Do not mark the Core issue fixed.

## Default Admin, Gin and Claro lineage

- Gin 6.x was prepared for Core. Core issue
  [#3556948](https://www.drupal.org/project/drupal/issues/3556948) is the merge
  issue; [#3576646](https://www.drupal.org/project/drupal/issues/3576646)
  renamed `admin` to `default_admin`.
- The Core issue summary for
  [#3582833](https://www.drupal.org/project/drupal/issues/3582833) says:
  "The Default Admin theme is basically Gin renamed. Gin used Claro as a base
  theme, and that structure was flattened when it was added to core. To do
  this, Claro's CSS was copied en masse to the new theme."
- [#3599680](https://www.drupal.org/project/drupal/issues/3599680) describes
  the overlapping token systems from the "Seven → Claro → Gin" lineage.
- The accessibility meta issue
  [#3585823](https://www.drupal.org/project/drupal/issues/3585823) says Gin
  accessibility issues that apply to Default Admin should be **copied to new
  Core issues**, not inherited. Two examples are
  [#3636027](https://www.drupal.org/project/drupal/issues/3636027) (colour
  contrast, copied from Gin `3506311`) and
  [#3636643](https://www.drupal.org/project/drupal/issues/3636643) (target size,
  copied from Gin `3506334`).
- Therefore: Gin 6.x is a strong candidate source; Gin 5.x is not. Every Gin or
  Claro issue needs an association and an applicability check against the exact
  Default Admin code before it appears in a Core release finding.

## Component lineage model

The curated records use a small JSON schema in
`src/acr_evidence/lineage.py`:

- `source` and `destination`: project, component, type, release boundaries;
- `relation`: introduced-into-core, moved-to-contrib, adopted-from-contrib,
  renamed, deprecated, removed, replaced, split-into, merged-into,
  derived-from, shares-inherited-code;
- `evidence`: kind, HTTPS URL, observation time, note;
- `evidence_class`: explicit-metadata, verified-source-code, strong-candidate,
  weak-inferred, unknown;
- `verification`: unreviewed, reviewed, rejected, stale;
- `limitations`.

Every current record is `unreviewed`. The repository does not invent a human
reviewer.

## Limitations

- The inventory parser reads shallow `.info.yml` keys. It does not evaluate
  PHP, recipes, configuration or contributed dependencies at runtime.
- The standard profile's installed set is a dependency closure over
  `.info.yml` dependencies. It is not a `core.extension.yml` dump from an
  installed site.
- The report target can declare a different configuration from the stock
  profile. The 11.4.12 manifest enables Default Admin as the admin theme even
  though the stock standard profile uses Claro; the report's scope note says so.
- The tree comparison is path-and-blob based. It proves shared files, not shared
  defects.
- The Drupal.org queue counts are a 2026-11-12 snapshot and include all statuses
  for the component, not only Accessibility-tagged issues.
- The lineage records cover the themes in this investigation only. Modules and
  other distributions are not yet modelled.

## Related files

- `src/acr_evidence/inventory.py`
- `src/acr_evidence/lineage.py`
- `src/acr_evidence/provenance.py`
- `data/component-inventory/`
- `data/component-lineage/olivero-claro-gin-default-admin.json`
- `tests/test_inventory.py`
- `tests/test_lineage.py`
- `tests/test_provenance.py`
- [`REPORT-TERMINOLOGY.md`](REPORT-TERMINOLOGY.md)
- [`CONFORMANCE-POLICY.md`](CONFORMANCE-POLICY.md)
