# AI governance

**AI is not used in the current evidence pipeline or report.** `ai.py` is an
opt-in Cloudflare helper that is not called by `collect`, `analyze`, `report` or
`pipeline`. It is currently **experimental and not production-ready**.

AI use is optional and off by default. If enabled, model tasks may suggest
concise summaries and WCAG mappings, but never make release applicability or ACR
conformance decisions, approve findings, or create nonexistent evidence.

## Required controls before enabling a provider

The current `ai.py` does **not** yet implement all of these; they are requirements
for the Phase 3 provider work, not claims about the prototype:

- Only send public, minimal issue text by default; private data requires
  informed administrator approval and a documented processing agreement.
- Treat all issue text as adversarial input and ignore embedded instructions.
- Request structured JSON, then validate it against an explicit schema: source
  record IDs, comment IDs, commit hashes, URLs and quoted references must resolve
  to known evidence.
- Reject invented issue IDs, comments, commit hashes, people or release numbers.
- Record provider, model, parameters, prompt revision, input content hash, date
  and whether the text was human reviewed.
- Cache by input hash and prompt version; impose spending limits, timeouts and
  retry limits.
- Never send unchanged issue data to a model repeatedly.
- Keep a no-AI path that still collects, classifies and reports.
- Provide human edit/approval, a correction pathway and disclosure of AI use.

## Provider abstraction

A provider-independent interface should offer at least:

- analyze an issue into barrier summary, user impact, affected functionality,
  candidate WCAG criteria, supporting references, resolution summary,
  release-specific uncertainty and missing verification evidence;
- summarize criterion evidence;
- summarize a change between two assessments.

Confirmed facts and hypotheses must be separate fields. A suggestion is never a
finding and never a conformance value.

## Evaluation

Reuse suitable `python-acr` fixtures and build a gold-standard Drupal set.
Measure mapping accuracy, unsupported claims, hallucinated references, missed
evidence, resolution accuracy, release-applicability errors, schema validity,
cost and processing time. Record model, prompt version, timestamp and input hash
for every result.

## Providers

- **Cloudflare Workers AI** is the preferred initial hosted provider, behind a
  server-side Worker or CI job. Never expose tokens to GitHub Pages.
- **Local models** should support an OpenAI-compatible configurable endpoint
  where practical; do not require every developer to install one.
- **GitHub Copilot** requires an officially supported interface (for example
  GitHub Models). A Copilot subscription alone is not assumed to grant generic
  inference. If no supported integration exists, document the limitation and
  accept an offline import of structured responses instead.

No provider is enabled in the current milestone.
