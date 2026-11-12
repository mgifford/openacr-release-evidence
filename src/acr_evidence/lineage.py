"""Curated component lineage records.

Lineage is evidence about how code and product scope moved. It is deliberately
separate from tracker status and release applicability:

* a removal from Core is **not** a fix;
* an adoption from contrib is **not** permission to inherit every predecessor
  issue;
* a relationship record never changes an ACR result on its own.

Records live in version-controlled JSON, carry authoritative source links and
an explicit verification state, and are validated before use.
"""
import json
from pathlib import Path

from .model import is_iso8601, sha256_json, valid_public_url

SCHEMA_VERSION = "1.0.0"
ARTIFACT_TYPE = "component-lineage"

RELATION_TYPES = frozenset({
    "introduced-into-core",
    "moved-to-contrib",
    "adopted-from-contrib",
    "renamed",
    "deprecated",
    "removed",
    "replaced",
    "split-into",
    "merged-into",
    "derived-from",
    "shares-inherited-code",
})

EVIDENCE_CLASSES = frozenset({
    "explicit-metadata",
    "verified-source-code",
    "strong-candidate",
    "weak-inferred",
    "unknown",
})

VERIFICATION_STATUSES = frozenset({"unreviewed", "reviewed", "rejected", "stale"})
COMPONENT_TYPES = frozenset({"module", "theme", "profile", "component"})


def load_lineage(path):
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_lineage(document)
    return document


def _require_component(value, field, errors):
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return
    for key in ("project", "component", "type"):
        item = value.get(key)
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{field}.{key} must be a non-empty string")
    if value.get("type") not in COMPONENT_TYPES:
        errors.append(f"{field}.type must be one of {sorted(COMPONENT_TYPES)}")
    boundary = value.get("release_boundary")
    if boundary is not None and not isinstance(boundary, dict):
        errors.append(f"{field}.release_boundary must be an object when present")


def _require_evidence(value, field, errors, evidence_class):
    if not isinstance(value, list) or not value:
        errors.append(f"{field} must be a non-empty list")
        return
    for index, item in enumerate(value):
        prefix = f"{field}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if not isinstance(item.get("kind"), str) or not item["kind"].strip():
            errors.append(f"{prefix}.kind must be a non-empty string")
        if not valid_public_url(item.get("url")):
            errors.append(f"{prefix}.url must be an HTTPS URL")
        if item.get("observed_at") is not None and not is_iso8601(item["observed_at"]):
            errors.append(f"{prefix}.observed_at must be ISO 8601")
        if evidence_class != "unknown" and not item.get("note"):
            errors.append(f"{prefix}.note is required for {evidence_class} evidence")


def validate_lineage(document):
    if not isinstance(document, dict):
        raise ValueError("Lineage document must be an object")
    if document.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Unsupported lineage schema_version: {document.get('schema_version')!r}")
    if document.get("artifact_type") != ARTIFACT_TYPE:
        raise ValueError("artifact_type must be 'component-lineage'")
    records = document.get("records")
    if not isinstance(records, list):
        raise ValueError("Lineage document needs a records list")

    errors = []
    seen = set()
    for index, record in enumerate(records):
        prefix = f"records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            errors.append(f"{prefix}.id must be a non-empty string")
        elif record_id in seen:
            errors.append(f"{prefix}.id is duplicated: {record_id}")
        else:
            seen.add(record_id)
        if record.get("relation") not in RELATION_TYPES:
            errors.append(f"{prefix}.relation must be one of {sorted(RELATION_TYPES)}")
        evidence_class = record.get("evidence_class")
        if evidence_class not in EVIDENCE_CLASSES:
            errors.append(f"{prefix}.evidence_class must be one of {sorted(EVIDENCE_CLASSES)}")
        verification = record.get("verification")
        if not isinstance(verification, dict):
            errors.append(f"{prefix}.verification must be an object")
        elif verification.get("status") not in VERIFICATION_STATUSES:
            errors.append(f"{prefix}.verification.status must be one of {sorted(VERIFICATION_STATUSES)}")
        _require_component(record.get("source"), f"{prefix}.source", errors)
        _require_component(record.get("destination"), f"{prefix}.destination", errors)
        _require_evidence(record.get("evidence"), f"{prefix}.evidence", errors, evidence_class)
        limitations = record.get("limitations")
        if limitations is not None and not (
            isinstance(limitations, list) and all(isinstance(item, str) for item in limitations)
        ):
            errors.append(f"{prefix}.limitations must be a list of strings")
    if errors:
        raise ValueError("Invalid lineage record(s): " + "; ".join(errors))
    return document


def relationships_for(records, *, project=None, component=None):
    """Return records touching a project/component, without resolving meaning."""
    matches = []
    for record in records:
        endpoints = (record.get("source") or {}, record.get("destination") or {})
        for endpoint in endpoints:
            if project is not None and endpoint.get("project") != project:
                continue
            if component is not None and endpoint.get("component") != component:
                continue
            matches.append(record)
            break
    return matches


def lineage_digest(document):
    """Stable digest of the curated records, excluding retrieval metadata."""
    return sha256_json({
        "schema_version": document.get("schema_version"),
        "records": document.get("records") or [],
    })
