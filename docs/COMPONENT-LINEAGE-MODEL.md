# Component lineage model

**Status: schema and validator implemented; records are curated and unreviewed.**

The release reports must not treat project ownership, component identity,
package membership, source-code lineage and release applicability as the same
thing. This model keeps them separate.

## Five separate concepts

| Concept | Question | Stored as |
| --- | --- | --- |
| Project ownership | Which Drupal.org project maintains the code? | `project` |
| Component identity | Which module/theme/component is this? | `component` + `type` |
| Package membership | Is it bundled with this Core release? | release inventory `bundled` |
| Source-code lineage | Did code move or get copied? | relationship record + tree comparison |
| Release applicability | Does a reported problem affect this release? | finding `applicability` in `evidence.json` |

A relationship record never sets applicability. A removal never means "fixed".
An adoption never means "inherit every predecessor issue".

## Record schema

`src/acr_evidence/lineage.py` validates records like this:

```json
{
  "id": "default-admin-adopted-from-gin",
  "relation": "adopted-from-contrib",
  "source": {
    "project": "gin",
    "component": "gin",
    "type": "theme",
    "release_boundary": {"adopted_branch": "6.x"}
  },
  "destination": {
    "project": "drupal",
    "component": "default_admin",
    "type": "theme",
    "release_boundary": {
      "first_bundled": "11.4.0",
      "first_stable": "12.0.0-beta1",
      "first_default_admin": "12.0.0-beta2"
    }
  },
  "evidence": [
    {
      "kind": "issue",
      "url": "https://www.drupal.org/project/drupal/issues/3556948",
      "observed_at": "2026-11-12T15:00:00Z",
      "note": "Closed (fixed) 'Merging Gin as Admin theme'."
    }
  ],
  "evidence_class": "verified-source-code",
  "verification": {"status": "unreviewed"},
  "limitations": [
    "Adoption does not automatically inherit Gin issues."
  ]
}
```

## Relationship types

- `introduced-into-core`
- `moved-to-contrib`
- `adopted-from-contrib`
- `renamed`
- `deprecated`
- `removed`
- `replaced`
- `split-into`
- `merged-into`
- `derived-from`
- `shares-inherited-code`

## Evidence classes

| Class | Meaning |
| --- | --- |
| `explicit-metadata` | An authoritative issue or release record states the relationship directly. |
| `verified-source-code` | Exact tags, commits, file paths or blob IDs show the relationship. |
| `strong-candidate` | Several signals agree, but the link is not complete. |
| `weak-inferred` | A name or text hint only. Do not use for a report conclusion. |
| `unknown` | No usable evidence. |

Confidence is not conformance confidence. Even `verified-source-code` proves code
relationship, not that a barrier survives or was fixed.

## Verification states

- `unreviewed` — machine-checked only; the default for every current record.
- `reviewed` — a named human checked the source and the limitation.
- `rejected` — the relationship is wrong; keep the record for audit.
- `stale` — the upstream release moved after the record was written.

Do not invent a reviewer. The current records are `unreviewed`.

## Scope separation

The model distinguishes:

1. **Core distribution** — bundled modules/themes in the exact tag.
2. **Default installation** — the standard profile's installed set and default
   themes.
3. **Configured product** — a downstream site or distribution with its own
   manifest, Composer lock and configuration.

A component can be bundled but not installed. A component can be installed but
not the default. A configured product can enable a component the stock profile
does not.

## Storage and validation

- Records: `data/component-lineage/olivero-claro-gin-default-admin.json`.
- Validator: `acr-evidence lineage-check --file <path>`.
- Tests: `tests/test_lineage.py`.
- Digest: `lineage_digest()` over the records, excluding retrieval metadata.

Do not add a graph database. JSON records are reviewable, diffable and work on
GitHub Pages.

## Reuse beyond Drupal

The schema is product-neutral. A relationship needs only:

- a source project/component;
- a destination project/component;
- a release boundary or commit range;
- evidence links and a verification state.

That is enough for Composer packages, npm packages, WordPress plugins/themes,
Drupal distributions or a downstream design system. The Drupal-specific parts
are the `.info.yml` inventory extractor and the Drupal.org/GitLab adapters, not
the relationship model.

## Current limits

- Only the Olivero/Claro/Gin/Default Admin theme relationships are recorded.
- Module moves and splits are not modelled yet.
- No contributed queue collection exists.
- No automatic lineage inference. Candidate relationships must be curated and
  reviewed before the report may use them.
- The report only uses lineage for scope explanations and inventory notes today;
  it does not change applicability automatically.
