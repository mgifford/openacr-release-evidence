"""Structured criterion evidence, separate from conformance determinations.

Issue-queue evidence can describe reported barriers and candidate criterion
relationships. It cannot establish Supports, Partially Supports or Does Not
Support. This artifact records what is known, what is unreviewed and what is
still missing; conformance_result remains null until a human assessment exists.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from .openacr_export import load_catalog

AUTOMATION_PATH = Path(__file__).resolve().parents[2] / "config" / "wcag-automation-coverage.json"
_AUTOMATION = None


def automation_for_criterion(criterion):
    """Return partial automated coverage for a criterion, if any.

    ACT/axe mappings indicate that a rule engine can evaluate some part of the
    criterion. They do not establish that the rule passed or that the criterion
    is supported. Guidepup is a separate behavioral method, not an ACT/axe rule.
    """
    global _AUTOMATION
    if _AUTOMATION is None:
        try:
            _AUTOMATION = json.loads(AUTOMATION_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _AUTOMATION = {"criteria": {}}
    item = (_AUTOMATION.get("criteria") or {}).get(str(criterion)) or {}
    axe = list(item.get("axe") or [])
    act = list(item.get("act") or [])
    return {
        "axe_rules": axe,
        "act_rules": act,
        "coverage": "partial" if (axe or act) else "none",
        "result": "not-recorded",
        "guidepup": "method-available-not-recorded",
    }

SCHEMA_VERSION = "0.1.0"
PRODUCT_SCOPE_NA = {
    "1.2.1": "Drupal Core does not provide audio/video playback out of the box; use a contributed media player.",
    "1.2.3": "Drupal Core does not provide audio description or media alternatives out of the box.",
    "1.2.4": "Drupal Core has no core live audio/video feature.",
    "1.2.5": "Drupal Core has no core video player or audio-description feature.",
}
COMPONENT_IDS = ("web", "electronic-docs", "software", "authoring-tool")


def _issue_record(finding):
    return {
        "issue_id": finding.get("issue_id"),
        "source_url": finding.get("source_url"),
        "title": finding.get("title"),
        "component": finding.get("component"),
        "tracker_status": finding.get("tracker_status_label"),
        "evidence_status": finding.get("evidence_status"),
        "release_applicability": finding.get("applicability"),
        "surface": (finding.get("surface") or {}).get("surface", "web"),
        "fix_included_in_target": bool(finding.get("fix_included_in_target")),
    }


def build_criterion_evidence(analysis):
    """Build a deterministic, version-specific evidence ledger.

    No formal adherence result is emitted. A criterion relationship is a
    candidate until reviewed; an empty queue is insufficient evidence, not a
    pass or a scope exclusion.
    """
    assessment = analysis.get("assessment") or {}
    target = analysis.get("target") or {}
    product = assessment.get("product") or target.get("product") or "Unknown product"
    release = target.get("release") or assessment.get("release") or "unknown"
    findings = analysis.get("findings") or []
    by_criterion = {}
    for finding in findings:
        for criterion in finding.get("wcag_candidates") or []:
            by_criterion.setdefault(str(criterion), []).append(finding)
    catalog = load_catalog()
    criteria = []
    for chapter in catalog.get("chapters") or []:
        for criterion in chapter.get("criteria") or []:
            criterion_id = str(criterion.get("id"))
            items = by_criterion.get(criterion_id, [])
            components = []
            for name in COMPONENT_IDS:
                surface = "authoring" if name == "authoring-tool" else "web"
                if name in {"electronic-docs", "software"}:
                    state = "outside-documented-scope"
                    component_issues = []
                    basis = "Drupal Core is a web CMS; no separate electronic-document or packaged-software product is in this scope."
                elif criterion_id in PRODUCT_SCOPE_NA:
                    state = "outside-documented-scope"
                    component_issues = []
                    basis = PRODUCT_SCOPE_NA[criterion_id]
                else:
                    component_issues = [
                        item for item in items
                        if (item.get("surface") or {}).get("surface", "web") == surface
                    ] if surface in {"web", "authoring"} else []
                    if component_issues:
                        state = "reported-barrier-unverified"
                        basis = "Active Drupal.org issue tagged with this criterion; not reproduced against the target."
                    else:
                        state = "insufficient-evidence"
                        basis = "No active tagged issue; absence is not evidence of support or inapplicability."
                components.append({
                    "component": name,
                    "evidence_state": state,
                    "scope_basis": basis,
                    "candidate_relationship": "issue-tag" if component_issues else "none",
                    "relationship_review_status": "unreviewed" if component_issues else "not-reviewed",
                    "verification_status": "not-reproduced" if component_issues else "not-tested",
                    "conformance_result": None,
                    "issues": [_issue_record(item) for item in component_issues],
                    "gaps": (
                        ["Reproduction on the exact target", "Review of the criterion mapping"]
                        if component_issues else
                        ["No positive evidence recorded"]
                    ),
                })
            criteria.append({
                "criterion": criterion_id,
                "handle": criterion.get("handle"),
                "level": chapter.get("id"),
                "automation": automation_for_criterion(criterion_id),
                "components": components,
                "review_status": "unreviewed",
                "reviewer": None,
                "reviewed_at": None,
            })
    summary = {
        "criteria": len(criteria),
        "reported_barrier": sum(
            1 for item in criteria
            for comp in item["components"]
            if comp["evidence_state"] == "reported-barrier-unverified"
        ),
        "insufficient_evidence": sum(
            1 for item in criteria
            for comp in item["components"]
            if comp["evidence_state"] == "insufficient-evidence"
        ),
        "outside_documented_scope": sum(
            1 for item in criteria
            for comp in item["components"]
            if comp["evidence_state"] == "outside-documented-scope"
        ),
        "automated_coverage": sum(
            1 for item in criteria
            if item["automation"]["coverage"] == "partial"
        ),
        "formal_conformance_results": 0,
        "reviewed_criteria": 0,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "criterion-evidence-ledger",
        "standard": "WCAG 2.2 / Section 508",
        "product": product,
        "release": release,
        "target_id": target.get("assessment_id") or assessment.get("id"),
        "target_ref": target.get("ref"),
        "generated_at": analysis.get("generated_at") or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "disclaimer": "Reported issue evidence only. No conformance result is assigned. Supports and Not Applicable require human-reviewed evidence.",
        "summary": summary,
        "criteria": criteria,
    }
