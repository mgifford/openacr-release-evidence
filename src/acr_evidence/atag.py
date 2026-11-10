"""ATAG 2.0 authoring-tool evidence and WAI ATAG Report Tool draft export.

ATAG is separate from WCAG/OpenACR. This module identifies issues tagged
``atag`` (and explicit Part A/B tags), groups only explicitly classified issues
by Part A/Part B, and writes a WAI ATAG Report Tool JSON with every criterion
set to "Not checked". Generic ``atag`` issues are left unassigned for human
triage; component names are never used to guess a Part.
"""
import html
import json
import re
import shutil
from pathlib import Path

from .model import sha256_json

STANDARDS_DIR = Path(__file__).resolve().parent / "standards" / "atag"
CATALOG_PATH = STANDARDS_DIR / "atag-2.0.json"
REPORT_CSS = Path(__file__).resolve().parent / "static" / "report.css"
SITE_URL = "https://mgifford.github.io/openacr-release-evidence/drupal-core-atag/"
SPEC_URL = "https://www.w3.org/TR/ATAG20/"
TOOL_URL = "https://www.w3.org/WAI/atag/report-tool/"
QUEUE_URL = "https://www.drupal.org/project/issues/search?text=&projects=&assigned=&submitted=&project_issue_followers=&issue_tags_op=%3D&issue_tags=Accessibility"
ATAG_QUEUE_URL = "https://www.drupal.org/project/issues/search?text=&projects=&assigned=&submitted=&project_issue_followers=&issue_tags_op=%3D&issue_tags=atag"
PART_LABELS = {
    "A": "Part A — authoring tool UI accessibility",
    "B": "Part B — support for accessible content",
}
REVIEW_LABEL = {
    "needs-triage": "Needs ATAG Part A/B triage",
    "unreviewed": "Unreviewed",
    "not-authoring": "Not ATAG-tagged",
}


def _load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_catalog(path=None):
    return _load_json(path or CATALOG_PATH)


def load_scope(path=None):
    if path:
        return _load_json(path)
    candidate = Path("config/atag-scope.json")
    if candidate.exists():
        return _load_json(candidate)
    return {"issues": {}}


def _catalog_index(catalog=None):
    catalog = catalog or load_catalog()
    result = {}
    for principle in catalog:
        part = (principle.get("principle") or {}).get("num", "")[:1]
        for guideline in principle.get("guidelines") or []:
            for criterion in guideline.get("successcriteria") or []:
                result[criterion["num"]] = {
                    "id": criterion.get("id") or criterion["num"],
                    "num": criterion["num"],
                    "handle": criterion.get("handle") or "",
                    "level": criterion.get("level") or "",
                    "part": part,
                    "guideline": guideline.get("num") or "",
                    "principle": (principle.get("principle") or {}).get("handle") or "",
                }
    return result


def _normalise_label(label):
    text = str(label).strip().casefold().replace("_", " ").replace("-", " ")
    text = re.sub(r"[\s.]+", " ", text).strip()
    return text


def _parse_tag(label):
    """Return (is_atag, parts, criteria_numbers) for a Drupal issue tag."""
    text = _normalise_label(label)
    if not (text == "atag" or text.startswith("atag ")):
        return False, set(), set()
    tail = text[4:].strip()
    parts = set()
    criteria = set()
    # atag-a / atag-part-b / atag 2.0 part a / atag-a.3.1.1
    match = re.match(r"^(?:2\s+0\s+)?(?:part\s+)?([ab])(?:\s+)?((?:\d+\s+){2}\d+|\d+\.\d+\.\d+)$", tail)
    if match:
        parts.add(match.group(1).upper())
        number = match.group(2).replace(" ", ".")
        criteria.add(f"{match.group(1).upper()}.{number}")
    elif tail in {"a", "part a"}:
        parts.add("A")
    elif tail in {"b", "part b"}:
        parts.add("B")
    elif tail in {"2 0 a", "2 0 part a"}:
        parts.add("A")
    elif tail in {"2 0 b", "2 0 part b"}:
        parts.add("B")
    return True, parts, criteria


