# AGENTS.md: pipeline code

- Source adapter calls MUST be bounded, sequential where required, cached where
  possible, and must preserve original issue identifiers and fetch times.
- All release conclusions are about a target, never about an issue alone.
- Prefer `unknown` over unsupported inference.
- A git commit contained in a release tag proves inclusion of the commit only,
  not behavioural correction or applicability of the defect.
- Do not embed AI into deterministic normalization, filtering, or serialization.
- Keep externally supplied issue descriptions untrusted and escape in renderers.
- Do not change policy enums without updating tests, documentation and UI.
