"""Optional AI summaries for ACR criterion barrier paragraphs.

The ACR remains a draft. A criterion summary is cached by issue-content hash,
model and prompt version. A failed or rejected response is never used; the ACR
falls back to deterministic issue-title summaries.
"""
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

PROMPT_VERSION = "acr-criterion-v2"
MODEL_DEFAULT = "Qwen/Qwen2.5-7B-Instruct"
BANNED = re.compile(
    r"\b(?:supports?|partially\s+supports?|does\s+not\s+support|conformant|"
    r"compliant|compliance|pass(?:es|ed)?|fail(?:s|ed)?|fixed|resolved)\b|%",
    re.IGNORECASE,
)
ISSUE_ID = re.compile(r"drupal:\d+")
SYSTEM_PROMPT = """You write concise barrier summaries for a draft Accessibility Conformance Report.

Use only the supplied Drupal issue evidence. Return JSON only, with this shape:
{"web": "one short paragraph", "authoring": "one short paragraph"}

Each paragraph should be 80-140 words and three to five sentences. Explain the known barrier patterns, the tasks and people affected, and the practical impact for the public web and for the authoring tool separately. If a component has no classified issue, say that no issue is classified for it rather than inventing a barrier. Do not use conformance terms (Supports, Partially Supports, Does Not Support, compliant, pass, fail, fixed or resolved). Do not invent issue IDs, numbers, causes, severity or reviewers. Do not repeat the raw issue list. This is a draft suggestion for human review.
"""


def _hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _read(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _evidence(collection):
    groups = {}
    for issue in collection.get("issues") or []:
        for criterion in issue.get("wcag_candidates") or []:
            groups.setdefault(str(criterion), []).append(issue)
    evidence = {}
    for criterion, issues in sorted(groups.items()):
        web = []
        authoring = []
        for issue in issues:
            surface = (issue.get("surface") or {}).get("surface", "web")
            record = {
                "id": issue.get("id"),
                "title": issue.get("title") or "",
                "status": (issue.get("status") or {}).get("label") or "unknown",
                "evidence": issue.get("evidence_status") or "inventory",
            }
            description = (issue.get("description_text") or "").strip()
            if description:
                record["description"] = description[:500]
            (authoring if surface == "authoring" else web).append(record)
        evidence[criterion] = {"web": web, "authoring": authoring}
    return evidence


def _valid(text, evidence):
    if not isinstance(text, str) or not text.strip():
        return False
    if len(re.findall(r"\S+", text)) > 180:
        return False
    if BANNED.search(text):
        return False
    allowed_ids = {item["id"] for items in evidence.values() for item in items}
    for issue_id in ISSUE_ID.findall(text):
        if issue_id not in allowed_ids:
            return False
    allowed_numbers = set(re.findall(r"\b\d+\b", json.dumps(evidence, ensure_ascii=False)))
    for number in re.findall(r"\b\d+\b", text):
        if number not in allowed_numbers:
            return False
    return True


def _parse_json(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object in response")
    return json.loads(text[start:end + 1])


def _client(model, provider, endpoint, token, client_factory):
    endpoint = endpoint or None
    if not os.environ.get("HF_ENDPOINT"):
        os.environ.pop("HF_ENDPOINT", None)
    if client_factory:
        return client_factory(model=model, provider=provider, token=token, base_url=endpoint)
    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise RuntimeError("Install the summaries extra: pip install -e '.[summaries]'") from exc
    kwargs = {"token": token, "model": model}
    if provider:
        kwargs["provider"] = provider
    if endpoint:
        kwargs["base_url"] = endpoint
    return InferenceClient(**kwargs)


def summarize_collection(
    collection,
    output,
    provider="huggingface",
    model=None,
    provider_name=None,
    endpoint=None,
    token=None,
    client_factory=None,
):
    """Generate accepted per-criterion summaries and write the cache."""
    if provider != "huggingface":
        raise ValueError("Only the huggingface provider is supported")
    if not token:
        raise RuntimeError("HF_TOKEN is not configured")
    if not model:
        raise RuntimeError("HF_MODEL is not configured")
    evidence = _evidence(collection)
    previous = _read(output)
    previous_criteria = previous.get("criteria") or {}
    client = None
    result = {
        "schema_version": "0.1.0",
        "prompt_version": PROMPT_VERSION,
        "provider": provider,
        "provider_name": provider_name,
        "model": model,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "criteria": {},
    }
    for criterion, groups in evidence.items():
        input_hash = _hash(groups)
        cached = previous_criteria.get(criterion) or {}
        if (
            cached.get("status") == "accepted"
            and cached.get("input_sha256") == input_hash
            and cached.get("model") == model
            and cached.get("prompt_version") == PROMPT_VERSION
        ):
            result["criteria"][criterion] = cached
            continue
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({"criterion": criterion, "issues": groups}, ensure_ascii=False)},
        ]
        entry = {
            "input_sha256": input_hash,
            "model": model,
            "prompt_version": PROMPT_VERSION,
            "status": "failed",
            "web": "",
            "authoring": "",
        }
        try:
            if client is None:
                client = _client(model, provider_name, endpoint, token, client_factory)
            response = client.chat_completion(messages=messages, max_tokens=900, temperature=0.0, seed=17)
            raw = response.choices[0].message.content or ""
            parsed = _parse_json(raw)
            web = str(parsed.get("web") or "").strip()
            authoring = str(parsed.get("authoring") or "").strip()
            if not _valid(web, groups) or not _valid(authoring, groups):
                entry["status"] = "rejected"
                entry["error"] = "summary failed validation"
            else:
                entry.update({"status": "accepted", "web": web, "authoring": authoring})
        except Exception as exc:
            entry["status"] = "failed"
            entry["error"] = f"{type(exc).__name__}: {exc}"[:300]
        result["criteria"][criterion] = entry
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
