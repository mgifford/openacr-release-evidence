"""Render a deterministic, ACR narrative draft from active evidence.

This is a human-readable narrative companion to the OpenACR YAML. It never
assigns an ACR result: every criterion is "Not Evaluated" until a reviewer
completes the evaluation. Issue-queue evidence is described, not converted into
Supports/Partially Supports/Does Not Support.
"""
from html import escape
from pathlib import Path

from .openacr_export import load_catalog

DRAFT_TERM = "Not Evaluated (draft — reviewer must select an ACR result)"
COMPONENTS = (
    ("Web", "Partially Supports", "web"),
    ("Electronic Documents", "Not Applicable", "electronic-docs"),
    ("Software", "Not Applicable", "software"),
    ("Authoring Tool", "Partially Supports", "authoring-tool"),
)
CORE_SCOPE = {
    "1.2.4": (
        "Drupal Core does not provide live audio/video. Proposed Not Applicable for Core; "
        "evaluate the contrib Video or AblePlayer modules separately."
    ),
    "1.2.5": (
        "Drupal Core does not provide a video player or audio-description feature. Proposed Not Applicable "
        "for Core; audio/video caption and description support belongs to contrib Video or AblePlayer."
    ),
}
STATUS_ORDER = ("Active", "Needs review", "Needs work", "Reviewed & tested by the community", "Patch")


def _slug(value):
    text = "".join(ch if ch.isalnum() else "-" for ch in str(value).lower()).strip("-")
    return text or "section"


class Cell:
    def __init__(self, text, url=None):
        self.text = "" if text is None else str(text)
        self.url = url if isinstance(url, str) and url.startswith("https://") else None


class Doc:
    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.blocks = []

    def h1(self, text):
        self.blocks.append(("h1", text))

    def h2(self, text):
        self.blocks.append(("h2", text))

    def h3(self, text):
        self.blocks.append(("h3", text))

    def p(self, text):
        self.blocks.append(("p", text))

    def ul(self, items):
        self.blocks.append(("ul", list(items)))

    def table(self, caption, headers, rows):
        self.blocks.append(("table", (caption, list(headers), [list(row) for row in rows])))

    def markdown(self):
        out = [f"# {self.title}", "", f"_{self.description}_", ""]
        for kind, value in self.blocks:
            if kind == "h1":
                out.extend([f"# {value}", ""])
            elif kind == "h2":
                out.extend([f"## {value}", ""])
            elif kind == "h3":
                out.extend([f"### {value}", ""])
            elif kind == "p":
                out.extend([value, ""])
            elif kind == "ul":
                out.extend([f"- {item}" for item in value] + [""])
            elif kind == "table":
                caption, headers, rows = value
                out.extend([f"**{caption}**", ""])
                out.append("| " + " | ".join(_md(head) for head in headers) + " |")
                out.append("|" + "|".join(" --- " for _ in headers) + "|")
                for row in rows:
                    out.append("| " + " | ".join(_md(cell) for cell in row) + " |")
                out.append("")
        return "\n".join(out).rstrip() + "\n"

    def html(self):
        headings = [value for kind, value in self.blocks if kind == "h2"]
        used = {}
        heading_ids = []
        for heading in headings:
            base = _slug(heading)
            count = used.get(base, 0)
            used[base] = count + 1
            heading_ids.append(base if count == 0 else f"{base}-{count + 1}")
        parts = [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<meta name="description" content="Draft ACR narrative. Not an approved Accessibility Conformance Report.">',
            '<meta name="robots" content="noindex">',
            f"<title>{escape(self.title)}</title>",
            '<link rel="stylesheet" href="./report.css">',
            "</head>",
            "<body>",
            '<a class="skip" href="#main">Skip to main content</a>',
            '<header class="page-header">',
            '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'
            '<li><a href="../">All release reports</a></li>'
            '<li><a href="./index.html">Release evidence report</a></li>'
            '<li><span aria-current="page">ACR draft</span></li></ol></nav>',
            '<p class="eyebrow">OpenACR Release Evidence · ACR draft</p>',
            f"<h1>{escape(self.title)}</h1>",
            f'<p class="status-banner"><strong>Draft for human review, not an approved ACR.</strong> {escape(self.description)}</p>',
            "</header>",
            '<nav class="section-nav" aria-label="ACR sections"><h2>On this page</h2><ol>',
        ]
        for heading, heading_id in zip(headings, heading_ids):
            parts.append(f'<li><a href="#{heading_id}">{escape(heading)}</a></li>')
        parts.extend([
            "</ol></nav>",
            '<main id="main" tabindex="-1">',
        ])
        heading_index = 0
        for kind, value in self.blocks:
            if kind == "h1":
                parts.append(f"<h2>{escape(value)}</h2>")
            elif kind == "h2":
                heading_id = heading_ids[heading_index]
                heading_index += 1
                parts.append(f'<h2 id="{heading_id}">{escape(value)}</h2>')
            elif kind == "h3":
                parts.append(f"<h3>{escape(value)}</h3>")
            elif kind == "p":
                parts.append(f"<p>{escape(value)}</p>")
            elif kind == "ul":
                parts.append("<ul>" + "".join(f"<li>{escape(item)}</li>" for item in value) + "</ul>")
            elif kind == "table":
                caption, headers, rows = value
                parts.append(f'<div class="table-scroll" tabindex="0" role="region" aria-label="{escape(caption)}">')
                parts.append("<table>")
                parts.append(f"<caption>{escape(caption)}</caption>")
                parts.append("<thead><tr>" + "".join(f'<th scope="col">{escape(head)}</th>' for head in headers) + "</tr></thead><tbody>")
                for row in rows:
                    parts.append("<tr>" + "".join(f"<td>{_html_cell(cell)}</td>" for cell in row) + "</tr>")
                parts.append("</tbody></table>")
                parts.append("</div>")
        # Close any open section wrappers conservatively: use a flat main instead.
        parts.append("</main>")
        parts.append("<footer><p>Draft ACR narrative generated from active Drupal.org issue evidence. Not a conformance claim. "
                     '<a href="./index.html">Evidence report</a> · <a href="./openacr.yaml">OpenACR YAML</a>.</p></footer>')
        parts.append("</body></html>")
        return "\n".join(part for part in parts if part != "")


