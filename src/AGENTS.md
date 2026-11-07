# AGENTS.md: pipeline code

- Source adapter calls MUST be bounded, sequential where required, cached where
  possible, and must preserve original issue identifiers and fetch times.
- All release conclusions are about a declared target, never about an issue
  alone. Every finding must carry `assessment_id`, `target` and `observed_at`.
- Prefer `unknown` over unsupported inference.
- A git commit contained in a release tag proves inclusion of the commit only,
  not behavioural correction or applicability of the defect.
- Do not embed AI into deterministic normalization, filtering, or serialization.
- Keep externally supplied issue descriptions and comments untrusted and escape
  them in renderers. `html_to_text` strips script/style content; it does not
  make the source trustworthy.
- Do not change policy enums or the verified Drupal status map without updating
  tests, `docs/EVIDENCE-MODEL.md`, report labels and UI filters.
- Do not change `evidence_digest`/`manifest_digest` semantics without an ADR.
  A published digest must be reproducible from the published artifact.
- `confirmed-fixed` requires a contained fix commit and a closed-fixed tracker;
  keep it `unreviewed` with the behavioural-verification caveat.
- Keep raw snapshots private, mode `0600`, and never overwrite historical
  evidence.
- The static report must remain usable without JavaScript.