def classify(labels, component=None, issue_id=None, scope=None):
    """Classify ATAG tags and explicit curated scope, without component guesses."""
    scope = scope or {}
    labels = [str(label) for label in labels or []]
    parts = set()
    criteria = set()
    is_atag = False
    basis = []
    tag_basis = []
    for label in labels:
        found, tag_parts, tag_criteria = _parse_tag(label)
        if found:
            is_atag = True
            tag_basis.append(label)
            parts |= tag_parts
            criteria |= tag_criteria
    if tag_basis:
        basis.append("tag")
    entry = (scope.get("issues") or {}).get(issue_id) if issue_id else None
    if entry:
        is_atag = True
        parts |= {part.upper() for part in entry.get("parts") or []}
        criteria |= {str(item) for item in entry.get("criteria") or []}
        basis.append(entry.get("basis") or "scope-config")
    valid = _catalog_index()
    criteria = {num for num in criteria if num in valid}
    # Do not infer Part A/B from a Drupal component. A generic "atag" issue is
    # evidence of an ATAG-related report, not evidence of which Part it belongs
    # to; a human or an explicit tag must supply the Part.
    if entry and entry.get("review_status"):
        review_status = entry["review_status"]
    elif not is_atag:
        review_status = "not-authoring"
    elif parts:
        review_status = "unreviewed"
    else:
        review_status = "needs-triage"
    return {
        "is_atag": is_atag,
        "parts": sorted(parts),
        "candidate_parts": [],
        "criteria": sorted(criteria),
        "basis": "+".join(dict.fromkeys(basis)) or "none",
        "review_status": review_status,
        "tag_basis": tag_basis,
    }


def _esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def _link(url, text=None):
    if isinstance(url, str) and url.startswith("https://"):
        return f'<a href="{_esc(url)}">{_esc(text if text is not None else url)}</a>'
    return _esc(text if text is not None else url)


def _date(value):
    return str(value)[:10] if value else "Not recorded"


def _facts(rows):
    parts = ['<dl class="facts">']
    for term, value in rows:
        parts.append(f"<dt>{_esc(term)}</dt><dd>{value}</dd>")
    parts.append("</dl>")
    return "".join(parts)


def _issue_item(issue):
    atag = issue.get("atag") or {}
    labels = []
    if atag.get("parts"):
        labels.extend(PART_LABELS[p] for p in atag["parts"])
    if not labels:
        labels.append("ATAG-tagged; Part A/B not specified")
    status = (issue.get("status") or {}).get("label") or "Unknown status"
    kind = " · meta/tracker" if issue.get("issue_kind") == "meta" else ""
    return (
        "<li>"
        f'<a href="{_esc(issue.get("url"))}">{_esc(issue.get("title"))}</a> '
        f'<span class="state">{" · ".join(_esc(item) for item in labels)}</span>'
        f'<span class="meta"> — {_esc(status)} · {_esc(issue.get("component") or "No component")} · '
        f'{_esc(issue.get("id"))}</span>'
        "</li>"
    )


def _issue_list(issues):
    if not issues:
        return "<p>No issues in this group.</p>"
    return '<ul class="finding-list">' + "".join(_issue_item(issue) for issue in issues) + "</ul>"


