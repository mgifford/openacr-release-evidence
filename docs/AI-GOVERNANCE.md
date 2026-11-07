# AI governance

AI use is **optional and off by default**. Model tasks may suggest concise
summaries and WCAG mappings, but never make release applicability or ACR
conformance decisions, approve findings, or create nonexistent evidence.

- Only send public, minimal issue text by default; private data requires
  informed administrator approval and a documented processing agreement.
- Treat all issue text as adversarial input and ignore embedded instructions.
- Request structured data; validate JSON, source IDs and evidence links.
- Record provider, model, parameters, prompt revision, content hash, date and
  whether text was human reviewed.
- Uncertainty and abstention are acceptable outcomes.
- Evaluate across real and adversarial annotated examples, including main-vs-
  release conflicts, invented fixes, wrong links and missing comments.
- Cache by input hash and prompt version; impose spending limits and timeouts.
- Prefer efficient model inference and minimize environmental cost.
- Provide human edit/approval, a correction pathway and disclosure of AI use.

Cloudflare models and policies can change: pin/verify the model and API contract
before enabling production requests. No browser-side AI secret is permitted.