def _md(value):
    if isinstance(value, Cell):
        text = value.text.replace("|", "\\|").replace("\n", " ")
        return f"[{text}]({value.url})" if value.url else text
    return str(value).replace("|", "\\|").replace("\n", " ")


def _html_cell(value):
    if isinstance(value, Cell):
        if value.url:
            return f'<a href="{escape(value.url)}">{escape(value.text)}</a>'
        return escape(value.text)
    return escape(str(value))


def _plural(count, singular, plural=None):
    return singular if count == 1 else (plural or singular + "s")


def _examples(issues, limit=3):
    out = []
    for issue in issues[:limit]:
        title = (issue.get("title") or "Untitled issue").strip()
        if len(title) > 90:
            title = title[:87].rstrip() + "…"
        out.append(f"{title} ({issue.get('issue_id')}, {issue.get('tracker_status_label') or 'unknown status'})")
    return "; ".join(out)


def _status_summary(issues):
    counts = {}
    for issue in issues:
        label = issue.get("tracker_status_label") or "Unknown"
        counts[label] = counts.get(label, 0) + 1
    order = [label for label in STATUS_ORDER if label in counts]
    order.extend(sorted(label for label in counts if label not in order))
    return ", ".join(f"{label}: {counts[label]}" for label in order)


def _criterion_remark(criterion, issues):
    if not issues:
        text = (
            "No active issue in this snapshot carries this WCAG tag. Absence of a tagged issue is not evidence that "
            "the criterion is met; a reviewer must evaluate it and select an ACR result."
        )
        if criterion in CORE_SCOPE:
            text += " Core scope: " + CORE_SCOPE[criterion]
        return text
    detailed = sum(1 for issue in issues if issue.get("evidence_status") != "inventory")
    inventory = len(issues) - detailed
    states = {}
    for issue in issues:
        states[issue.get("applicability") or "unknown"] = states.get(issue.get("applicability") or "unknown", 0) + 1
    state_text = ", ".join(f"{key}: {value}" for key, value in sorted(states.items()))
    text = (
        f"{len(issues)} active {_plural(len(issues), 'issue')} tagged to this criterion: {detailed} detailed, "
        f"{inventory} metadata-only inventory. "
        f"Tracker statuses: {_status_summary(issues)}. Target evidence states: {state_text}. "
        f"Examples: {_examples(issues)}. This is issue-queue evidence, not a conformance result; verify the barrier "
        "and select the ACR result."
    )
    if criterion in CORE_SCOPE:
        text += " Core scope: " + CORE_SCOPE[criterion]
    if inventory:
        text += " Inventory records have no comments, merge requests or commit analysis."
    return text


