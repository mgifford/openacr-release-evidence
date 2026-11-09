"""Render a deterministic, ACR narrative draft from active evidence.

This is a human-readable narrative companion to the OpenACR YAML. It never
assigns an ACR result: every criterion is "Not Evaluated" until a reviewer
completes the evaluation. Issue-queue evidence is described, not converted into
Supports/Partially Supports/Does Not Support.
"""
import json
from html import escape
from pathlib import Path

from .criterion_summaries import PROMPT_VERSION as CRITERION_PROMPT_VERSION
from .openacr_export import load_catalog

DRAFT_TERM = "Not Evaluated (draft — reviewer must select an ACR result)"
COMPONENTS = (
    ("Web", "Partially Supports", "web"),
    ("Electronic Documents", "Not Applicable", "electronic-docs"),
    ("Software", "Not Applicable", "software"),
    ("Authoring Tool", "Partially Supports", "authoring-tool"),
)
CORE_SCOPE = {
    "1.2.1": (
        "Drupal Core does not provide audio/video playback out of the box. Consider Able Player for "
        "pre-recorded audio/video."
    ),
    "1.2.3": (
        "Drupal Core does not provide audio description or media alternatives out of the box. Consider "
        "Able Player for pre-recorded media."
    ),
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


def _load_release_changes():
    try:
        data = json.loads((Path(__file__).resolve().parents[2] / "config" / "release-changes.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data.get("release_lines") or {}


def _load_criterion_summaries(output_dir):
    """Load the shared cache without relying only on the output directory.

    ``multi`` writes reports under reports/<target>, so the cache is in the
    parent. Standalone ``report`` rebuilds may write to /tmp while the committed
    cache remains at reports/acr-summaries.json; search the working tree too.
    """
    candidates = [
        Path(output_dir).parent / "acr-summaries.json",
        Path.cwd() / "reports" / "acr-summaries.json",
        Path("reports") / "acr-summaries.json",
    ]
    data = {}
    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            break
        except (OSError, ValueError):
            continue
    if data.get("prompt_version") != CRITERION_PROMPT_VERSION:
        return {}
    criteria = data.get("criteria") or {}
    return {
        criterion: item
        for criterion, item in criteria.items()
        if item.get("status") == "accepted"
    }


def _slug(value):
    text = "".join(ch if ch.isalnum() else "-" for ch in str(value).lower()).strip("-")
    return text or "section"


class Cell:
    def __init__(self, text, url=None):
        self.text = "" if text is None else str(text)
        self.url = url if isinstance(url, str) and url.startswith("https://") else None


class RichCell:
    """A table cell containing text, links and emphasis."""

    def __init__(self, *parts):
        self.parts = parts


class Bold:
    def __init__(self, text):
        self.text = "" if text is None else str(text)


class Gap:
    """A larger visual separation between sections in a table cell."""
    pass


class BulletList:
    def __init__(self, items):
        self.items = list(items)


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

    def heading(self, text, anchor):
        self.blocks.append(("heading", (text, anchor)))

    def links(self, items):
        self.blocks.append(("links", list(items)))

    def table(self, caption, headers, rows, css_class=None):
        self.blocks.append(("table", (caption, list(headers), [list(row) for row in rows], css_class)))

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
            elif kind == "heading":
                text, _anchor = value
                out.extend([f"### {text}", ""])
            elif kind == "links":
                out.extend([f"- [{label}]({url})" if url else f"- {label}" for label, url in value] + [""])
            elif kind == "table":
                caption, headers, rows, _css_class = value
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
            elif kind == "heading":
                text, anchor = value
                parts.append(f'<h3 id="{escape(anchor)}">{escape(text)}</h3>')
            elif kind == "links":
                items = []
                for label, url in value:
                    if url:
                        items.append(f'<li><a href="{escape(url)}">{escape(label)}</a></li>')
                    else:
                        items.append(f"<li>{escape(label)}</li>")
                parts.append("<ul>" + "".join(items) + "</ul>")
            elif kind == "table":
                caption, headers, rows, css_class = value
                parts.append(f'<div class="table-scroll" tabindex="0" role="region" aria-label="{escape(caption)}">')
                parts.append(f'<table class="{escape(css_class)}">' if css_class else "<table>")
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
        text = value.text.replace("|", "\\|").replace("\n", "; ")
        return f"[{text}]({value.url})" if value.url else text
    if isinstance(value, RichCell):
        rendered = []
        for part in value.parts:
            if isinstance(part, tuple) and len(part) == 2:
                label, url = part
                rendered.append(f"[{str(label).replace('|', '\\|')}]({url})")
            elif isinstance(part, Bold):
                rendered.append(f"**{part.text.replace('|', '\\|')}**")
            elif isinstance(part, Gap):
                rendered.append("<br><br>")
            elif isinstance(part, BulletList):
                bullets = []
                for item in part.items:
                    if isinstance(item, tuple) and len(item) == 2:
                        label, url = item
                        bullets.append(f"• [{str(label).replace('|', '\\|')}]({url})")
                    else:
                        bullets.append(f"• {str(item).replace('|', '\\|')}")
                rendered.append("<br>".join(bullets))
            else:
                rendered.append(str(part).replace("|", "\\|"))
        return " ".join(rendered).replace("\n", " ")
    return str(value).replace("|", "\\|").replace("\n", " ")


def _html_cell(value):
    if isinstance(value, Cell):
        if value.url:
            return f'<a href="{escape(value.url)}">{escape(value.text)}</a>'
        return escape(value.text)
    if isinstance(value, RichCell):
        rendered = []
        for part in value.parts:
            if isinstance(part, tuple) and len(part) == 2:
                label, url = part
                rendered.append(f'<a href="{escape(url)}">{escape(str(label))}</a>')
            elif isinstance(part, Bold):
                rendered.append(f"<strong>{escape(part.text)}</strong>")
            elif isinstance(part, Gap):
                rendered.append("<br><br>")
            elif isinstance(part, BulletList):
                rendered.append('<ul class="cell-list">')
                for item in part.items:
                    if isinstance(item, tuple) and len(item) == 2:
                        label, url = item
                        rendered.append(f'<li><a href="{escape(url)}">{escape(str(label))}</a></li>')
                    else:
                        rendered.append(f"<li>{escape(str(item))}</li>")
                rendered.append("</ul>")
            else:
                rendered.append(escape(str(part)))
        return "".join(rendered)
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
            "No active tagged issue in this snapshot. Absence of a tagged issue is not evidence that the "
            "criterion is met; the criterion remains Not Evaluated."
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
        f"Examples: {_examples(issues)}. The open issue queue is treated as reported barrier evidence; "
        "no issue was reproduced against this release."
    )
    if criterion in CORE_SCOPE:
        text += " Core scope: " + CORE_SCOPE[criterion]
    if inventory:
        text += " Inventory records have no comments, merge requests or commit analysis."
    return text


def _criterion_levels(criterion, issues):
    if criterion in CORE_SCOPE:
        return {
            "Web": "Not Applicable",
            "Electronic Documents": "Not Applicable",
            "Software": "Not Applicable",
            "Authoring Tool": "Not Applicable",
        }
    web = bool(_surface_items(issues, "web"))
    authoring = bool(_surface_items(issues, "authoring"))
    return {
        "Web": "Partially Supports" if web else "Not Evaluated",
        "Electronic Documents": "Not Applicable",
        "Software": "Not Applicable",
        "Authoring Tool": "Partially Supports" if authoring else "Not Evaluated",
    }


def _levels_text(criterion, issues):
    levels = _criterion_levels(criterion, issues)
    return "\n".join(f"{name}: {level}" for name, level in levels.items())


def _levels_cell(criterion, issues):
    levels = _criterion_levels(criterion, issues)
    parts = []
    for index, (name, level) in enumerate(levels.items()):
        if index:
            parts.append(Gap())
        parts.extend([Bold(name + ":"), " ", "N/A" if level == "Not Applicable" else level])
    return RichCell(*parts)


def _surface_items(items, surface):
    return [item for item in items if (item.get("surface") or {}).get("surface", "web") == surface]


def _barrier_summary(items, surface):
    label = "web" if surface == "web" else "authoring"
    if not items:
        return (
            f"No {label}-classified issue is tagged in this snapshot; the "
            f"{'Web' if surface == 'web' else 'Authoring Tool'} component remains Not Evaluated."
        )
    titles = []
    for item in items[:6]:
        title = (item.get("title") or "Untitled issue").strip()
        if len(title) > 110:
            title = title[:107].rstrip() + "…"
        titles.append(title)
    return (
        f"Reported {label} barriers include: " + "; ".join(titles) +
        f". These are {len(items)} active issue-queue reports; they describe known patterns rather than a complete census."
    )


def _evidence_text(items):
    detailed = sum(1 for item in items if item.get("evidence_status") != "inventory")
    inventory = len(items) - detailed
    states = {}
    for item in items:
        key = item.get("applicability") or "unknown"
        states[key] = states.get(key, 0) + 1
    state_text = ", ".join(f"{key}: {value}" for key, value in sorted(states.items()))
    return (
        f"{len(items)} active {_plural(len(items), 'issue')} tagged to this criterion: "
        f"{detailed} detailed, {inventory} metadata-only inventory. "
        f"Tracker statuses: {_status_summary(items)}. Target evidence states: {state_text}."
    )


def _example_items(items, limit=3):
    examples = []
    for item in items[:limit]:
        title = (item.get("title") or item.get("issue_id") or "Untitled issue").strip()
        if len(title) > 80:
            title = title[:77].rstrip() + "…"
        url = item.get("source_url")
        label = f"{title} ({item.get('issue_id')}, {item.get('tracker_status_label') or 'unknown status'})"
        examples.append((label, url) if url else label)
    return examples


def _reference_items(items):
    refs = []
    for item in items:
        title = (item.get("title") or item.get("issue_id") or "Untitled issue").strip()
        label = f"{item.get('issue_id')} — {title} ({item.get('tracker_status_label') or 'unknown status'})"
        refs.append((label, item.get("source_url")))
    return refs


def _remarks_cell(criterion, issues, ai_summary=None):
    if criterion in CORE_SCOPE:
        if criterion == "1.2.1":
            return RichCell(
                Bold("Web:"), " Drupal Core doesn't support audio/video out of the box. Consider ",
                ("Able Player", "https://www.drupal.org/project/ableplayer"),
                " for pre-recorded audio/video support.",
                Gap(),
                Bold("Authoring Tool:"), " Drupal Core doesn't support audio/video authoring out of the box.",
            )
        if criterion == "1.2.3":
            return RichCell(
                Bold("Web:"), " Drupal Core doesn't support audio description or media alternatives out of the box. Consider ",
                ("Able Player", "https://www.drupal.org/project/ableplayer"),
                " for pre-recorded media.",
                Gap(),
                Bold("Authoring Tool:"), " Drupal Core doesn't support audio description authoring out of the box.",
            )
        return RichCell(
            Bold("Web:"), " " + CORE_SCOPE[criterion],
            Gap(),
            Bold("Authoring Tool:"), " Drupal Core does not provide this audio/video feature in its authoring interface.",
        )
    web = _surface_items(issues, "web")
    authoring = _surface_items(issues, "authoring")
    ai_summary = ai_summary or {}
    if not issues:
        return RichCell(
            Bold("Web:"), " No active tagged issue; remains Not Evaluated.",
            Gap(),
            Bold("Authoring Tool:"), " No active tagged issue; remains Not Evaluated.",
        )
    parts = [
        Bold("Web:"), " ", ai_summary.get("web") or _barrier_summary(web, "web"),
        Gap(),
        Bold("Authoring Tool:"), " ", ai_summary.get("authoring") or _barrier_summary(authoring, "authoring"),
        Gap(),
        Bold("Evidence:"), " ", _evidence_text(issues),
        Gap(),
    ]
    examples = _example_items(issues)
    if examples:
        label = "Example:" if len(examples) == 1 else "Examples:"
        parts.extend([Bold(label), BulletList(examples)])
    if len(issues) > len(examples):
        parts.extend([
            Gap(),
            Bold("All issue references:"), " ",
            (f"{criterion} reference list", f"#ref-{_slug(criterion)}"),
        ])
    return RichCell(*parts)


def _table_number(level):
    return {"A": 1, "AA": 2, "AAA": 3}.get(level, "")


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
    ai_summaries = _load_criterion_summaries(output)
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
    doc = Doc(
        title,
        "Issue-tagged criteria use a draft Partially Supports result based on the open Drupal issue queue; "
        "criteria without a tagged issue remain Not Evaluated.",
    )

    doc.p("This document converts the active issue evidence into an ACR narrative. It is deliberately not a completed ACR: criteria with active tagged issues use a draft Partially Supports result from the open issue queue, while criteria without a tagged issue remain Not Evaluated. No issue was reproduced against this release, and a named reviewer must approve the report.")
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
    doc.p("These are proposed component-level labels for review, not final ACR terms. Criteria with active tagged issues carry a draft Partially Supports result; criteria without a tagged issue remain Not Evaluated.")
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
    doc.p("Reading the tables: Open issue reports are treated as reported barrier evidence; no issue was reproduced against this release. Inventory records have no comments, merge requests or commit analysis. Issue-tagged criteria use draft Partially Supports for Web and Authoring Tool; criteria without a tagged issue remain Not Evaluated. Electronic Documents and Software are Not Applicable because Drupal Core does not ship a standalone electronic-document or packaged software product in this scope.")
    doc.p("Surface counts are draft classification evidence. Inventory-only records have no collected descriptions/comments and default to Web; add explicit issue-queue guidance or tags to improve the authoring/web split. A Web result can include barriers that also affect the authoring interface; the per-component remarks identify the classified evidence.")
    if ai_summaries:
        doc.p("Some Web/Authoring paragraphs are model-assisted draft summaries generated from the cited issue evidence. They are suggestions for human review, not conformance conclusions; the issue list, statistics and references remain the source record.")
    else:
        doc.p("No accepted AI summary cache is present for this build. The Web/Authoring paragraphs are deterministic extracts from issue titles; add the optional criterion-summary step to enable model-assisted draft summaries.")
    doc.h2("Draft status and ACR result terms")
    doc.p("ACR result terms are defined here so the draft uses the same vocabulary as a completed ACR. Issue-tagged criteria use draft Partially Supports; criteria without a tagged issue remain Not Evaluated. A reviewer must confirm every term after evaluating the product.")
    doc.table("ACR result terms used in review", ["Term", "Meaning"], [
        ["Supports", "The product has at least one method of meeting the criterion, and the reviewer has evidence that it works for the evaluated scope."],
        ["Partially Supports", "Some product functionality meets the criterion; other functionality does not, and the reviewer can explain the boundary."],
        ["Does Not Support", "The majority of product functionality does not meet the criterion."],
        ["Not Applicable", "The criterion is not relevant to the product, and the reviewer records why."],
        ["Not Evaluated", "No active tagged issue and no other evidence supports a per-criterion term. Absence of a tagged issue is not evidence of support."],
    ])
    doc.h2("Scope and evaluation method")
    doc.p(f"The evidence collection covers active, review-relevant Drupal Core Accessibility issues: Active, Needs review, Needs work, RTBC and Patch. Fixed, closed and postponed issues are excluded. The snapshot contains {len(findings)} active {_plural(len(findings), 'finding')}, of which {tagged} {_plural(tagged, 'carries', 'carry')} at least one explicit WCAG issue tag.")
    doc.p(f"{detailed} {_plural(detailed, 'finding')} {_plural(detailed, 'has', 'have')} full comments and merge-request evidence; {inventory} are metadata-only inventory records. The inventory records identify active issues but do not include comments, merge requests or commit analysis. All findings are unreviewed.")
    doc.ul([
        "Discovery pages the complete Accessibility queue; it does not stop at the first API page.",
        "WCAG tags are candidate relevance signals from the issue queue, not conformance determinations.",
        "No issue was reproduced against an installed Drupal target in this pass.",
        "Open issue reports are treated as draft barrier evidence; they are not a release reproduction.",
        "No keyboard, screen-reader, zoom, reduced-motion or forced-colors testing of the product is claimed.",
        "No AI was used to assign applicability or an ACR result.",
    ])
    release_line = str(target.get("release_line") or "")
    theme_info = _load_release_changes().get(release_line) or {}
    if theme_info:
        front = ", ".join(theme_info.get("front_end_themes") or []) or "none recorded"
        admin = ", ".join(theme_info.get("admin_themes") or []) or "none recorded"
        removed = ", ".join(theme_info.get("removed") or [])
        note = f"Theme availability for {release_line}: front-end themes {front}; admin themes {admin}."
        if removed:
            note += f" Removed in this line: {removed}."
        note += (" The core collection does not include the theme project queues; a theme's own ACR must cover those issues.")
        doc.p(note)
    doc.h2("Why this ACR is different")
    doc.p("A VPAT is a template; a completed report is an ACR. Most vendor ACRs are periodic, sample-based snapshots reviewed by legal or product management, with the vendor's issue queue kept separate. This report is an issue-queue attestation: it is generated from the full active Drupal Core Accessibility queue and keeps every cited issue linked.")
    doc.table("Conventional vendor ACR and this issue-queue attestation", ["Dimension", "Conventional vendor ACR", "This ACR"], [
        ["Cadence", "Annual, biennial or procurement-driven", "Every weekly tracker snapshot"],
        ["Evidence", "Selected pages, flows or a WCAG-EM sample", "Full active Accessibility queue; comments/MRs where collected"],
        ["Traceability", "Summary claims, often without issue links", "Every cited issue links to the public Drupal.org source"],
        ["Authoring", "Often folded into web or omitted", "Explicit Authoring Tool component and separate remarks"],
        ["Change", "Static until the next report", "Incremental; new issues and status changes appear next snapshot"],
        ["Independence", "Often a commissioned assessment", "Community-reported issue evidence; no independent WCAG-EM audit"],
    ])
    doc.p("It is stronger on completeness of known reports, traceability, recency and connection to the remediation backlog. It is weaker on independent page sampling and manual assistive-technology coverage. It is not a WCAG-EM evaluation, a certification or a substitute for a procurement-specific ACR. A missing tagged issue is not evidence of support.")
    doc.p("Read the queue as reported barrier evidence. The criterion result is a draft issue-queue attestation subject to human confirmation. See the GSA OpenACR discussion and Drupal's ACR process for the wider model.")
    doc.links([
        ("GSA OpenACR issue #180", "https://github.com/GSA/openacr/issues/180"),
        ("Drupal ACR process", "https://www.drupal.org/docs/getting-started/accessibility/accessibility-conformance-report-acr-process"),
        ("WCAG-EM 2.0", "https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/"),
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

    for chapter, level in ((chapter_a, "A"), (chapter_aa, "AA"), (chapter_aaa, "AAA")):
        if not chapter:
            continue
        doc.h2(f"WCAG 2.2 Level {level} criteria")
        rows = []
        for criterion in chapter.get("criteria") or []:
            criterion_id = str(criterion.get("id"))
            items = by_criterion.get(criterion_id, [])
            alt_id = criterion.get("alt_id") or ""
            criterion_url = f"https://www.w3.org/TR/WCAG22/#{alt_id}" if alt_id else "https://www.w3.org/TR/WCAG22/"
            rows.append([
                Cell(f"{criterion_id} {criterion.get('handle') or ''}", criterion_url),
                _levels_cell(criterion_id, items),
                _remarks_cell(criterion_id, items, ai_summaries.get(criterion_id)),
            ])
        doc.table(
            f"Table {_table_number(level)}: Success Criteria, Level {level}",
            ["Criteria", "Conformance Level", "Remarks and Explanations"],
            rows,
            css_class="acr-table",
        )

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
        "Verify each criterion against the installed product; do not treat an issue count as a severity or percentage.",
        "Complete the reviewer name, organization and approval record outside this generated draft.",
        "Replace every Not Evaluated result with a reviewed ACR result, or record the remaining evaluation gap.",
        "Confirm the proposed Partially Supports results for issue-tagged criteria or record why the queue evidence is insufficient.",
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
    doc.h2("References")
    doc.p("Every Drupal.org issue cited in the criterion tables is listed below by criterion. Each link goes to the public issue where the barrier is discussed.")
    for criterion_id in sorted(by_criterion):
        items = by_criterion[criterion_id]
        handle = next(
            (
                criterion.get("handle")
                for chapter in catalog.get("chapters") or []
                for criterion in chapter.get("criteria") or []
                if str(criterion.get("id")) == criterion_id
            ),
            "",
        )
        doc.heading(f"{criterion_id} — {handle or 'WCAG criterion'}", f"ref-{_slug(criterion_id)}")
        doc.links(_reference_items(items))
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
