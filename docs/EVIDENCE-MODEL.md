# Evidence model v0.1

`assessment`: `id`, `product`, `release`, `ref`, `components`, `standards`,
`installation`, and optional `applicability_overrides` indexed by issue ID.
Targets must identify an actual release before assessment claims can be made;
the example uses an illustrative release and does not claim reproducibility.

`issue`: `source`, `id`, `url`, `title`, `description`, `status`,
`updated_at`, `wcag_candidates`, `component`, `raw_version`.
An issue's `status`/`raw_version` is **tracker metadata only**.

`finding`: `issue_id`, `applicability`, `reason`, `evidence_urls`,
`basis`, `review_status`, `wcag_candidates`. Valid applicability enums:
`confirmed-affected`, `likely-affected`, `confirmed-fixed`,
`not-introduced`, `not-in-scope`, `unknown`.

Overrides are the only way to change an issue from `unknown` in this
prototype. Each override MUST have a nonempty reason and one or more URLs,
and specify a basis such as `direct-reproduction`, `git-analysis`, or
`human-review`. The code does not assert these sources are truthful.

`ai_summary` (future): provider, model, prompt version, content hash, source
references, proposed summary, uncertainty, review status. Never overwrite
reviewed facts with model output.

`conformance` (future): independent reviewer decision for each applicable
requirement, release target, scope and test protocol. Never collapse this
into issue counts. `unknown` is **not** an OpenACR `Not Evaluated` synonym.

Inputs and generated evidence carry deterministic hashes for traceability.
Release composition and effect of patches remain future work.