def build_report_json(collection, issues):
    catalog = load_catalog()
    assessment = collection.get("assessment") or {}
    release = assessment.get("release") or "unknown"
    generated = collection.get("generated_at") or ""
    evaluation = {}
    for principle in catalog:
        for guideline in principle.get("guidelines") or []:
            for criterion in guideline.get("successcriteria") or []:
                level = criterion.get("level") or ""
                evaluated = "Level AA" if level == "A, AA, AAA" else f"Level {level}"
                evaluation[criterion.get("id") or criterion["num"]] = {
                    "id": criterion.get("id") or criterion["num"],
                    "num": criterion["num"],
                    "handle": criterion.get("handle") or "",
                    "result": "Not checked",
                    "observations": None,
                    "level": level,
                    "evaluatedLevel": evaluated,
                }
    summary = (
        f"DRAFT ATAG 2.0 authoring-tool evidence for {assessment.get('product', 'Drupal Core')} "
        f"{release}. {len(issues)} ATAG-tagged issues were collected from Drupal.org. "
        "No ATAG conformance values are populated; every criterion is 'Not checked'. "
        f"Evidence report: {SITE_URL}. A human reviewer must complete the ATAG Report Tool evaluation."
    )
    return {
        "evaluationData": evaluation,
        "meta": {
            "name": {"id": "name", "value": f"{assessment.get('product', 'Drupal Core')} {release} authoring tool — ATAG 2.0 draft"},
            "website": {"id": "website", "value": SITE_URL},
            "executiveSummary": {"id": "executiveSummary", "value": summary},
            "evaluatorName": {"id": "evaluatorName", "value": "Unassigned reviewer (draft)"},
            "evaluatorOrg": {"id": "evaluatorOrg", "value": "Unassigned organization (draft)"},
            "evaluationId": {"id": "evaluationId", "value": f"{release}-{_date(generated)}"},
            "conformanceTarget": {"id": "conformanceTarget", "value": "AA"},
            "createdWith": {"id": "createdWith", "value": "openacr-release-evidence 0.2.0"},
        },
    }


def _missing_message(count):
    if count == 0:
        return ('<p>No ATAG-tagged issues are missing the common Accessibility tag in this snapshot.</p>')
    if count == 1:
        return ('<p>1 ATAG-tagged issue does not currently carry the common Accessibility tag. '
                'It is included here so it is not lost, but it will not appear in the Accessibility-only queue '
                'filter. Add the Accessibility tag through the normal issue workflow.</p>')
    return (f'<p>{count} ATAG-tagged issues do not currently carry the common Accessibility tag. '
            'They are included here so they are not lost, but they will not appear in the Accessibility-only '
            'queue filter. Add the Accessibility tag through the normal issue workflow.</p>')


