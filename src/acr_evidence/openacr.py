"""Preliminary review worksheet. NOT a schema-valid OpenACR export."""

def export_worksheet(evidence, path):
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("Install optional dependency: pip install -e '.[yaml]'") from exc
    content = {
        "document_type": "openacr-authoring-worksheet-NOT-AN-OPENACR",
        "warning": "No WCAG conformance determinations made. Do not import as an approved ACR.",
        "target": evidence["assessment"],
        "evidence_digest": evidence["evidence_digest"],
        "criterion_evidence": {}
    }
    for issue in evidence["findings"]:
        for criterion in issue["wcag_candidates"]:
            content["criterion_evidence"].setdefault(criterion, []).append({
                "issue_id": issue["issue_id"],
                "applicability": issue["applicability"],
                "source_url": issue["source_url"],
                "remarks_suggestion": None,
                "human_conformance_decision": None
            })
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(content, f, sort_keys=False, allow_unicode=True)
    return path
