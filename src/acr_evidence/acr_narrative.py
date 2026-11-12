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
from .criterion_evidence import automation_for_criterion
from .openacr_export import load_catalog
from .fpc import summarize as summarize_fpc
from .impact import get_criterion_impact, load_global_stats
from .non_wcag import load_considerations
from .surface_assessment import assessment_note, component_results, criterion_results

DRAFT_TERM = "Not Evaluated (draft — reviewer must select an ACR result)"
COMPONENTS = (
    ("Web", "Not Evaluated", "web"),
    ("Electronic Documents", "Not Applicable", "electronic-docs"),
    ("Software", "Not Applicable", "software"),
    ("Authoring Tool", "Not Evaluated", "authoring-tool"),
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
    "1.4.2": (
        "Drupal Core does not provide native audio playback or automatic audio to control; "
        "contrib media players are separate products."
    ),
}
STATUS_ORDER = ("Active", "Needs review", "Needs work", "Reviewed & tested by the community", "Patch")


def _load_release_changes():
    try:
        data = json.loads((Path(__file__).resolve().parents[2] / "config" / "release-changes.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data.get("release_lines") or {}


def _load_release_ledger(output_dir):
    candidates = [
        Path(output_dir) / "release-ledger.json",
        Path.cwd() / "reports" / "release-ledger.json",
    ]
    for path in candidates:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if value.get("artifact_type") == "drupal-release-transition-ledger":
            return value
    return {}


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


class Permalink:
    """A visible # link with a descriptive name for its heading or row."""

    def __init__(self, label, url):
        self.label = label
        self.url = url


class Break:
    pass


class Small:
    def __init__(self, text):
        self.text = "" if text is None else str(text)


def _heading_with_permalink(level, text, heading_id):
    label = "Permalink to " + str(text)
    return (
        f'<div class="heading-with-anchor"><h{level} id="{escape(heading_id)}">{escape(text)}</h{level}>'
        f'<a class="permalink" href="#{escape(heading_id)}">'
        f'<span aria-hidden="true">#</span>'
        f'<span class="visually-hidden">{escape(label)}</span></a></div>'
    )


class Doc:
    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.blocks = []

    def h1(self, text):
        self.blocks.append(("h1", text))

    def h2(self, text):
        self.blocks.append(("h2", text))

    def h2_anchor(self, text, anchor):
        self.blocks.append(("h2a", (text, anchor)))

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

    def table(self, caption, headers, rows, css_class=None, row_ids=None):
        self.blocks.append(("table", (caption, list(headers), [list(row) for row in rows], css_class, list(row_ids) if row_ids else None)))

    def details(self, summary, groups):
        self.blocks.append(("details", (summary, list(groups))))

    def markdown(self):
        out = [f"# {self.title}", "", f"_{self.description}_", ""]
        for kind, value in self.blocks:
            if kind == "h1":
                out.extend([f"# {value}", ""])
            elif kind == "h2":
                out.extend([f"## {value}", ""])
            elif kind == "h2a":
                out.extend([f"## {value[0]}", ""])
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
            elif kind == "details":
                summary, groups = value
                out.extend(["<details open>", f"<summary>{summary}</summary>", ""])
                for heading, links in groups:
                    out.extend([f"### {heading}", ""])
                    out.extend(f"- [{label}]({url})" if url else f"- {label}" for label, url in links)
                    out.append("")
                out.extend(["</details>", ""])
            elif kind == "table":
                caption, headers, rows, _css_class, _row_ids = value
                out.extend([f"**{caption}**", ""])
                out.append("| " + " | ".join(_md(head) for head in headers) + " |")
                out.append("|" + "|".join(" --- " for _ in headers) + "|")
                for row in rows:
                    out.append("| " + " | ".join(_md(cell) for cell in row) + " |")
                out.append("")
        return "\n".join(out).rstrip() + "\n"

    def html(self):
        used = {}
        heading_ids = {}
        for index, (kind, value) in enumerate(self.blocks):
            if kind in {"h2", "h3"}:
                base = _slug(value)
            elif kind == "h2a":
                base = value[1]
            elif kind == "heading":
                base = value[1]
            else:
                continue
            count = used.get(base, 0)
            used[base] = count + 1
            heading_ids[index] = base if count == 0 else f"{base}-{count + 1}"
        h2_indexes = [
            index for index, (kind, _value) in enumerate(self.blocks)
            if kind in {"h2", "h2a"}
        ]
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
        nav_groups = []
        current_group = None
        for index, (kind, value) in enumerate(self.blocks):
            if kind in {"h2", "h2a"}:
                current_group = [index, []]
                nav_groups.append(current_group)
            elif kind in {"h3", "heading"} and current_group is not None:
                current_group[1].append(index)
        for index, children in nav_groups:
            heading = self.blocks[index][1][0] if self.blocks[index][0] == "h2a" else self.blocks[index][1]
            parts.append(f'<li><a href="#{heading_ids[index]}">{escape(heading)}</a>')
            if children:
                parts.append('<ol>')
                for child in children:
                    child_text = self.blocks[child][1][0] if self.blocks[child][0] == "heading" else self.blocks[child][1]
                    parts.append(f'<li><a href="#{heading_ids[child]}">{escape(child_text)}</a></li>')
                parts.append('</ol>')
            parts.append('</li>')
        parts.extend([
            "</ol></nav>",
            '<main id="main" tabindex="-1">',
        ])
        for index, (kind, value) in enumerate(self.blocks):
            if kind == "h1":
                parts.append(f"<h2>{escape(value)}</h2>")
            elif kind == "h2":
                parts.append(_heading_with_permalink("2", value, heading_ids[index]))
            elif kind == "h2a":
                parts.append(_heading_with_permalink("2", value[0], heading_ids[index]))
            elif kind == "h3":
                parts.append(_heading_with_permalink("3", value, heading_ids[index]))
            elif kind == "p":
                parts.append(f"<p>{escape(value)}</p>")
            elif kind == "ul":
                parts.append("<ul>" + "".join(f"<li>{escape(item)}</li>" for item in value) + "</ul>")
            elif kind == "heading":
                text, _anchor = value
                parts.append(_heading_with_permalink("3", text, heading_ids[index]))
            elif kind == "links":
                items = []
                for label, url in value:
                    if url:
                        items.append(f'<li><a href="{escape(url)}">{escape(label)}</a></li>')
                    else:
                        items.append(f"<li>{escape(label)}</li>")
                parts.append("<ul>" + "".join(items) + "</ul>")
            elif kind == "details":
                summary, groups = value
                parts.append(f'<details class="reference-group" open><summary>{escape(summary)}</summary>')
                for heading, links in groups:
                    anchor = _slug(heading.split(" — ", 1)[0])
                    parts.append(_heading_with_permalink("3", heading, f"ref-{anchor}"))
                    parts.append("<ul>" + "".join(
                        f'<li><a href="{escape(url)}">{escape(label)}</a></li>' if url else f"<li>{escape(label)}</li>"
                        for label, url in links
                    ) + "</ul>")
                parts.append("</details>")
            elif kind == "table":
                caption, headers, rows, css_class, row_ids = value
                parts.append(f'<div class="table-scroll" tabindex="0" role="region" aria-label="{escape(caption)}">')
                parts.append(f'<table class="{escape(css_class)}">' if css_class else "<table>")
                parts.append(f"<caption>{escape(caption)}</caption>")
                parts.append("<thead><tr>" + "".join(f'<th scope="col">{escape(head)}</th>' for head in headers) + "</tr></thead><tbody>")
                for index, row in enumerate(rows):
                    row_id = f' id="{escape(row_ids[index])}"' if row_ids and index < len(row_ids) and row_ids[index] else ""
                    parts.append(f"<tr{row_id}>" + "".join(f"<td>{_html_cell(cell)}</td>" for cell in row) + "</tr>")
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
            elif isinstance(part, Permalink):
                rendered.append(f"[#]({part.url})")
            elif isinstance(part, Break):
                rendered.append("<br>")
            elif isinstance(part, Small):
                rendered.append(part.text.replace("|", "\\|"))
            elif isinstance(part, Cell):
                rendered.append(_md(part))
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
            elif isinstance(part, Permalink):
                rendered.append(
                    f'<a class="permalink" href="{escape(part.url)}">'
                    f'<span aria-hidden="true">#</span>'
                    f'<span class="visually-hidden">{escape(part.label)}</span></a>'
                )
            elif isinstance(part, Break):
                rendered.append("<br>")
            elif isinstance(part, Small):
                rendered.append(f'<span class="criterion-disability">{escape(part.text)}</span>')
            elif isinstance(part, Cell):
                rendered.append(_html_cell(part))
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
    results = criterion_results(criterion, issues)
    return {
        "Web": results["web"],
        "Electronic Documents": results["electronic-docs"],
        "Software": results["software"],
        "Authoring Tool": results["authoring-tool"],
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


def _automation_text(criterion):
    coverage = automation_for_criterion(criterion)
    if coverage["coverage"] == "none":
        return "Automated coverage: none mapped. This is not evidence that no barriers exist."
    return (
        f"Automated coverage: partial — {len(coverage['axe_rules'])} axe-core "
        f"{_plural(len(coverage['axe_rules']), 'rule')}, {len(coverage['act_rules'])} ACT "
        f"{_plural(len(coverage['act_rules']), 'rule')}. Coverage is available; no pass/fail "
        "is recorded here, and coverage is not a conformance result."
    )


def _barrier_summary(items, surface):
    label = "web" if surface == "web" else "authoring"
    if not items:
        return (
            f"No {label}-classified issue is known in this snapshot. Supports is based on the declared "
            "Drupal surface assessment, not on automated testing or the empty queue alone."
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
        if criterion == "1.4.2":
            return RichCell(
                Bold("Web:"), " Drupal Core has no native audio playback or automatic audio feature to control. ",
                ("Able Player", "https://www.drupal.org/project/ableplayer"),
                " and other contrib media players are separate products.",
                Gap(),
                Bold("Authoring Tool:"), " Drupal Core does not provide native audio playback or automatic audio authoring controls.",
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
    levels = _criterion_levels(criterion, issues)
    ai_summary = ai_summary or {}
    if not issues:
        levels = _criterion_levels(criterion, issues)
        return RichCell(
            Bold("Web:"), f" {levels['Web']}. {assessment_note(criterion, 'Web', levels['Web'])}",
            Gap(),
            Bold("Authoring Tool:"), f" {levels['Authoring Tool']}. {assessment_note(criterion, 'Authoring Tool', levels['Authoring Tool'])}",
            Gap(),
            _automation_text(criterion),
        )
    parts = [
        Bold("Evidence state:"), " Reported barrier, unverified. Candidate criterion mapping: issue tag, unreviewed. No conformance result assigned.",
        Gap(),
        _automation_text(criterion),
        Gap(),
        Bold("Web:"), f" {levels['Web']}. ", ai_summary.get("web") or _barrier_summary(web, "web"),
        Gap(),
        Bold("Authoring Tool:"), f" {levels['Authoring Tool']}. ", ai_summary.get("authoring") or _barrier_summary(authoring, "authoring"),
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


def _format_population(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f} billion"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.0f} million"
    return f"{value:,}"


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
        "Issue evidence is summarized under the declared surface assessment: "
        "known issues are Partially Supports and assessed surfaces with no known issue are Supports.",
    )

    doc.p("This document converts active issue evidence into an ACR narrative. It is deliberately not a completed ACR: results are draft applications of the declared surface assessment and the known-barrier register. No issue was reproduced against this release, and a named reviewer must approve the report.")
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
    doc.p("Web and Authoring Tool use the declared Drupal surface assessment plus the active known-barrier register. Known issues produce Partially Supports; an assessed surface with no active tagged issue produces Supports. No Does Not Support result is recorded.")
    component_rows = []
    component_policy = component_results(findings)
    for component, proposed, component_id in COMPONENTS:
        proposed = component_policy.get(component_id, proposed)
        if component_id == "web":
            evidence = f"{surface_counts['web']} active findings classified as front-end/web"
            rationale = (
                "Active front-end issue evidence exists, so Partially Supports is proposed. The issue queue is "
                "the known-barrier register; this is not a WCAG-EM audit."
            )
        elif component_id == "authoring-tool":
            evidence = f"{surface_counts['authoring']} active findings classified as authoring/admin UI"
            rationale = (
                "Active authoring-interface issue evidence exists, so Partially Supports is proposed. The "
                "/admin and /user-path classification remains draft and needs review."
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
        component_rows.append([Cell(component), Cell(proposed), Cell(evidence), Cell(rationale)])
    doc.table(
        "Section 508 component scope",
        ["Component", "Conformance result", "Evidence", "Rationale"],
        component_rows,
    )
    doc.p("Supports, Partially Supports, Does Not Support and Not Applicable are conformance labels. This draft applies them from the declared surface assessment and the active known-barrier register. It does not use a clean automated scan as a pass and does not record Does Not Support without explicit broad-failure evidence.")
    doc.p("Reading the tables: Open issue reports are treated as reported barrier evidence; no issue was reproduced against this release. Inventory records have no comments, merge requests or commit analysis. A surface with known issues is Partially Supports; an assessed surface with no active tagged issue is Supports.")
    doc.p("Surface counts are draft classification evidence. Inventory-only records have no collected descriptions/comments and default to Web; add explicit issue-queue guidance or tags to improve the authoring/web split. A Web result can include barriers that also affect the authoring interface; the per-component remarks identify the classified evidence.")
    if ai_summaries:
        doc.p("Some Web/Authoring paragraphs are model-assisted draft summaries generated from the cited issue evidence. They are suggestions for human review, not conformance conclusions; the issue list, statistics and references remain the source record.")
    else:
        doc.p("No accepted AI summary cache is present for this build. The Web/Authoring paragraphs are deterministic extracts from issue titles; add the optional criterion-summary step to enable model-assisted draft summaries.")
    doc.h2("Not Applicable claim review")
    doc.p("Electronic Documents and Software are Not Applicable for every criterion in this report. Drupal Core does not ship a standalone electronic-document product or packaged non-web software; uploaded documents are delivered as web content. Individual remarks therefore do not repeat this component-level exclusion.")
    doc.p("These N/A claims are product-scope decisions, not outcomes inferred from an empty issue queue. Procurement reviewers should test them against the declared product, not accept them as silent exclusions.")
    total_criteria = sum(len(chapter.get("criteria") or []) for chapter in catalog.get("chapters") or [])
    doc.table("N/A claims and rationale", ["Component", "Criteria", "Factual basis", "Review state"], [
        [Cell("Electronic Documents"), Cell(f"All {total_criteria}"), Cell("No standalone electronic-document product. Uploaded documents are delivered as web content."), Cell("Project-asserted; human confirmation required")],
        [Cell("Software"), Cell(f"All {total_criteria}"), Cell("No packaged non-web software product. Drupal Core is web software."), Cell("Project-asserted; human confirmation required")],
        [Cell("Web and Authoring Tool"), Cell("1.2.1, 1.2.3, 1.2.4, 1.2.5, 1.4.2"), Cell("No native audio/video playback, live audio/video, audio-description player, media-alternative feature or automatic audio control in Core. Contrib media players are separate products."), Cell("Project-asserted; human confirmation required")],
    ])
    doc.p("N/A is never used merely because no active issue is tagged. Any future N/A claim needs the same documented feature-absence basis and human review.")
    doc.h2("Draft status and ACR result terms")
    doc.p("ACR result terms are defined here so the draft uses the same vocabulary as a completed ACR. Results are proposed from the declared surface assessment and the known-barrier register; a reviewer must confirm every term and explanation.")
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
        "Automated coverage is partial: axe/ACT rule mappings show where some evaluation is possible, but no pass/fail result is recorded here. Guidepup can add behavioral screen-reader evidence when a run is recorded; no Guidepup run is claimed in this snapshot.",
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
    doc.h2("How the draft results are assigned")
    doc.p("The declared Drupal surface assessment is the baseline. Web and Authoring Tool are assessed surfaces. The active accessibility issue queue is the known-barrier register for those surfaces.")
    doc.p("A known active issue on a surface produces Partially Supports. An assessed surface with no active tagged issue produces Supports. Does Not Support is not recorded because there is no explicit broad-failure evidence. Not Applicable is used only for documented feature absence. Not Evaluated is reserved for an unassessed surface.")
    doc.p("This is an issue-queue attestation, not a WCAG-EM audit. Supports does not mean that axe-core or any other automated tool proved the criterion; automated coverage is partial and is reported separately.")
    doc.p("The media criteria 1.2.1, 1.2.3, 1.2.4, 1.2.5 and 1.4.2 are Not Applicable because Drupal Core does not provide the relevant audio/video player, live-media feature or automatic audio control. They are not Not Applicable because the queue is empty.")
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
    ledger = _load_release_ledger(output_dir)
    target_id = (analysis.get("target") or {}).get("assessment_id") or assessment.get("id")
    target_order = ledger.get("target_order") or []
    if ledger.get("issues") and target_id in target_order:
        current_index = target_order.index(target_id)
        transition_rows = []
        for issue in ledger["issues"]:
            states = issue.get("targets") or {}
            state = states.get(target_id)
            newer = [
                candidate for candidate in target_order[current_index + 1:]
                if states.get(candidate) == "included"
            ]
            if state not in {"not-included", "removed"} or (state == "not-included" and not newer):
                continue
            if state == "removed":
                state_label = "Component or theme removed from this release; out of scope"
                newer_label = "Not a fix for this target"
            else:
                state_label = "Fix commit not included in this target"
                newer_label = ", ".join(newer)
            commits = ", ".join(
                commit.get("sha", "")[:12] for commit in issue.get("commits") or []
                if any((commit.get("targets") or {}).get(candidate) for candidate in newer)
            ) or "No contained commit"
            transition_rows.append([
                Cell(issue.get("title") or issue.get("issue_id"), issue.get("source_url")),
                Cell(state_label),
                Cell(newer_label),
                Cell(commits),
            ])
        if transition_rows:
            doc.h2("Between-release fix notes (not active-issue results)")
            doc.p("These closed-fixed issues are separate from the active queue and do not change any criterion result. A newer target is listed only when a fix commit is contained there and is absent from this selected target. Absence is not proof that a backport will never happen.")
            doc.table(
                "Closed-fixed issues with newer-target commits",
                ["Issue", "State in selected target", "Newer target with the fix", "Commit"],
                transition_rows[:40],
            )
            if len(transition_rows) > 40:
                doc.p(f"Only the first 40 of {len(transition_rows)} transition records are shown; see the release ledger for the full set.")
            doc.p("A removed component or theme is a scope change, not a fix. Olivero-specific issues in a release that no longer ships Olivero are out of scope for that target and remain relevant to the release lines that still include it.")
            doc.p("This ledger is not a promise that a future backport will occur. It records commit containment in the named targets at this snapshot.")
            doc.links([
                ("Drupal release notes", "https://www.drupal.org/project/drupal/releases"),
                ("Drupal Core Accessibility queue", "https://www.drupal.org/project/issues/search?projects=Drupal+core&issue_tags=Accessibility"),
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
        row_ids = []
        for criterion in chapter.get("criteria") or []:
            criterion_id = str(criterion.get("id"))
            if criterion_id == "4.1.1":
                continue
            items = by_criterion.get(criterion_id, [])
            alt_id = criterion.get("alt_id") or ""
            criterion_url = f"https://www.w3.org/TR/WCAG22/#{alt_id}" if alt_id else "https://www.w3.org/TR/WCAG22/"
            row_id = f"criterion-{_slug(criterion_id)}"
            row_ids.append(row_id)
            impact = get_criterion_impact(criterion_id)
            rows.append([
                RichCell(
                    Cell(f"{criterion_id} {criterion.get('handle') or ''}", criterion_url),
                    " ",
                    Permalink(f"Permalink to criterion {criterion_id} {criterion.get('handle') or ''}", f"#{row_id}"),
                    *([Break(), Small("Introduced in WCAG " + impact["introduced_in"])] if impact and impact.get("introduced_in") in {"2.1", "2.2"} else []),
                    Break(),
                    Small("Affects: " + (impact or {}).get("affects_short", "")),
                    Break(),
                    Small("Barrier: " + (impact or {}).get("barrier_short", "")),
                    Break(),
                    (("Why this matters", "#human-impact")),
                    Break(),
                    Cell(
                        "W3C Understanding",
                        ((impact or {}).get("sources") or [{}])[0].get("url"),
                    ) if impact else Small("User-impact description pending review."),
                ),
                _levels_cell(criterion_id, items),
                _remarks_cell(criterion_id, items, ai_summaries.get(criterion_id)),
            ])
        doc.table(
            f"Table {_table_number(level)}: Success Criteria, Level {level}",
            ["Criteria", "Conformance Level", "Remarks and Explanations"],
            rows,
            css_class="acr-table",
            row_ids=row_ids,
        )

    results_by_criterion = {}
    for chapter in (chapter_a, chapter_aa, chapter_aaa):
        for criterion in (chapter or {}).get("criteria") or []:
            criterion_id = str(criterion.get("id"))
            results_by_criterion[criterion_id] = criterion_results(
                criterion_id, by_criterion.get(criterion_id, [])
            )
    fpc = summarize_fpc(results_by_criterion)
    doc.h2("Functional Performance Criteria (mapped)")
    doc.p("These are mapped summaries of the WCAG evidence by functional impact. They are not an independent functional-performance evaluation and are not OpenACR FPC values. The OpenACR FPC chapter remains Not Evaluated.")
    fpc_rows = []
    for row in fpc["rows"]:
        criteria = ", ".join(row["criteria"]) if len(row["criteria"]) <= 8 else ", ".join(row["criteria"][:8]) + "…"
        basis = f"Mapped from {len(row['criteria'])} WCAG criteria; see the mapping source."
        fpc_rows.append([Cell(row["label"]), Cell(row["status"]), Cell(criteria), Cell(basis)])
    doc.table("Functional performance summary mapped from WCAG evidence", ["Functional performance criterion", "Mapped result", "WCAG criteria", "Basis"], fpc_rows)
    doc.p("Without Hearing is Partially Supports in this mapping. Drupal Core's native Web surface does not require hearing and provides no native audio/video, so the deaf and hard-of-hearing community is not broadly disadvantaged by Core. The exception is authoring support for captions and transcripts (1.2.2), plus any other known media-authoring barriers. Contrib media players are separate products and need their own evaluation.")
    doc.links([
        ("CivicActions accessibility data reference / FPC mapping", "https://github.com/CivicActions/accessibility-data-reference"),
        ("Section 508 functional performance criteria", "https://www.access-board.gov/ict/"),
    ])
    doc.h2("Functional Performance, Hardware, Software and Support Documentation")
    doc.p("These Section 508/ACR chapters are not evaluated by this web issue-evidence pipeline. They are shown so the draft has the complete ACR shape; a reviewer must evaluate them or mark Not Applicable with a rationale.")
    rows = []
    chapter_labels = {
        "functional_performance_criteria": "Functional Performance Criteria",
        "hardware": "Hardware",
        "software": "Software",
        "support_documentation_and_services": "Support Documentation and Services",
    }
    chapter_notes = {
        "functional_performance_criteria": "A mapped functional-performance summary is provided above from WCAG evidence. It is not an independent FPC test; the OpenACR FPC chapter remains Not Evaluated.",
        "hardware": "Outside the declared product scope: Drupal Core is web software with no hardware product in this assessment.",
        "software": "Outside the declared product scope: no packaged non-web software product is included in this assessment.",
        "support_documentation_and_services": "No separate support-documentation and services evaluation was performed for this draft.",
    }
    for chapter in non_wcag:
        chapter_id = chapter.get("id") or ""
        rows.append([
            Cell(chapter_labels.get(chapter_id, chapter_id.replace("_", " ").title())),
            Cell(str(len(chapter.get("criteria") or []))),
            Cell("Not Evaluated"),
            Cell(chapter_notes.get(chapter_id, "Not evaluated by this web issue-evidence method.")),
        ])
    doc.table("Non-WCAG ACR chapters", ["Chapter", "Criteria", "Draft result", "Remarks and explanations"], rows)

    doc.h2("ATAG 2.0 authoring evidence")
    doc.p("ATAG 2.0 is a separate standard from WCAG and is not part of this ACR narrative. Drupal Core's authoring-tool evidence is reported separately. Part A/B is assigned only from explicit tags or a reviewed issue mapping; unassigned issues remain for human triage. The WAI ATAG Report Tool JSON draft contains no conformance values.")
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
        "Use the criterion-evidence ledger to review reported barriers and decide whether a formal ACR result is justified.",
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
    doc.h2("Beyond WCAG: non-WCAG accessibility considerations")
    considerations = load_considerations()
    doc.p("This box is outside WCAG and outside the OpenACR result terms. It records accessibility topics that can create real barriers without a clean WCAG 2.2 AA success criterion. These are review prompts, not findings, and no Supports, Partially Supports or Does Not Support value is assigned.")
    non_wcag_rows = []
    for item in considerations.get("items") or []:
        title = Cell(item.get("title"), item.get("source_url"))
        why = item.get("why")
        collect = item.get("what_to_collect")
        status = f"{item.get('evidence_state')} · {item.get('review_status')}"
        non_wcag_rows.append([title, Cell(why), Cell(collect), Cell(status)])
    doc.table(
        "Non-WCAG accessibility considerations",
        ["Topic", "Why it matters", "Evidence to collect", "Review status"],
        non_wcag_rows,
    )
    doc.p("EN 301 549 user preferences and motion-sensitivity concerns are examples of best-practice accessibility work that a WCAG-only report can miss. They need separate evidence and human review before any claim.")
    doc.links([
        ("EN 301 549 V3.2.1 (ETSI)", "https://www.etsi.org/deliver/etsi_en/301500_301599/301549/03.02.01_60/en_301549v030201p.pdf"),
        ("WCAG 2.3.3 Animation from Interactions", "https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html"),
        ("prefers-reduced-motion", "https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion"),
        ("forced-colors", "https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors"),
    ])
    doc.h2_anchor("Why these accessibility issues matter", "human-impact")
    doc.p("Accessibility barriers can prevent people from finding information, completing tasks, communicating and using digital services independently. The barrier arises from the interaction between a person's needs and inaccessible technology, content or environments; disability itself is not the problem.")
    doc.h3("Accessibility is a global concern")
    doc.p("The World Health Organization estimates that approximately 1.3 billion people, or 16% of the world's population, experience significant disability. WHO also reports at least 2.2 billion people with near or distance vision impairment, and approximately 430 million people who require rehabilitation for disabling hearing loss.")
    doc.p("These estimates use different definitions and overlap. They are context for the scale of accessibility needs, not counts of Drupal users and not estimates of people excluded by this release.")
    stats = load_global_stats()
    stat_rows = []
    for item in stats.get("statistics") or []:
        estimate = _format_population(item["value"])
        if item.get("percentage"):
            estimate += f" ({item['percentage']}%)"
        stat_rows.append([
            Cell(item.get("organization") or "Source", item.get("source_url")),
            Cell(item.get("measure") or ""),
            Cell(estimate),
            Cell(item.get("population_definition") or item.get("geography") or ""),
            Cell(item.get("source_publication_date") or "Not recorded"),
            Cell("; ".join(item.get("limitations") or [])),
        ])
    doc.table("Global disability context (WHO)", ["Source", "Measure", "Estimate", "Population and scope", "Source date", "Limitations"], stat_rows)
    doc.p(f"Repository verification date for these figures: {stats.get('verified_at', 'not recorded')}. Definitions and dates are retained rather than combining the populations.")
    doc.h3("How barriers affect people")
    doc.p("The same barrier can affect several functional needs. These examples are illustrative and are not a complete crosswalk.")
    doc.table("Functional needs and representative barriers", ["Functional need", "Example barriers", "WCAG examples"], [
        [Cell("Access without vision"), Cell("Missing image alternatives, inaccessible controls and structure"), Cell("1.1.1, 1.3.1, 4.1.2")],
        [Cell("Access with limited vision"), Cell("Insufficient contrast, poor reflow, restricted text enlargement"), Cell("1.4.3, 1.4.4, 1.4.10")],
        [Cell("Access without hearing"), Cell("Audio without captions or alternatives"), Cell("1.2.2, 1.2.4")],
        [Cell("Alternative input and limited dexterity"), Cell("Keyboard inaccessibility, dragging requirements, small targets"), Cell("2.1.1, 2.5.7, 2.5.8")],
        [Cell("Cognitive accessibility"), Cell("Complex instructions, redundant entry, inaccessible authentication"), Cell("3.3.2, 3.3.7, 3.3.8")],
        [Cell("Protection from seizure triggers"), Cell("Excessive flashing"), Cell("2.3.1")],
    ])
    doc.h3("Why remediation matters for Drupal")
    doc.p("Drupal Core is shared software used by many sites and downstream products. A defect in a reusable component can affect multiple deployments, and a fix can benefit them together. But an issue in Core does not prove that every Drupal site contains the barrier: the component may be disabled, the site may use another theme or implementation, the issue may affect only some interactions or roles, and the reported issue may not reproduce in this release. No Drupal installation count is used to estimate affected people.")
    doc.h3("Sources, methodology and limitations")
    doc.p("Criterion impact descriptions are proposed editorial summaries based on W3C Understanding documents and the functional needs in this report. Section 508 FPC and EN 301 549 relationships are maintained separately; EN 301 549 clause mapping is still pending. Global statistics come from WHO and retain their source dates, definitions and limitations.")
    doc.p("These descriptions are not conformance assessments, do not establish that a barrier occurs in a particular Drupal deployment, and do not replace testing with disabled people. The impact records are marked proposed until a human reviewer records approval. No AI model is used as an authoritative source for a description or statistic.")
    doc.links([
        ("WHO: Disability", "https://www.who.int/news-room/fact-sheets/detail/disability-and-health"),
        ("WHO: Blindness and vision impairment", "https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment"),
        ("WHO: Deafness and hearing loss", "https://www.who.int/news-room/fact-sheets/detail/deafness-and-hearing-loss"),
        ("W3C: How People with Disabilities Use the Web", "https://www.w3.org/WAI/people-use-web/"),
    ])
    doc.h2("References")
    doc.p("Every Drupal.org issue cited in the criterion tables is listed below by WCAG principle. Each group can be collapsed; each criterion keeps a stable reference anchor. Each link goes to the public issue where the barrier is discussed.")
    principle_labels = {
        "1": "1. Perceivable",
        "2": "2. Operable",
        "3": "3. Understandable",
        "4": "4. Robust",
    }
    handles = {
        str(criterion.get("id")): criterion.get("handle") or ""
        for chapter in catalog.get("chapters") or []
        for criterion in chapter.get("criteria") or []
    }
    grouped = {}
    for criterion_id in sorted(by_criterion):
        grouped.setdefault(criterion_id.split(".", 1)[0], []).append(criterion_id)
    for principle in ("1", "2", "3", "4"):
        criterion_ids = grouped.get(principle) or []
        if not criterion_ids:
            continue
        groups = []
        for criterion_id in criterion_ids:
            handle = handles.get(criterion_id, "")
            groups.append((
                f"{criterion_id} — {handle or 'WCAG criterion'}",
                _reference_items(by_criterion[criterion_id]),
            ))
        doc.details(f"{principle_labels[principle]} ({len(groups)} {_plural(len(groups), 'criterion', 'criteria')})", groups)
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