def render_atag_report(collection, output_dir, scope=None):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    scope = scope if scope is not None else load_scope()
    issues = []
    for issue in collection.get("issues") or []:
        labels = issue.get("labels") or []
        atag = classify(labels, issue.get("component"), issue.get("id"), scope)
        record = dict(issue)
        record["atag"] = atag
        record["accessibility_tag"] = any(str(label).casefold() == "accessibility" for label in labels)
        record["missing_accessibility_tag"] = bool(atag["is_atag"] and not record["accessibility_tag"])
        record["issue_kind"] = "meta" if re.match(r"^\s*\[meta\]", str(record.get("title") or ""), re.I) else "issue"
        issues.append(record)
    atag_issues = [issue for issue in issues if (issue.get("atag") or {}).get("is_atag")]
    meta_issues = [issue for issue in atag_issues if issue.get("issue_kind") == "meta"]
    substantive = [issue for issue in atag_issues if issue.get("issue_kind") != "meta"]
    explicit_a = [issue for issue in substantive if "A" in issue["atag"]["parts"]]
    explicit_b = [issue for issue in substantive if "B" in issue["atag"]["parts"]]
    unspecified = [issue for issue in substantive if not issue["atag"]["parts"]]
    missing_accessibility = [issue for issue in atag_issues if issue["missing_accessibility_tag"]]
    assessment = collection.get("assessment") or {}
    release = assessment.get("release") or "unknown"
    summary = {
        "issues": len(atag_issues),
        "explicit_part_a": len(explicit_a),
        "explicit_part_b": len(explicit_b),
        "unspecified": len(unspecified),
        "meta_issues": len(meta_issues),
        "missing_accessibility_tag": len(missing_accessibility),
        "criteria": len(_catalog_index()),
    }
    evidence = {
        "schema_version": "0.2.0",
        "artifact_type": "atag-evidence-draft",
        "atag_version": "2.0",
        "product": assessment.get("product"),
        "release": release,
        "generated_at": collection.get("generated_at"),
        "source": {
            "tag": "atag",
            "tag_tid": "5050",
            "accessibility_tag": "Accessibility",
            "queue_url": QUEUE_URL,
            "atag_queue_url": ATAG_QUEUE_URL,
            "atag_spec": SPEC_URL,
            "wai_report_tool": TOOL_URL,
            "wai_report_tool_repository": "https://github.com/w3c/wai-atag-report-tool",
        },
        "summary": summary,
        "issues": [
            {
                "issue_id": issue.get("id"),
                "title": issue.get("title"),
                "url": issue.get("url"),
                "component": issue.get("component"),
                "status": (issue.get("status") or {}).get("label"),
                "issue_kind": issue.get("issue_kind"),
                "atag": issue.get("atag"),
                "accessibility_tag": issue.get("accessibility_tag"),
                "missing_accessibility_tag": issue.get("missing_accessibility_tag"),
            }
            for issue in atag_issues
        ],
        "review_status": "unreviewed",
        "notes": "ATAG is separate from WCAG/OpenACR. No ATAG conformance values are populated.",
    }
    evidence["evidence_digest"] = sha256_json({k: v for k, v in evidence.items() if k not in ("generated_at", "evidence_digest")})
    (output / "atag-evidence.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_json = build_report_json(collection, atag_issues)
    (output / "atag-report.json").write_text(json.dumps(report_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.copyfile(REPORT_CSS, output / "report.css")

    rows = [
        ("Product", _esc(assessment.get("product"))),
        ("Release context (not applicability-scoped)", _esc(release)),
        ("ATAG version", "2.0"),
        ("Source tags", "Accessibility + atag (taxonomy term 5050)"),
        ("Collection date", _esc(_date(collection.get("generated_at")))),
        ("ATAG-tagged issues", _esc(summary["issues"])),
        ("Explicit Part A / Part B (non-meta)", f'{summary["explicit_part_a"]} / {summary["explicit_part_b"]}'),
        ("ATAG-tagged, part not specified (non-meta)", _esc(summary["unspecified"])),
        ("Meta/tracker issues", _esc(summary["meta_issues"])),
        ("Missing Accessibility tag", _esc(summary["missing_accessibility_tag"])),
        ("ATAG criteria", _esc(summary["criteria"]) + " (WAI ATAG Report Tool)"),
    ]
    html_parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="description" content="Draft ATAG 2.0 authoring-tool evidence. Not an ATAG conformance report.">',
        '<meta name="robots" content="noindex">',
        "<title>Drupal Core authoring tool — ATAG 2.0 evidence (draft)</title>",
        '<link rel="stylesheet" href="./report.css">',
        "</head>",
        "<body>",
        '<a class="skip" href="#main">Skip to main content</a>',
        '<header class="page-header">',
        '<p class="eyebrow">OpenACR Release Evidence · ATAG 2.0</p>',
        "<h1>Drupal Core authoring tool — ATAG 2.0 evidence</h1>",
        '<p class="status-banner"><strong>Draft authoring evidence, not an ATAG conformance report.</strong> '
        "The issue tag identifies reported authoring-tool problems. It does not prove conformance, and no ATAG "
        "success-criterion result is assigned here.</p>",
        '<p class="meta">ATAG 2.0 · 63 success criteria · WAI ATAG Report Tool draft · '
        f'{_esc(summary["issues"])} ATAG-tagged issues</p>',
        "</header>",
        '<main id="main" tabindex="-1">',
        '<section aria-labelledby="scope-heading"><h2 id="scope-heading">Scope and method</h2>',
        '<p>ATAG applies to the authoring tool interfaces used to create and edit content. This is a product-level '
        'queue inventory, not a release applicability result; issue versions and components are visible but must be '
        'verified on the target. The report is separate from the WCAG release matrix: WCAG evidence must not be '
        'inherited by ATAG, and ATAG evidence must not be treated as a WCAG result.</p>',
        _facts(rows),
        f'<p class="meta">Source queue: {_link(QUEUE_URL, "Accessibility-tagged issues")} · '
        f'{_link(ATAG_QUEUE_URL, "atag-tagged issues")} · '
        f'{_link(SPEC_URL, "ATAG 2.0 specification")}</p>',
        "</section>",
        '<section aria-labelledby="parts-heading"><h2 id="parts-heading">Part A and Part B evidence</h2>',
        "<p><strong>Part A</strong> covers accessibility of the authoring tool user interface. "
        "<strong>Part B</strong> covers support for producing accessible content. Explicit "
        "<code>atag-a</code>/<code>atag-b</code> tags or a reviewed <code>config/atag-scope.json</code> mapping are "
        "authoritative. A generic <code>atag</code> tag is not assigned to a Part; component names are not used "
        "to guess one.</p>",
        '<h3>Part A — explicit</h3>',
        _issue_list(explicit_a),
        '<h3>Part B — explicit</h3>',
        _issue_list(explicit_b),
        '<h3>ATAG-tagged, part not specified</h3>',
        _issue_list(unspecified),
        '<h3>ATAG meta/tracker issues</h3>',
        _issue_list(meta_issues),
        "</section>",
        '<section aria-labelledby="quality-heading"><h2 id="quality-heading">Data quality</h2>',
        _missing_message(summary["missing_accessibility_tag"]),
        _issue_list(missing_accessibility),
        "</section>",
        '<section aria-labelledby="tool-heading"><h2 id="tool-heading">WAI ATAG Report Tool draft</h2>',
        '<p>Download <a href="./atag-report.json">atag-report.json</a> and import it into the '
        f'{_link(TOOL_URL, "WAI ATAG Report Tool")}. Every one of the 63 criteria is <strong>Not checked</strong>; '
        "the evaluator name and organization are placeholders. A human reviewer must complete the evaluation, "
        "record observations and export the final ATAG report.</p>",
        '<p class="meta">Machine-readable evidence: <a href="./atag-evidence.json">atag-evidence.json</a>. '
        f'Report Tool source: {_link("https://github.com/w3c/wai-atag-report-tool", "w3c/wai-atag-report-tool")}. '
        "No ATAG conformance values are populated.</p>",
        "</section>",
        '<section aria-labelledby="limits-heading"><h2 id="limits-heading">Limitations</h2><ul>',
        "<li>The queue currently uses a generic <code>atag</code> tag. Part A/B tags were not present in the "
        "snapshot, so most issues are unassigned and need human triage.</li>",
        "<li>No Part A/B assignment is inferred from a component name or issue title.</li>",
        "<li>No ATAG evaluation was performed against the authoring tool; no assistive-technology testing is claimed.</li>",
        "<li>ATAG Part A/B applies to the authoring tool UI; release-specific behaviour may differ and must be "
        "reproduced on the installed version.</li>",
        "<li>ATAG and WCAG are separate standards. This report does not modify the OpenACR WCAG draft or inherit "
        "WCAG results.</li>",
        "</ul></section>",
        "</main>",
        '<footer><p>Draft ATAG 2.0 evidence. Not a conformance report. '
        f'{_link(SPEC_URL, "ATAG 2.0")} · {_link(TOOL_URL, "ATAG Report Tool")} · '
        '<a href="../">All reports</a>.</p>'
        '<p class="meta">Issue titles are quoted from public Drupal.org issues with source links and attribution.</p></footer>',
        "</body></html>",
    ]
    (output / "index.html").write_text("\n".join(html_parts) + "\n", encoding="utf-8")
    return {
        "index": output / "index.html",
        "report": output / "atag-report.json",
        "evidence": output / "atag-evidence.json",
        "summary": summary,
    }
