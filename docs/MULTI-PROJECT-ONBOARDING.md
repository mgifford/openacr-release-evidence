# Onboarding Drupal CMS and LocalGov Drupal

This is the process for taking the Drupal Core evidence pipeline to a
distribution. It is deliberately not “point `--project` at another queue and
publish.”

## 1. Define the product and release scope

For each distribution, choose **one exact release** for the pilot and declare:

- product name and repository;
- distribution version/tag;
- Composer project template and lockfile;
- Drupal Core version;
- install profile;
- recipes, modules and themes included as shipped;
- configuration/sample content used for the assessment;
- supported/development status and target commit;
- parent project (`drupal` for both CMS and LocalGov).

**Drupal CMS**

- Install paths: launcher, DDEV, or the documented project template.
- Start from a clean install and capture the generated `composer.lock`; the lock
  is the distribution inventory, not a hand-written module list.
- Record the Drupal CMS version/tag and the Core version it resolves to.
- Include the recipes and default theme/admin theme actually installed.

**LocalGov Drupal**

- Drupal 11 is documented on the 4.x line using
  `composer create-project drupal/localgov_project:^4.0`.
- Drupal 10 is documented on the 3.x line. Recheck the current supported-branch
  policy at release time.
- Capture the lockfile and install profile (`localgov`), plus enabled
  `localgov_*` modules, themes and recipes.

Do not claim the distribution covers every site built from it, or every optional
recipe. State the exact profile and lockfile.

## 2. Inventory issue sources

The distribution project queue is only one source.

- Drupal CMS project: `https://www.drupal.org/project/issues/drupal_cms`
  (project ID `3466967`).
- LocalGov project: `https://www.drupal.org/project/issues/localgov`
  (project ID `3154243`).
- Parent Core queue: `https://www.drupal.org/project/issues/drupal`.
- Every included contributed project's queue.
- Theme queues, including front-end/admin themes.
- Recipes and install-profile queues where they exist.

The current collector can query a single Drupal project ID. It needs a
**distribution collector** that:

1. reads the Composer lock;
2. maps Drupal packages to Drupal.org project IDs/machine names;
3. collects each included project's active Accessibility-tagged issues;
4. deduplicates by issue ID;
5. records the source project and package version;
6. includes parent Core issues only when the affected component is in the
   distribution;
7. does not inherit Core or contrib conformance.

### Coverage warning

A quick check on 2026-11-09 found:

- Drupal CMS project queue: active Accessibility-tagged issues exist.
- LocalGov distribution project queue: no active Accessibility-tagged issues in
  the first query.

That does **not** mean LocalGov is accessible. It means the distribution queue
alone is not a sufficient source. LocalGov issues are likely in its component
module/theme queues, or the issue lacks the Accessibility tag. The collector
must include those queues and report tag coverage as a limitation.

## 3. Build target manifests

Create one target per exact release, for example:

```text
config/drupal-cms-1.x.json
config/drupal-cms-targets.json
config/localgov-4.x.json
config/localgov-targets.json
```

Each manifest should include:

- `id`, product, release/ref, release line, support status;
- `parent_project: "drupal"`;
- Core version and target commit;
- Composer lock digest;
- install profile and recipes;
- enabled components/themes;
- issue projects and source URLs;
- scope note (stock install vs recommended recipe set).

Do not copy the Core manifest and change only the product name.

## 4. Surface policy

Reuse `config/surface-policy.json` with distribution additions:

- admin themes and authoring modules → Authoring Tool;
- front-end themes/components → Web;
- explicit issue overrides for mixed modules;
- `config/release-changes.json` per release line for added/removed themes.

Drupal CMS and LocalGov have their own themes, admin UI and recipe-specific
components. A Core component mapping is not automatically correct for a
distribution.

## 5. ACR treatment

The ACR for a distribution:

- covers the distribution **as shipped**, with the declared lockfile;
- has Web and Authoring Tool components;
- marks Electronic Documents/Software N/A unless the distribution ships a
  distinct document/software product;
- links to the parent Core ACR but does **not** inherit its results;
- links component/upstream ACRs rather than copying conclusions;
- keeps every criterion draft and human-reviewed;
- states that theme project queues and optional recipes may be out of scope.

A distribution ACR should not simply reproduce the Core ACR with a different
title. It needs its own issue inventory and release scope.

## 6. Reports and publication

Add:

- product sections to the landing page;
- per-release report directories;
- a `matrix` or comparison view for the distribution's releases;
- an ACR draft per target;
- a parent/child link to Core and component ACRs;
- separate Pages paths and allowlist entries.

Do not merge distribution evidence into the Core collection. Keep canonical
issues shared, but preserve release-specific applicability and provenance.

## 7. Pilot sequence

1. Pick **one** Drupal CMS release and one LocalGov 4.x release.
2. Build clean installs and capture lockfiles.
3. Generate the package/project inventory and a coverage report.
4. Collect project + component queues with Accessibility tags.
5. Run the existing report/ACR generation with product-specific manifests.
6. Manually inspect 20–30 issues for surface and applicability.
7. Add issue overrides and component mappings.
8. Add regression tests for the new mappings and counts.
9. Publish as a draft/review PR.
10. Only then automate the weekly run.

## 8. Success criteria

- Exact product/version/lockfile is reproducible.
- Every included issue source is named.
- Every issue has a public URL and source project.
- Web and Authoring Tool are separated.
- Parent Core and component results are not inherited.
- Missing Accessibility tags and omitted queues are explicit limitations.
- A human review PR is the publication gate.
