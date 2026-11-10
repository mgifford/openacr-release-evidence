# Cloudflare Workers AI summaries (exploratory)

Cloudflare is an **optional alternative/comparison provider**. It is not enabled
in the scheduled workflow by default. Hugging Face remains the primary route
until a blind comparison shows Cloudflare is better for this workload.

## Configuration

Repository/environment values:

```sh
export CLOUDFLARE_ACCOUNT_ID="..."
export CLOUDFLARE_API_TOKEN="..."
export CLOUDFLARE_MODEL="@cf/meta/llama-3.1-8b-instruct"
```

The API token should be scoped to Workers AI. Do not use a global API key.
Pin a supported Workers AI instruct model; avoid preview/GGUF-only checkpoints.

## Criterion summaries

Write a separate comparison cache so the primary ACR is untouched:

```sh
acr-evidence criterion-summaries \
  --collection reports/collection.json \
  --output reports/acr-summaries-cloudflare.json \
  --provider cloudflare \
  --model "$CLOUDFLARE_MODEL"
```

The ACR reads `reports/acr-summaries.json` by default. To use a reviewed
Cloudflare cache, copy/rename it to that primary path in a reviewed PR; do not
overwrite the Hugging Face cache automatically.

## Weekly digest

Use a separate output directory for comparison:

```sh
acr-evidence weekly-summary \
  --current-collection reports/collection.json \
  --previous-collection /tmp/previous-reports/collection.json \
  --reports reports \
  --previous-reports /tmp/previous-reports \
  --context context/DRUPAL.md \
  --output reports/weekly-cloudflare \
  --provider cloudflare \
  --model "$CLOUDFLARE_MODEL"
```

The weekly summary uses the same deterministic facts, prompt version, validator
and fallback as Hugging Face. Cloudflare failures fall back to the deterministic
digest.

## Cost and latency

Cloudflare Workers AI bills by model/neuron usage, with a limited free allocation
that changes over time. Check the current Workers AI pricing before scheduling it.

For this workload:

- one request per changed criterion;
- one weekly executive-summary request;
- accepted summaries are cached by issue-content hash and prompt version;
- rejected/failed responses are retried, so a pathological model can cost more.

A full initial criterion run can be roughly 40 requests; subsequent weeks only
re-run changed criteria. This is exploratory and should be budgeted before being
enabled in the scheduled workflow.

## Limitations

- Smaller model catalogue than Hugging Face.
- Model availability, context limits and JSON adherence vary.
- Cold starts and provider latency can be higher.
- Cloudflare can return valid text that still fails the ACR validator.
- No automatic quality advantage; compare outputs rather than assuming.
- AI Gateway adds logs/caching/rate limits but also configuration and cost.
- Do not send private evidence, credentials or non-public data.

## Comparison

Until a judge is implemented, compare manually:

1. Run Hugging Face and Cloudflare on the same collection.
2. Keep both cache files.
3. Check accepted/rejected counts.
4. Compare factual grounding, issue links, scope, Web/Authoring separation,
   specificity, readability and conformance safety.
5. Human-review the preferred variant before copying it to the primary path.

A future judge should use deterministic hard gates plus an optional model-assisted
rubric review. It should never auto-publish a winner.

## Safety

The same rules apply:

- no applicability or conformance decisions;
- no issue references, counts or quoted comments invented by the model;
- no raw comments or private evidence in prompts;
- every generated paragraph remains draft;
- human review is the publication gate.
