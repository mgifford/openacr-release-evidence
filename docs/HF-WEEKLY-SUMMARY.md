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

## Only issues with new activity

The weekly digest does not ask the model to summarize the whole 428-issue queue.
It compares the current collection with the previous snapshot and builds an
`activity.changed` list.

Activity signals include:

- the issue's `updated_at`/`changed` timestamp;
- status changes, including a return to an active status;
- new or changed comments (where comments were collected);
- new or changed merge requests, including state or head changes;
- description, title, component, version or criterion-tag changes;
- a change from metadata-only inventory to detailed evidence.

Newly active issues are included. Issues that left the active list are listed as
**no longer active**, not fixed.

If no issue has new activity, the model is **not called**. The digest records
`status: skipped` and still writes the deterministic snapshot.

### Fixed and reopened issues

Snapshots can miss a close/reopen cycle that happens between weekly runs. If an
issue was closed at the previous snapshot, it is absent from that active
collection; when it returns, the digest reports it as newly active. If it was
active at both snapshots but was closed and reopened in between, the changed
timestamp, new comments or MR changes will usually show activity, but the digest
does not claim it was reopened unless the evidence says so.

Inventory-only issues expose the changed timestamp and status but not their full
comments/MRs; code-only activity without an issue update may not be detected.

## Hugging Face setup

### 1. Choose a model and route

For evaluation, use a Hugging Face **Inference Provider** and a chat/instruction
model that is licensed for your use.

For a stable weekly process, use a **dedicated Inference Endpoint** running the
exact model revision you evaluated. This avoids provider-side model changes.

### Recommended starting models

These are starting points, not permanent endorsements. Provider availability and
model licences change; check the model page before setting `HF_MODEL`.

| Model | Why | Notes |
|---|---|---|
| `Qwen/Qwen2.5-7B-Instruct` | Good first choice: non-reasoning instruction model, 7B, concise summaries | Available through Inference Providers at the time of writing; use `HF_PROVIDER=auto` |
| `meta-llama/Llama-3.1-8B-Instruct` | Strong instruction following; widely supported | Gated model: accept the licence and give the token gated-repo read access |
| `Qwen/Qwen3-14B` | Stronger writing quality if 7B is too shallow | May emit reasoning; may need more tokens/time |
| `mistralai/Mistral-7B-Instruct-v0.3` | Concise, stable 7B alternative | Check current provider support |

Avoid for this job:

- **GGUF files** such as `*-gguf`; they are for local llama.cpp/Ollama and are not
  generally available through Inference Providers.
- **Preview or fine-tuned summarizer experiments** with no provider mapping,
  model card, or licence review.
- **Base models** without a chat/instruction template.
- **Very small models under ~3B**; they are more likely to blur counts or invent
  wording.

For example, the proposed
`mithulaartigala/reasoning-summarizer-qwen3.5-0.8b-preview-gguf` is a GGUF
preview with no Inference Provider mapping and a 0.8B base. It is not a good fit
for this workflow. Use a provider-backed instruction model instead.

`HF_PROVIDER=auto` is the right first setting. If auto fails, copy a provider
from the model page's **Inference Providers** section into `HF_PROVIDER`.

#### Do you need a dedicated endpoint?

Not to start.

- **Inference Providers** are shared serverless inference. Cheapest and simplest.
- **Dedicated Inference Endpoints** deploy a model to an endpoint you control,
  with a pinned revision and predictable capacity. They cost hourly and require
  more setup.

Start with `auto`. Move to a dedicated endpoint only if you need exact model
revision enforcement, higher reliability, or no shared-provider variance. If you
do, set `HF_ENDPOINT` and `HF_MODEL_REVISION`.

#### How to evaluate a model without a formal eval team

Use the same facts file for each model and read the executive summary against
the deterministic sections.

| Check | What to do |
|---|---|
| Facts | Every number and issue ID must appear in the facts; the validator checks this automatically |
| Safety | No Supports/Partially Supports/Does Not Support, compliant, fixed, resolved or percentage language; the validator checks this |
| Coverage | Does it mention the active count, the main changes, RTBC, and the inventory limitation? |
| Clarity | Is it 2–3 short paragraphs, readable, and free of invented causes? |
| Stability | Record model, provider, revision and prompt version |

The model only writes the executive summary. The rest of the digest is
deterministic, so a weak model cannot change the counts.

**Practical rule:** choose the smallest provider-backed instruction model that
passes validation and produces a clear summary. For this workload, a 7B–14B
instruction model is usually enough. There is no need to start with a large
reasoning model.

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
