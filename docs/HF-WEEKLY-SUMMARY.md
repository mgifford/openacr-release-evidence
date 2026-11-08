# Weekly ACR digest with an optional Hugging Face summary

The weekly job can produce a deterministic digest of what changed and, optionally,
a short executive summary written by a pinned Hugging Face model. The model never
calculates counts or assigns ACR results.

## What is generated

```text
reports/weekly/YYYY-MM-DD.facts.json
reports/weekly/YYYY-MM-DD.md
reports/weekly/YYYY-MM-DD.provenance.json
reports/weekly/index.md
```

- `facts.json` is derived from the current and previous collections. It contains
  counts, status changes, new/no-longer-active issues, RTBC changes, criterion
  tag changes, target counts, ATAG changes and artifact hashes.
- `md` contains the deterministic digest plus the optional AI executive summary.
- `provenance.json` records provider, model, route, revision, prompt version,
  input/output hashes and AI status.
- `index.md` is the weekly trend table.

The digest is **not** an ACR and does not modify `openacr.yaml`, `acr.html` or
`acr.md`.

## Hugging Face setup

### 1. Choose a model and route

For evaluation, use a Hugging Face **Inference Provider** and a chat/instruction
model that is licensed for your use.

For a stable weekly process, use a **dedicated Inference Endpoint** running the
exact model revision you evaluated. This avoids provider-side model changes.

### 2. Create a token

Create a fine-grained Hugging Face token with inference access. Do not commit it.

### 3. Add GitHub configuration

Add these to the repository’s Actions secrets/variables:

| Name | Kind | Purpose |
|---|---|---|
| `HF_TOKEN` | Secret | Hugging Face inference token |
| `HF_MODEL` | Variable | Model ID available to your account |
| `HF_PROVIDER` | Variable | Inference Provider name, or `auto` |
| `HF_ENDPOINT` | Variable | Optional dedicated endpoint URL |
| `HF_MODEL_REVISION` | Variable | Optional revision/version recorded in provenance |

If `HF_TOKEN` is absent, the workflow still generates the deterministic digest
and marks AI as disabled.

### 4. Install the optional client

The weekly workflow installs:

```sh
python -m pip install -e '.[openacr,summaries]'
```

`summaries` adds `huggingface_hub` (Apache-2.0). The core report path does not
depend on it.

### 5. Run the workflow

Use **Actions → Weekly Drupal Core evidence snapshot → Run workflow**, or wait for
the Monday 13:00 UTC schedule.

The weekly PR will contain `reports/weekly/<date>.md`. Review the digest and the
provenance before merging.

## Model stability

- Pin `huggingface_hub`.
- Pin the model ID and provider; prefer a dedicated endpoint for strict
  reproducibility.
- Pin the prompt version (`weekly-evidence-v1`).
- Use temperature `0` and a fixed seed.
- Record model revision, input hash and output hash.
- Do not auto-upgrade the model; a change requires a new evaluation.

## Guardrails

The AI output is accepted only if:

- it is under 300 words;
- it contains no Supports/Partially Supports/Does Not Support, conformant,
  compliant, pass/fail, fixed, resolved or percentage language;
- every number appears in the facts;
- every `drupal:NNN` ID appears in the facts;
- it contains no unknown issue IDs.

On rejection or provider failure, the deterministic digest is used and the
provenance records `rejected` or `failed` with a short reason.

## Tracking changes over time

- Each week gets an immutable file; nothing overwrites an earlier digest.
- `index.md` summarizes active, new, no-longer-active, RTBC, detailed and
  inventory counts.
- “No longer active” is not a claim that an issue was fixed.
- The facts are the source of truth; the AI writes only the executive summary.

## Privacy and prompt injection

Only aggregated facts and selected public issue titles are sent. Comments, raw
evidence, private snapshots and tokens are not sent. Issue titles are delimited
as untrusted data; the model has no tools and cannot approve or publish.

## Adding Cloudflare later

The same facts and validation layer can support a Cloudflare Workers AI provider.
The provider is selected by configuration; the no-AI path remains the default.
