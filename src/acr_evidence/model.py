"""Small, explicit domain contract with conservative applicability defaults."""
import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import urlsplit

APPLICABILITY = frozenset({"confirmed-affected", "likely-affected", "confirmed-fixed", "not-introduced", "not-in-scope", "unknown"})


def sha256_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def valid_public_url(url):
    if not isinstance(url, str):
        return False
    parts = urlsplit(url)
    return parts.scheme == "https" and bool(parts.hostname) and not parts.username and not parts.password


def validate_manifest(manifest):
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be an object")
    for key in ("id", "product", "release", "ref"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise ValueError(f"Missing required manifest string: {key}")
    if not isinstance(manifest.get("components"), list) or not manifest["components"]:
        raise ValueError("Manifest must list in-scope components")
    if not isinstance(manifest.get("installation"), dict):
        raise ValueError("Manifest needs an installation specification")
    for issue_id, override in manifest.get("applicability_overrides", {}).items():
        if override.get("status") not in APPLICABILITY:
            raise ValueError(f"Invalid applicability status for {issue_id}")
        if not override.get("reason") or not override.get("basis"):
            raise ValueError(f"Missing evidence rationale for {issue_id}")
        urls = override.get("evidence_urls", [])
        if not urls or not all(valid_public_url(u) for u in urls):
            raise ValueError(f"Expected HTTPS evidence URLs for {issue_id}")
    return manifest


def normalize_issue(issue):
    for key in ("source", "id", "title", "url"):
        if not isinstance(issue.get(key), str) or not issue[key]:
            raise ValueError(f"Missing issue field {key}")
    if not valid_public_url(issue["url"]):
        raise ValueError("Issue URL must use HTTPS")
    result = {key: issue.get(key) for key in ("source", "id", "url", "title", "description", "status", "updated_at", "component", "raw_version")}
    result["issue_id"] = f"{issue['source']}:{issue['id']}"
    result["wcag_candidates"] = [str(x) for x in issue.get("wcag_candidates", []) if isinstance(x, (str, int))]
    return result


def assess(manifest, issues, generated_at=None):
    validate_manifest(manifest)
    records = []
    seen = set()
    for raw in issues:
        issue = normalize_issue(raw)
        key = issue["issue_id"]
        if key in seen:
            raise ValueError(f"Duplicate issue identifier {key}")
        seen.add(key)
        override = manifest.get("applicability_overrides", {}).get(key)
        assessment = {
            "issue_id": key,
            "source_url": issue["url"],
            "title": issue["title"],
            "tracker_status": issue["status"],
            "tracker_version": issue["raw_version"],
            "source_updated_at": issue["updated_at"],
            "component": issue["component"],
            "wcag_candidates": issue["wcag_candidates"],
            "applicability": override["status"] if override else "unknown",
            "reason": override["reason"] if override else "No target-specific evidence supplied; issue status alone does not establish release applicability.",
            "basis": override["basis"] if override else "none",
            "evidence_urls": override["evidence_urls"] if override else [],
            "review_status": "unreviewed" if not override else "evidence-supplied-not-independently-verified"
        }
        records.append(assessment)
    records.sort(key=lambda x: x["issue_id"])
    return {
        "schema_version": "0.1.0",
        "artifact_type": "release-accessibility-evidence-draft",
        "disclaimer": "Draft evidence only; not an accessibility conformance report or certification.",
        "assessment": {k: v for k, v in manifest.items() if k != "applicability_overrides"},
        "generated_at": generated_at or utcnow(),
        "findings": records,
        "evidence_digest": sha256_json({"assessment": manifest, "findings": records})
    }
