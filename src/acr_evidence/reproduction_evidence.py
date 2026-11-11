"""External reproduction evidence, kept separate from target verification.

This imports documented Drupal Core Lab records. It does not claim that a
reproduction was performed on the selected OpenACR target, and an external
result never becomes a conformance result.
"""
import json
from pathlib import Path

SCHEMA_VERSION = "0.1.0"
SOURCE_PATH = Path(__file__).resolve().parents[2] / "config" / "reproduction-sources.json"


def load_sources(path=None):
    try:
        data = json.loads(Path(path or SOURCE_PATH).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"records": []}
    return data


def build_reproduction_evidence(analysis, source_path=None):
    sources = load_sources(source_path)
    findings = {finding.get("issue_id"): finding for finding in analysis.get("findings") or []}
    entries = []
    for record in sources.get("records") or []:
        issue_id = record.get("issue_id")
        finding = findings.get(issue_id)
        entries.append({
            "issue_id": issue_id,
            "in_active_collection": bool(finding),
            "issue_url": (finding or {}).get("source_url"),
            "issue_title": (finding or {}).get("title"),
            "source": sources.get("source") or "Drupal Core Lab",
            "source_url": record.get("source_url"),
            "source_core_commit": record.get("source_core_commit"),
            "source_verified_at": record.get("source_verified_at"),
            "source_result": record.get("source_result") or "not-recorded",
            "source_scope": record.get("source_scope"),
            "methods": record.get("methods") or [],
            "limitations": record.get("limitations"),
            "target_applicability": "not-established",
            "target_verified": False,
            "target_scope_note": "External Core Lab evidence; not reproduced on the selected OpenACR target.",
            "review_status": record.get("review_status") or "unreviewed",
            "conformance_result": None,
        })
    entries.sort(key=lambda item: item.get("issue_id") or "")
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "reproduction-evidence-ledger",
        "target_id": (analysis.get("target") or {}).get("assessment_id"),
        "release": (analysis.get("target") or {}).get("release"),
        "source_repository": sources.get("source_repository"),
        "disclaimer": "External reproduction evidence only. It does not verify the selected target and does not establish conformance.",
        "summary": {
            "records": len(entries),
            "in_active_collection": sum(1 for item in entries if item["in_active_collection"]),
            "target_verified": 0,
            "external_only": sum(1 for item in entries if item["in_active_collection"]),
        },
        "entries": entries,
    }
