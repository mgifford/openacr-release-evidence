# Release inventory design

**Status: implemented as `src/acr_evidence/inventory.py`; four exact-tag
inventories are committed under `data/component-inventory/`.**

The inventory is a deterministic record of what a Drupal Core release bundles,
what its standard profile installs, and which themes that profile sets as
default and admin. It is not an accessibility assessment.

## Why the distinctions matter

| Scope | Question answered | Do not infer |
| --- | --- | --- |
| Bundled | Does the extension ship in the release? | That it is enabled or used. |
| Installed by standard profile | Does a stock install enable it, including dependencies? | That a site uses it, or that it is the default theme. |
| Default theme | Which installed theme does the profile set? | That every site uses it. |
| Configured product | What does a declared downstream manifest enable? | That the stock profile or every site matches it. |

A removed theme is not installed, but its issues do not become fixed. A bundled
experimental module is present in the code but not enabled by the stock profile.

## Method

1. Check out the exact Git tag.
2. Read `core/modules/*/*.info.yml`, `core/themes/*/*.info.yml` and
   `core/profiles/*/*.info.yml`.
3. Exclude hidden test profiles from the shipped-profile count.
4. Resolve the standard profile's `install:` list through module dependencies.
5. Read `core/profiles/standard/config/install/system.theme.yml` for the default
   and admin themes.
6. Record the exact commit, retrieval time and source path for every component.
7. Compute a content digest over components, profile and source (excluding the
   retrieval time).

No release-note inference. No current-documentation inference. No third-party
YAML parser.

## Artifact schema

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "drupal-component-inventory",
  "disclaimer": "Declared component inventory ... not an accessibility assessment.",
  "source": {
    "product": "Drupal Core",
    "repository": "https://git.drupalcode.org/project/drupal",
    "ref": "11.4.12",
    "ref_type": "tag",
    "commit": "aa556ff13046baca57d5f69fac25c96fc30b4f43",
    "retrieved_at": "2026-11-12T15:00:00Z",
    "method": "direct .info.yml extraction from the exact ref; no release-note inference"
  },
  "scope": {
    "bundled": "Every module, theme and profile directory with a matching .info.yml.",
    "installed": "Closure of the standard profile install list plus themes and system.theme.yml.",
    "default": "system.theme.yml default/admin values, not a site configuration."
  },
  "profile": {
    "name": "standard",
    "install_list": ["node", "block"],
    "themes": ["olivero", "claro"],
    "default_theme": "olivero",
    "admin_theme": "claro"
  },
  "counts": {
    "modules_bundled": 75,
    "themes_bundled": 6,
    "modules_installed_by_standard_profile": 36,
    "themes_installed_by_standard_profile": 2,
    "modules_experimental": 2,
    "themes_experimental": 1,
    "modules_deprecated": 6,
    "themes_deprecated": 1,
    "modules_obsolete": 1
  },
  "components": [
    {
      "machine_name": "default_admin",
      "type": "theme",
      "label": "Default Admin",
      "status": "experimental",
      "status_basis": "lifecycle",
      "bundled": true,
      "installed_by_standard_profile": false,
      "default_theme": false,
      "admin_theme": false,
      "hidden": false,
      "base_theme": null,
      "package": "Core",
      "dependencies": [],
      "source_path": "core/themes/default_admin/default_admin.info.yml"
    }
  ],
  "content_digest": "…",
  "evidence_digest": "…"
}
```

## Comparison artifact

`component-compare` compares two inventories and records:

- added components;
- removed components;
- status changes (experimental → stable, deprecated, obsolete);
- installation/default changes;
- count deltas;
- source refs and inventory digests.

It deliberately does **not** record a fix, a successor project or inherited
issues. Those require a lineage record and per-issue evidence.

## Initial comparison

| | 11.4.12 | 12.0.0-beta2 |
| --- | ---: | ---: |
| Modules bundled | 75 | 67 |
| Themes bundled | 6 | 3 |
| Modules installed by standard | 36 | 36 |
| Themes installed by standard | 2 | 1 |
| Default theme | Olivero | Default Admin |
| Admin theme | Claro | Default Admin |
| Modules removed | — | ban, contact, field_layout, history, search, settings_tray, shortcut, telephone, toolbar |
| Modules added | — | mailer |
| Themes removed | — | claro, olivero, stable9 |

At 12.0.0-alpha1, the counts are 69 modules and 5 themes; Claro is still the
default and admin theme, and Olivero is bundled but not installed. The
`12.0.x` line is not a single theme configuration.

## Reproduction commands

```sh
git clone --filter=blob:none --no-checkout https://git.drupalcode.org/project/drupal.git
cd drupal
git fetch --depth 1 origin refs/tags/11.4.12:refs/tags/11.4.12
git checkout 11.4.12

acr-evidence component-inventory \
  --source . --ref 11.4.12 --commit "$(git rev-parse 11.4.12)" \
  --retrieved-at 2026-11-12T15:00:00Z \
  --output data/component-inventory/drupal-core-11.4.12.json

acr-evidence component-compare \
  --before data/component-inventory/drupal-core-11.4.12.json \
  --after data/component-inventory/drupal-core-12.0.0-beta2.json \
  --output data/component-inventory/comparison-11.4.12-12.0.0-beta2.json
```

## Limitations

- `.info.yml` parsing is shallow; PHP, recipes, config and runtime dependencies
  are not evaluated.
- The installed set is a dependency closure, not a database dump from a running
  site.
- Hidden test modules/themes are counted if they are direct top-level
  extensions; hidden test profiles are excluded.
- The inventory cannot tell whether a contrib package overrides a component.
- A configured product's manifest is separate from the stock profile.

## Related

- [`COMPONENT-HISTORY-INVESTIGATION.md`](COMPONENT-HISTORY-INVESTIGATION.md)
- [`COMPONENT-LINEAGE-MODEL.md`](COMPONENT-LINEAGE-MODEL.md)
- `src/acr_evidence/inventory.py`
- `tests/test_inventory.py`
