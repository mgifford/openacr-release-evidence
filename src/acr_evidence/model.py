"""Small, explicit domain contract with conservative applicability defaults.

Schema 0.2.0 adds:
- per-finding assessment target and observation timestamp;
- a reproducible published-artifact digest plus an input manifest digest;
- explicit rejection of placeholder release/ref values unless a manifest is
  marked synthetic.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

SCHEMA_VERSION = "0.2.0"

APPLICABILITY = frozenset({
    "confirmed-affected",
    "likely-affected",
    "confirmed-fixed",
    "not-introduced",
    "not-in-scope",
    "unknown",
})

# Verified against live Drupal.org issue pages on 2026-11-07. Codes 9-12 did not
# appear in the core queue at audit time, so they deliberately remain unknown
# rather than being guessed from an older status vocabulary.
STATUS_LABELS = {
    1: "Active",
    2: "Fixed",
    3: "Closed (duplicate)",
    4: "Postponed",
    5: "Closed (won't fix)",
    6: "Closed (works as designed)",
    7: "Closed (fixed)",
    8: "Needs review",
    13: "Needs work",
    14: "Reviewed & tested by the community",
    15: "Patch (to be ported)",
    16: "Postponed (maintainer needs more info)",
    17: "Closed (outdated)",
    18: "Closed (cannot reproduce)",
}

STATUS_WORKFLOW = {
    1: "open",
    2: "fixed-unverified",
    3: "closed-other",
    4: "postponed",
    5: "closed-other",
    6: "closed-other",
    7: "closed-fixed",
    8: "needs-review",
    13: "needs-work",
    14: "rtbc",
    15: "patch",
    16: "postponed",
    17: "closed-other",
    18: "closed-other",
}

# Statuses that still need review in an ACR evidence pass. Fixed/closed issues
# are excluded; RTBC and patch-to-be-ported stay in until the issue is closed.
ACR_REVIEW_STATUSES = (1, 8, 13, 14, 15)
ACR_REVIEW_STATUS_LABELS = {
    1: "Active",
    8: "Needs review",
    13: "Needs work",
    14: "Reviewed & tested by the community",
    15: "Patch (to be ported)",
}


def is_acr_review_status(code):
    try:
        return int(code) in ACR_REVIEW_STATUSES
    except (TypeError, ValueError):
        return False

PLACEHOLDER_RE = re.compile(
    r"(TEMPLATE|SET-A-REAL|SET-EXACT|EXAMPLE|UNVERIFIED|TODO|CHANGEME|REPLACE-ME)",
    re.IGNORECASE,
)


def sha256_json(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def valid_public_url(url):
    if not isinstance(url, str):
        return False
    parts = urlsplit(url)
    return parts.scheme == "https" and bool(parts.hostname) and not parts.username and not parts.password


def is_iso8601(value):
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def status_label(code):
    if isinstance(code, str) and code.isdigit():
        code = int(code)
    if isinstance(code, int):
        return STATUS_LABELS.get(code, f"Unknown status ({code})")
    return str(code) if code else "Unknown"


def status_workflow(code):
    if isinstance(code, str) and code.isdigit():
        code = int(code)
    if isinstance(code, int):
        return STATUS_WORKFLOW.get(code, "unknown")
    return "unknown"


def digest_artifact(artifact):
    """Hash the published artifact excluding volatile/generated fields.

    A verifier can copy an exported JSON file, delete ``generated_at`` and
    ``evidence_digest``, and recompute this value without access to private
    inputs. This is deliberately different from ``manifest_digest``, which
    covers the input manifest including overrides.
    """
    payload = {k: v for k, v in artifact.items() if k not in ("generated_at", "evidence_digest")}
    return sha256_json(payload)


def _check_placeholder(value, field, synthetic):
    if isinstance(value, str) and PLACEHOLDER_RE.search(value) and not synthetic:
        raise ValueError(
            f"Placeholder value in {field}; set 'synthetic': true for fixtures or use a real value"
        )


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
    synthetic = manifest.get("synthetic", False)
    if not isinstance(synthetic, bool):
        raise ValueError("Manifest 'synthetic' must be a boolean")
    for key in ("id", "product", "release", "ref"):
        _check_placeholder(manifest[key], key, synthetic)
    installation = manifest["installation"]
    _check_placeholder(installation.get("configuration"), "installation.configuration", synthetic)
    _check_placeholder(installation.get("profile"), "installation.profile", synthetic)

    overrides = manifest.get("applicability_overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("applicability_overrides must be an object keyed by issue ID")
    for issue_id, override in overrides.items():
        if not isinstance(override, dict):
            raise ValueError(f"Invalid applicability override for {issue_id}")
        if override.get("status") not in APPLICABILITY:
            raise ValueError(f"Invalid applicability status for {issue_id}")
        if not override.get("reason") or not override.get("basis"):
            raise ValueError(f"Missing evidence rationale for {issue_id}")
        urls = override.get("evidence_urls", [])
        if not urls or not all(valid_public_url(u) for u in urls):
            raise ValueError(f"Expected HTTPS evidence URLs for {issue_id}")
        observed_at = override.get("observed_at")
        if observed_at is not None and not is_iso8601(observed_at):
            raise ValueError(f"Invalid observation timestamp for {issue_id}")
        reviewer = override.get("reviewer")
        if reviewer is not None and (not isinstance(reviewer, str) or not reviewer.strip()):
            raise ValueError(f"Invalid reviewer for {issue_id}")
    return manifest


def normalize_issue(issue):
    for key in ("source", "id", "title", "url"):
        if not isinstance(issue.get(key), str) or not issue[key]:
            raise ValueError(f"Missing issue field {key}")
    if not valid_public_url(issue["url"]):
        raise ValueError("Issue URL must use HTTPS")
    result = {
        key: issue.get(key)
        for key in (
            "source",
            "id",
            "url",
            "title",
            "description",
            "status",
            "updated_at",
            "component",
            "raw_version",
            "observed_at",
            "fetched_at",
            "tracker_status_label",
        )
    }
    result["issue_id"] = f"{issue['source']}:{issue['id']}"
    result["status_code"] = issue.get("status")
    result["tracker_status_label"] = (
        issue.get("tracker_status_label") or status_label(issue.get("status"))
    )
    result["workflow_state"] = status_workflow(issue.get("status"))
    result["observed_at"] = issue.get("observed_at") or issue.get("fetched_at")
    result["wcag_candidates"] = [
        str(x) for x in issue.get("wcag_candidates", []) if isinstance(x, (str, int))
    ]
    return result


def assess(manifest, issues, generated_at=None):
    validate_manifest(manifest)
    generated_at = generated_at or utcnow()
    target = {
        "product": manifest["product"],
        "release": manifest["release"],
        "ref": manifest["ref"],
    }
    records = []
    seen = set()
    for raw in issues:
        issue = normalize_issue(raw)
        key = issue["issue_id"]
        if key in seen:
            raise ValueError(f"Duplicate issue identifier {key}")
        seen.add(key)
        override = manifest.get("applicability_overrides", {}).get(key)
        observed_at = issue.get("observed_at")
        if override and override.get("observed_at"):
            observed_at = override["observed_at"]
        observed_at_basis = "source-retrieval" if observed_at else "artifact-generation"
        assessment = {
            "schema_version": SCHEMA_VERSION,
            "assessment_id": manifest["id"],
            "target": target,
            "issue_id": key,
            "source_url": issue["url"],
            "title": issue["title"],
            "component": issue["component"],
            "tracker_status": issue["status"],
            "tracker_status_label": issue["tracker_status_label"],
            "tracker_version": issue["raw_version"],
            "source_updated_at": issue["updated_at"],
            "observed_at": observed_at or generated_at,
            "observed_at_basis": observed_at_basis,
            "wcag_candidates": issue["wcag_candidates"],
            "applicability": override["status"] if override else "unknown",
            "reason": override["reason"]
            if override
            else "No target-specific evidence supplied; issue status alone does not establish release applicability.",
            "basis": override["basis"] if override else "none",
            "evidence_urls": override["evidence_urls"] if override else [],
            "review_status": "unreviewed"
            if not override
            else "evidence-supplied-not-independently-verified",
        }
        if override and override.get("reviewer"):
            assessment["reviewer"] = override["reviewer"]
        records.append(assessment)
    records.sort(key=lambda x: x["issue_id"])
    public_assessment = {k: v for k, v in manifest.items() if k != "applicability_overrides"}
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "release-accessibility-evidence-draft",
        "disclaimer": "Draft evidence only; not an accessibility conformance report or certification.",
        "assessment": public_assessment,
        "generated_at": generated_at,
        "findings": records,
        "manifest_digest": sha256_json(manifest),
        "digest_scope": "sha256 over this artifact excluding generated_at and evidence_digest",
    }
    artifact["evidence_digest"] = digest_artifact(artifact)
    return artifact