def render_acr_narrative(analysis, output_dir):
    """Write acr.md and acr.html for one target."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    assessment = analysis.get("assessment") or {}
    target = analysis.get("target") or {}
    summary = analysis.get("summary") or {}
    findings = analysis.get("findings") or []
    issues = {issue.get("id"): issue for issue in (analysis.get("issues") or [])}
    catalog = load_catalog()
    by_criterion = {}
    for finding in findings:
        for criterion in finding.get("wcag_candidates") or []:
            by_criterion.setdefault(str(criterion), []).append(finding)
    chapter_a = next((c for c in catalog["chapters"] if c["id"] == "success_criteria_level_a"), None)
    chapter_aa = next((c for c in catalog["chapters"] if c["id"] == "success_criteria_level_aa"), None)
    chapter_aaa = next((c for c in catalog["chapters"] if c["id"] == "success_criteria_level_aaa"), None)
    non_wcag = [c for c in catalog["chapters"] if c["id"] in {
        "functional_performance_criteria", "hardware", "software", "support_documentation_and_services"
    }]
    report_date = str(analysis.get("generated_at") or "")[:10] or "Not recorded"
    product = assessment.get("product") or "Product"
    release = target.get("release") or assessment.get("release") or "unknown"
    tagged = sum(1 for finding in findings if finding.get("wcag_candidates"))
    detailed = sum(1 for issue in findings if issue.get("evidence_status") != "inventory")
    inventory = len(findings) - detailed
    status_counts = {}
    for finding in findings:
        label = finding.get("tracker_status_label") or "Unknown"
        status_counts[label] = status_counts.get(label, 0) + 1
    top = sorted(
        ((criterion, len(items)) for criterion, items in by_criterion.items()),
        key=lambda item: (-item[1], item[0]),
    )[:8]

    title = f"{product} {release} — Draft Accessibility Conformance Report (ACR) Narrative"
    doc = Doc(title, "Issue evidence is described for human review. No criterion is assigned Supports, Partially Supports or Does Not Support.")

    doc.p("This document converts the active issue evidence into an ACR narrative. It is deliberately not a completed ACR: every criterion is marked Not Evaluated until a named reviewer completes the evaluation and approves the report.")
    doc.h2("Product information")
    doc.table("Product and report identification", ["Field", "Value"], [
        ["Product", Cell(product)],
        ["Version / release", Cell(release)],
        ["Target ref", Cell(f"{target.get('ref') or assessment.get('ref')} ({target.get('ref_type') or 'tag'})")],
        ["Support status", Cell(str(target.get("support_status") or "Not recorded"))],
        ["Report date", Cell(report_date)],
        ["Report status", Cell("DRAFT — not approved for publication")],
        ["Prepared by", Cell("Unassigned reviewer (draft)")],
        ["Assessment identifier", Cell(assessment.get("id") or "Not recorded")],
        ["Standards baseline", Cell(", ".join(assessment.get("standards") or []) or "Not recorded")],
    ])
    surface_counts = {"web": 0, "authoring": 0}
    for finding in findings:
        surface = (finding.get("surface") or {}).get("surface", "web")
        if surface in surface_counts:
            surface_counts[surface] += 1
    doc.h2("Component scope and proposed result")
    doc.p("These are proposed component-level labels for review, not final ACR terms. Every per-criterion result below remains Not Evaluated until a reviewer completes it.")
    component_rows = []
    for component, proposed, component_id in COMPONENTS:
        if component_id == "web":
            evidence = f"{surface_counts['web']} active findings classified as front-end/web"
            rationale = (
                "Partially Supports is proposed because active front-end accessibility issues exist in the "
                "published evidence. This label needs a specific explanation and independent review."
            )
        elif component_id == "authoring-tool":
            evidence = f"{surface_counts['authoring']} active findings classified as authoring/admin UI"
            rationale = (
                "Partially Supports is proposed because active authoring-interface issues exist. "
                "The /admin, Drupal /user account paths and login/reproduction cues are the classification basis; a reviewer must confirm."
            )
        elif component_id == "electronic-docs":
            evidence = "No core electronic-document product"
            rationale = (
                "Not Applicable is proposed: Drupal Core is a web CMS, not a standalone electronic-document "
                "authoring or playback product. Uploaded documents are delivered as web content."
            )
        else:
            evidence = "No packaged/non-web software product"
            rationale = (
                "Not Applicable is proposed: Drupal Core is web software. The Section 508 software "
                "chapter is not a separate installed application in this scope."
            )
        component_rows.append([Cell(component), Cell(proposed + " (proposed)"), Cell(evidence), Cell(rationale)])
    doc.table(
        "Section 508 component scope",
        ["Component", "Proposed result", "Evidence", "Rationale"],
        component_rows,
    )
    doc.p("Supports, Partially Supports and Not Applicable are conformance labels. A proposed Partially Supports result requires an explanation; a proposed Supports result must also be explained. The ACR template records this structure for reuse.")
    doc.p("Surface counts are draft classification evidence. Inventory-only records have no collected descriptions/comments and default to Web; add explicit issue-queue guidance or tags to improve the authoring/web split.")
    doc.h2("Draft status and ACR result terms")
    doc.p("ACR result terms are defined here so the draft uses the same vocabulary as a completed ACR. This draft assigns no per-criterion term. A reviewer must select each term from the definitions below after evaluating the product.")
    doc.table("ACR result terms used in review", ["Term", "Meaning"], [
        ["Supports", "The product has at least one method of meeting the criterion, and the reviewer has evidence that it works for the evaluated scope."],
        ["Partially Supports", "Some product functionality meets the criterion; other functionality does not, and the reviewer can explain the boundary."],
        ["Does Not Support", "The majority of product functionality does not meet the criterion."],
        ["Not Applicable", "The criterion is not relevant to the product, and the reviewer records why."],
        ["Not Evaluated", "The reviewer has not completed enough evaluation to select a per-criterion term. Every criterion row uses this; the component proposals above are not per-criterion terms."],
    ])
    doc.h2("Scope and evaluation method")
    doc.p(f"The evidence collection covers active, review-relevant Drupal Core Accessibility issues: Active, Needs review, Needs work, RTBC and Patch. Fixed, closed and postponed issues are excluded. The snapshot contains {len(findings)} active {_plural(len(findings), 'finding')}, of which {tagged} {_plural(tagged, 'carries', 'carry')} at least one explicit WCAG issue tag.")
    doc.p(f"{detailed} {_plural(detailed, 'finding')} {_plural(detailed, 'has', 'have')} full comments and merge-request evidence; {inventory} are metadata-only inventory records. The inventory records identify active issues but do not include comments, merge requests or commit analysis. All findings are unreviewed.")
    doc.ul([
        "Discovery pages the complete Accessibility queue; it does not stop at the first API page.",
        "WCAG tags are candidate relevance signals from the issue queue, not conformance determinations.",
        "No issue was reproduced against an installed Drupal target in this pass.",
        "No keyboard, screen-reader, zoom, reduced-motion or forced-colors testing of the product is claimed.",
        "No AI was used to assign applicability or an ACR result.",
    ])
    doc.h2("Executive summary")
    doc.p(f"The active queue contains {len(findings)} {_plural(len(findings), 'issue')}. Tracker states are: {_status_summary(findings)}. {detailed} {_plural(detailed, 'issue')} {_plural(detailed, 'has', 'have')} detailed evidence and {inventory} are inventory-only. The queue is a triage input, not an accessibility score.")
    if top:
        doc.p("The largest explicitly tagged criterion clusters are listed below. A count reflects issue tagging, not severity or conformance.")
        doc.ul([f"WCAG {criterion}: {count} active {_plural(count, 'issue')}" for criterion, count in top])
    else:
        doc.p("No active finding carries an explicit WCAG criterion tag in this snapshot.")
    unmapped = len(findings) - tagged
    doc.p(f"{unmapped} active {_plural(unmapped, 'finding')} {_plural(unmapped, 'has', 'have')} no WCAG criterion tag. They remain in the evidence report and may still describe accessibility barriers; no criterion is inferred from their prose.")

    for chapter, level in ((chapter_a, "A"), (chapter_aa, "AA")):
        if not chapter:
            continue
        doc.h2(f"WCAG 2.2 Level {level} criteria")
        rows = []
        for criterion in chapter.get("criteria") or []:
            criterion_id = str(criterion.get("id"))
            items = by_criterion.get(criterion_id, [])
            if items:
                evidence = f"{len(items)} active ({sum(1 for i in items if i.get('evidence_status') != 'inventory')} detailed, {sum(1 for i in items if i.get('evidence_status') == 'inventory')} inventory)"
            else:
                evidence = "No active tagged issue"
            rows.append([
                Cell(f"{criterion_id} — {criterion.get('handle') or ''}"),
                Cell(level),
                Cell(evidence),
                Cell(DRAFT_TERM),
                Cell(_criterion_remark(criterion_id, items)),
            ])
        doc.table(f"WCAG 2.2 Level {level} remarks and explanations", ["Criterion", "Level", "Active issue evidence", "Draft result", "Remarks and explanations"], rows)

    if chapter_aaa:
        doc.h2("WCAG 2.2 Level AAA criteria")
        doc.p(f"{len(chapter_aaa.get('criteria') or [])} AAA criteria are outside the declared WCAG 2.2 AA target. They are not marked Supports or Not Applicable in this draft; a reviewer must decide whether to evaluate them or record a scope rationale.")

    doc.h2("Functional performance, hardware, software and support documentation")
    doc.p("These Section 508/ACR chapters are not evaluated by this web issue-evidence pipeline. They are shown so the draft has the complete ACR shape; a reviewer must evaluate them or mark Not Applicable with a rationale.")
    rows = []
    for chapter in non_wcag:
        rows.append([
            Cell(chapter.get("id") or ""),
            Cell(str(len(chapter.get("criteria") or []))),
            Cell("Not Evaluated"),
            Cell("Outside the web issue-evidence method's coverage. The pipeline collected issue/commit evidence only; no hardware, packaged software, functional-performance or support-documentation testing was performed."),
        ])
    doc.table("Non-WCAG ACR chapters", ["Chapter", "Criteria", "Draft result", "Remarks and explanations"], rows)

    doc.h2("ATAG 2.0 authoring evidence")
    doc.p("ATAG 2.0 is a separate standard from WCAG and is not part of this ACR narrative. Drupal Core's authoring-tool evidence is reported separately, with Part A/Part B candidates and a WAI ATAG Report Tool JSON draft containing no conformance values.")
    doc.p("See ../drupal-core-atag/ for the ATAG evidence report. It must not be copied into a WCAG criterion result.")

    doc.h2("Active issue evidence and review actions")
    doc.p("The evidence report lists all active issues and their source links. It distinguishes full-detail evidence from metadata-only inventory records. Use it to review the criterion remarks above, collect missing evidence and decide each ACR result.")
    doc.ul([
        "Use the generic templates/drupal-acr-template.md as the reusable ACR shell.",
        "Record scope and wording notes in context/DRUPAL.md (or the matching product context file); context is not evidence.",
        "Open ./index.html#issues and review the active issue evidence.",
        "For inventory records, read the source issue and collect the missing comments, merge requests and target evidence.",
        "Verify each criterion against the installed product; do not convert issue counts into Supports or Does Not Support.",
        "Complete the reviewer name, organization and approval record outside this generated draft.",
        "Replace every Not Evaluated result with a reviewed ACR result, or record the remaining evaluation gap.",
        "Remove the draft status only after independent review and sign-off.",
    ])

    doc.h2("Limitations")
    doc.ul([
        "This is an issue-queue evidence narrative, not a WCAG-EM sample or a conformance test.",
        "Fixed and closed issues are excluded by policy; their absence is not evidence that a barrier is gone.",
        f"The {inventory} {_plural(inventory, 'inventory record')} {'has' if inventory == 1 else 'have'} no comments/MRs/commit analysis; they are included for completeness, not as finished findings.",
        "No reproduction, assistive-technology testing, hardware testing or packaged-software testing is claimed.",
        "The product is a declared Drupal Core configuration; it is not every Drupal site.",
        "The draft does not establish legal compliance or a procurement-safe conformance claim.",
    ])
    doc.h2("Sources")
    doc.table("Authoritative sources", ["Source", "Link"], [
        ["Drupal Core Accessibility queue", Cell("Drupal.org Accessibility issue queue", "https://www.drupal.org/project/issues/search?text=&projects=Drupal+core&assigned=&submitted=&project_issue_followers=&status%5B%5D=Open&issue_tags_op=%3D&issue_tags=Accessibility")],
        ["WCAG 2.2", Cell("W3C WCAG 2.2 Recommendation", "https://www.w3.org/TR/WCAG22/")],
        ["OpenACR", Cell("GSA OpenACR", "https://github.com/GSA/openacr")],
        ["ATAG 2.0", Cell("W3C ATAG 2.0", "https://www.w3.org/TR/ATAG20/")],
        ["WAI ATAG Report Tool", Cell("WAI ATAG Report Tool", "https://www.w3.org/WAI/atag/report-tool/")],
    ])

    markdown = doc.markdown()
    html = doc.html()
    (output / "acr.md").write_text(markdown, encoding="utf-8")
    (output / "acr.html").write_text(html + "\n", encoding="utf-8")
    return {"markdown": output / "acr.md", "html": output / "acr.html"}
