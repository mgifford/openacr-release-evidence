"""Render a static, no-JavaScript evidence report.

All upstream text is escaped. The report is intentionally usable without
JavaScript, from a GitHub Pages repository subpath, and at 320 CSS pixels.
"""
import json
import shutil
from html import escape
from pathlib import Path

from .criterion_evidence import build_criterion_evidence
from .reproduction_evidence import build_reproduction_evidence
from .model import digest_artifact
from .wcag import (
    APPLICABILITY_LABELS,
    APPLICABILITY_MEANINGS,
    SHORT_APPLICABILITY,
    SUPPORT_STATUS_LABELS,
    criterion_info,
)

EXCERPT_LIMIT = 1800
COMMENT_LIMIT = 8
COMMENT_EXCERPT = 600


def esc(value):
    return escape("" if value is None else str(value), quote=True)


def safe_link(url, text=None):
    if isinstance(url, str) and url.startswith("https://"):
        label = esc(text if text is not None else url)
        return f'<a href="{esc(url)}">{label}</a>'
    return esc(text if text is not None else url)


def display_date(value):
    if not value:
        return "Not recorded"
    text = str(value)
    return text[:10] if len(text) >= 10 else text


def excerpt(text, limit=EXCERPT_LIMIT):
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def anchor_for(value):
    return "issue-" + "".join(ch if ch.isalnum() else "-" for ch in str(value))


def app_label(value):
    return APPLICABILITY_LABELS.get(value, value or "Unknown")


def _facts(rows):
    parts = ['<dl class="facts">']
    for term, definition in rows:
        parts.append(f"<dt>{esc(term)}</dt><dd>{definition}</dd>")
    parts.append("</dl>")
    return "".join(parts)


def _summary_table(findings):
    counts = {}
    for finding in findings:
        counts[finding["applicability"]] = counts.get(finding["applicability"], 0) + 1
    parts = [
        '<table class="summary-table">',
        "<caption>Findings by release applicability. Counts are evidence states, not an accessibility score.</caption>",
        "<thead><tr><th scope=\"col\">Release applicability</th><th scope=\"col\">Count</th><th scope=\"col\">Meaning</th></tr></thead><tbody>",
    ]
    for key in sorted(counts):
        parts.append(
            f'<tr><th scope="row">{esc(app_label(key))}</th><td>{counts[key]}</td>'
            f'<td>{esc(APPLICABILITY_MEANINGS.get(key, "No documented meaning"))}</td></tr>'
        )
    parts.append("</tbody></table>")
    return "".join(parts)


def _status_table(findings):
    counts = {}
    for finding in findings:
        label = finding.get("tracker_status_label") or "Unknown"
        counts[label] = counts.get(label, 0) + 1
    parts = [
        '<table class="summary-table">',
        "<caption>Tracker workflow states among the collected active issues. Tracker status is not release applicability.</caption>",
        '<thead><tr><th scope="col">Tracker status</th><th scope="col">Count</th></tr></thead><tbody>',
    ]
    for label in sorted(counts):
        parts.append(f'<tr><th scope="row">{esc(label)}</th><td>{counts[label]}</td></tr>')
    parts.append("</tbody></table>")
    return "".join(parts)


def _criterion_section(criterion, findings):
    info = criterion_info(criterion)
    section_id = "sc-" + criterion.replace(".", "-")
    parts = [
        f'<section class="criterion" aria-labelledby="{section_id}">',
        f'<h3 id="{section_id}">{esc(criterion)} {esc(info["title"])} — Level {esc(info["level"])}</h3>',
        f'<p class="meta">Criterion title from WCAG 2.2. {safe_link(info["url"], "W3C definition")}. '
        "Issue tags suggest candidate relevance only; they are not a conformance determination.</p>",
        '<ul class="finding-list">',
    ]
    for finding in findings:
        parts.append(
            "<li>"
            f'<a href="#{anchor_for(finding["issue_id"])}">{esc(finding.get("title") or finding["issue_id"])}</a> '
            f'<span class="state">{esc(app_label(finding["applicability"]))}</span>'
            f'<span class="meta"> — {esc(finding.get("tracker_status_label") or "Unknown tracker status")}</span>'
            "</li>"
        )
    parts.append("</ul></section>")
    return "".join(parts)


def _commit_list(commits):
    if not commits:
        return "<p>No matching fix commits were found in the indexed branches.</p>"
    parts = ['<ul class="commit-list">']
    for commit in commits:
        state = "contained in release tag" if commit.get("in_release") else "not contained in release tag"
        branches = commit.get("branches") or ([commit.get("branch")] if commit.get("branch") else [])
        parts.append(
            "<li>"
            f'{safe_link(commit.get("url"), (commit.get("short_id") or commit.get("sha") or "")[:12])} '
            f'<span class="meta">{esc(", ".join(branches) or "branch unknown")} · '
            f'{esc(display_date(commit.get("created_at")))} · '
            f'{esc(commit.get("title"))} · <strong>{esc(state)}</strong></span>'
            "</li>"
        )
    parts.append("</ul>")
    return "".join(parts)


def _comment_list(issue):
    comments = issue.get("comments") or []
    useful = [comment for comment in comments if not comment.get("machine_generated")]
    shown = useful[:COMMENT_LIMIT]
    if not shown:
        return "<p>No substantive comments were captured.</p>"
    parts = ['<ol class="comments">']
    for comment in shown:
        parts.append(
            "<li>"
            f'<p class="comment-meta"><strong>{esc(comment.get("author"))}</strong> · '
            f'{esc(display_date(comment.get("created_at")))} · '
            f'{safe_link(comment.get("url"), "comment link")}</p>'
            f'<p class="preline">{esc(excerpt(comment.get("body_text"), COMMENT_EXCERPT))}</p>'
            "</li>"
        )
    parts.append("</ol>")
    if len(useful) > len(shown):
        parts.append(
            f'<p class="meta">Showing {len(shown)} of {len(useful)} substantive comments. '
            f'{safe_link(issue.get("url"), "Read all comments at the source")}.</p>'
        )
    return "".join(parts)


def _issue_article(finding, issue):
    anchor = anchor_for(finding["issue_id"])
    nid = issue.get("source_id") if issue else finding["issue_id"]
    source = safe_link(finding.get("source_url"), f"Drupal.org issue #{nid}")
    if finding.get("evidence_status") == "inventory":
        return (
            f'<article class="issue" data-evidence="inventory" id="{anchor}" aria-labelledby="{anchor}-title">'
            f'<h3 id="{anchor}-title">{esc(finding.get("title") or finding["issue_id"])}</h3>'
            f'<p class="issue-source">{source} · <span class="meta">{esc(finding["issue_id"])}</span></p>'
            '<p class="meta"><strong>Metadata-only inventory record.</strong> No comments, merge requests or commit '
            'history were collected. Read the source issue before relying on its applicability.</p>'
            f'<p class="meta">Tracker status: {esc(finding.get("tracker_status_label") or "Unknown")} · '
            f'Component: {esc(finding.get("component") or "Not recorded")} · '
            f'Version: {esc(finding.get("tracker_version") or "Not recorded")} · '
            f'Observed: {esc(finding.get("observed_at") or "Not recorded")}</p>'
            "</article>"
        )
    criteria = finding.get("wcag_candidates") or []
    criterion_links = ", ".join(
        f'<a href="#sc-{esc(criterion.replace(".", "-"))}">{esc(criterion)}</a>'
        for criterion in criteria
    ) or "No WCAG criterion tag on the issue"
    commits = finding.get("commits") or []
    mrs = finding.get("merge_requests") or []
    parts = [
        f'<article class="issue" id="{anchor}" aria-labelledby="{anchor}-title">',
        f'<h3 id="{anchor}-title">{esc(finding.get("title") or finding["issue_id"])}</h3>',
        f'<p class="issue-source">{source} · <span class="meta">{esc(finding["issue_id"])}</span></p>',
        ('<p class="meta"><strong>Metadata-only inventory record.</strong> Comments, merge requests and commit history were not collected for this active issue; read the source issue before relying on its applicability.</p>'
         if finding.get("evidence_status") == "inventory" else ""),
        _facts([
            ("Release applicability", f'<strong>{esc(app_label(finding["applicability"]))}</strong>'),
            ("Why", esc(finding.get("reason"))),
            ("Evidence detail", "Metadata only" if finding.get("evidence_status") == "inventory" else "Full comments and merge requests"),
            ("Evidence basis", esc(finding.get("basis"))),
            ("Fix included in target?", "Yes" if finding.get("fix_included_in_target", finding.get("fix_included_in_release")) else "No"),
            ("Tracker status (not release status)", esc(finding.get("tracker_status_label") or "Unknown")),
            ("Version field at last fetch", esc(finding.get("tracker_version") or "Not recorded")),
            ("Component", esc(finding.get("component") or "Not recorded")),
            ("Surface", esc((finding.get("surface") or {}).get("surface", "web")) + " (" + esc((finding.get("surface") or {}).get("basis", "default-web")) + ")"),
            ("Created / updated", f'{esc(display_date(finding.get("created_at")))} / {esc(display_date(issue.get("updated_at") if issue else None))}'),
            ("Observed at", esc(finding.get("observed_at") or "Not recorded")),
            ("Candidate WCAG criteria", criterion_links),
            ("Review state", esc(finding.get("review_status") or "unreviewed")),
        ]),
    ]
    if mrs:
        parts.append('<h4 class="subhead">Merge requests</h4><ul class="commit-list">')
        for mr in mrs:
            parts.append(
                "<li>"
                f'{safe_link(mr.get("url"), f"!{mr.get('iid')}")} '
                f'<span class="meta">{esc(mr.get("state"))} → {esc(mr.get("target_branch"))} · '
                f'{esc(mr.get("title"))}</span></li>'
            )
        parts.append("</ul>")
    parts.append('<h4 class="subhead">Matching commits</h4>')
    parts.append(_commit_list(commits))
    if issue and finding.get("evidence_status") != "inventory":
        description = issue.get("description_text") or ""
        parts.append(
            '<details class="issue-detail">'
            f'<summary>Issue summary and comments ({len(issue.get("comments") or [])} comments captured)</summary>'
            '<h4>Issue summary</h4>'
            f'<p class="preline">{esc(excerpt(description))}</p>'
            f'<p class="meta">{safe_link(issue.get("url"), "Read the full issue and discussion at Drupal.org")}</p>'
            '<h4>Selected comments</h4>'
            f"{_comment_list(issue)}"
            "</details>"
        )
    parts.append("</article>")
    return "".join(parts)


def _gaps(findings):
    needs = [
        finding for finding in findings
        if finding["applicability"] in {"likely-affected", "unknown", "confirmed-fixed"}
    ]
    if not needs:
        return "<p>No findings require further verification in this collection.</p>"
    parts = ["<ul class=\"gap-list\">"]
    for finding in needs:
        parts.append(
            "<li>"
            f'<a href="#{anchor_for(finding["issue_id"])}">{esc(finding.get("title") or finding["issue_id"])}</a> '
            f'— <strong>{esc(app_label(finding["applicability"]))}</strong>. {esc(finding.get("reason"))}'
            "</li>"
        )
    parts.append("</ul>")
    return "".join(parts)


def compact_artifact(analysis):
    """Return the compact artifact published as evidence.json.

    Full comments/descriptions remain in the rendered HTML and in the private
    collection; the public evidence file keeps findings and issue identity so it
    is small enough to publish five times without duplicating the queue.
    """
    keep_issue = (
        "schema_version", "id", "project_scoped_id", "source_system", "source_project",
        "source_id", "url", "title", "labels", "status", "created_at", "updated_at",
        "component", "version", "priority", "category", "evidence_status",
        "wcag_candidates", "atag", "provenance",
    )
    compact = {
        key: value
        for key, value in analysis.items()
        if key not in ("issues", "findings", "evidence_digest", "compact")
    }
    compact["issues"] = [
        {key: issue.get(key) for key in keep_issue if key in issue}
        for issue in (analysis.get("issues") or [])
    ]
    compact["findings"] = [dict(finding) for finding in (analysis.get("findings") or [])]
    compact["compact"] = True
    compact["digest_scope"] = "sha256 over the published compact evidence artifact excluding generated_at and evidence_digest"
    compact["evidence_digest"] = digest_artifact(compact)
    return compact


def render_report(analysis, output_dir, css_source=None, full_collection=None):
    """Write index.html, report.css, evidence.json and summary.json."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    compact = compact_artifact(analysis)
    analysis["evidence_digest"] = compact["evidence_digest"]
    analysis["digest_scope"] = compact["digest_scope"]
    assessment = analysis.get("assessment") or {}
    target = analysis.get("target") or {}
    summary = analysis.get("summary") or {}
    collection = analysis.get("collection") or {}
    findings = analysis.get("findings") or []
    issue_source = (full_collection or {}).get("issues") if full_collection else None
    issues = {issue.get("id"): issue for issue in (issue_source or analysis.get("issues") or [])}
    synthetic = bool(assessment.get("synthetic"))
    standard = ", ".join(assessment.get("standards") or []) or "Not recorded"
    installation = assessment.get("installation") or {}
    enabled_themes = installation.get("enabled_themes") or {}
    theme_text = ", ".join(f"{key}: {value}" for key, value in enabled_themes.items()) or "Not recorded"
    title = (
        f"{assessment.get('product', 'Product')} {target.get('release', assessment.get('release', ''))} "
        "accessibility evidence"
    )
    finding_groups = {}
    unmapped = []
    for finding in findings:
        criteria = finding.get("wcag_candidates") or []
        if not criteria:
            unmapped.append(finding)
        for criterion in criteria:
            finding_groups.setdefault(criterion, []).append(finding)
    rows = [
        ("Product", esc(assessment.get("product"))),
        ("Release", esc(target.get("release") or assessment.get("release"))),
        ("Target ref", f'{esc(target.get("ref") or assessment.get("ref"))} '
                        f'({esc(target.get("ref_type") or "tag")})'),
        ("Support status", esc(SUPPORT_STATUS_LABELS.get(target.get("support_status"), target.get("support_status") or "Unknown"))),
        ("Release line", esc(target.get("release_line") or "Not recorded")),
        ("Parent project", esc(target.get("parent_project") or "None (top-level product)")),
        ("Target commit", f'{esc(target.get("tag_commit_short") or "Not resolved")}'
                          f' <span class="meta">{esc(target.get("tag_commit") or "")}</span>'),
        ("Target date", esc(display_date(target.get("tag_date")))),
        ("Assessment identifier", esc(assessment.get("id"))),
        ("Assessment date", esc(display_date(analysis.get("generated_at")))),
        ("Standards baseline", esc(standard)),
        ("Profile", esc(installation.get("profile") or "Not recorded")),
        ("Drupal Core version", esc(installation.get("drupal_core_version") or "Not recorded")),
        ("Composer lock SHA-256", esc(installation.get("composer_lock_sha256") or "Not recorded")),
        ("Enabled themes", esc(theme_text)),
        ("In-scope components", esc(", ".join(assessment.get("components") or []) or "Not recorded")),
        ("Surface split", f'{sum(1 for f in findings if (f.get("surface") or {}).get("surface", "web") == "web")} web · '
                         f'{sum(1 for f in findings if (f.get("surface") or {}).get("surface", "web") == "authoring")} authoring'),
        ("Configuration note", esc(installation.get("configuration") or "Not recorded")),
        ("Collection source", "Drupal.org REST API for discovery, tags and inventory; drupalorg-cli JSON for detailed issues, comments and all MR states"),
        ("Collection timestamp", esc((collection.get("summary") or {}).get("retrieved_at") or analysis.get("generated_at"))),
        ("Issues collected (active, review-relevant)", esc(len(issues))),
        ("Collection status filter", esc(", ".join(str(item) for item in ((collection.get("summary") or {}).get("statuses") or [])) or "Not recorded") + " — fixed/closed issues excluded"),
        ("Evidence detail", f'{esc((collection.get("summary") or {}).get("detailed", 0))} full · '
                          f'{esc((collection.get("summary") or {}).get("inventory", 0))} metadata-only inventory'),
        ("Comments captured", esc((collection.get("summary") or {}).get("comments", "Not recorded"))),
        ("Issues with merge requests", esc((collection.get("summary") or {}).get("with_merge_requests", "Not recorded"))),
        ("Issues with WCAG tags", esc((collection.get("summary") or {}).get("with_wcag_tags", "Not recorded"))),
        ("Findings", esc(len(findings))),
        ("Fix commits included in target", esc(summary.get("fix_included_in_target", summary.get("fix_included_in_release", 0)))),
        ("Findings needing verification", esc(summary.get("needs_verification", 0))),
    ]

    target_id = target.get("assessment_id") or assessment.get("id")
    support = target.get("support_status") or "unknown"
    release = target.get("release") or assessment.get("release") or "Unknown release"
    full_evidence = (collection.get("summary") or {}).get("detailed", "Not recorded")
    inventory_evidence = (collection.get("summary") or {}).get("inventory", "Not recorded")
    with_mrs = (collection.get("summary") or {}).get("with_merge_requests", "Not recorded")
    by_app = summary.get("by_applicability") or {}
    likely = by_app.get("likely-affected", 0)
    unknown = by_app.get("unknown", 0)
    needs = summary.get("needs_verification", 0)
    html = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="description" content="Draft release-scoped accessibility evidence. Not an Accessibility Conformance Report.">',
        '<meta name="robots" content="noindex">',
        f"<title>{esc(title)}</title>",
        '<link rel="stylesheet" href="./report.css">',
        "</head>",
        "<body>",
        '<a class="skip" href="#main">Skip to main content</a>',
        '<header class="page-header">',
        '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'
        '<li><a href="../">All release reports</a></li>'
        f'<li><span aria-current="page">{esc(assessment.get("product", "Product"))} {esc(release)}</span></li>'
        "</ol></nav>",
        '<p class="eyebrow">OpenACR Release Evidence · release report</p>',
        '<div class="page-title-row">',
        f"<h1>{esc(title)}</h1>",
        '<div class="badges"><span class="badge badge-draft">Draft evidence</span>'
        f'<span class="badge badge-{esc(_support_class(support))}">{esc(_support_label(support))}</span>'
        f'<span class="badge">{esc(target.get("ref_type") or "tag")}</span></div>',
        "</div>",
        f'<p class="report-subtitle">{esc(assessment.get("product", "Product"))} <strong>{esc(release)}</strong> · '
        f'{esc(target.get("release_line") or "unknown line")} · assessment <code>{esc(assessment.get("id"))}</code></p>',
        '<p class="status-banner"><strong>Draft evidence, not an Accessibility Conformance Report or certification.</strong> '
        "Issue counts, issue status and commit inclusion do not establish WCAG conformance. A human reviewer must verify every claim.</p>",
    ]
    if synthetic:
        html.append('<p class="synthetic"><strong>Synthetic example.</strong> This target is a fixture and must not be read as evidence about a real release.</p>')
    html.append(
        f'<p class="meta">Generated {esc(display_date(analysis.get("generated_at")))} · '
        f'Standards baseline: {esc(standard)} · Assessment <code>{esc(assessment.get("id"))}</code></p>'
        "</header>"
    )
    html.append('<main id="main" tabindex="-1">')
    html.append(
        '<nav class="report-actions" aria-label="Supporting outputs">'
        '<h2>Supporting outputs</h2>'
        f'<ul><li><a href="./evidence.json">evidence.json</a></li>'
        f'<li><a href="./summary.json">summary.json</a></li>'
        f'<li><a href="./openacr.yaml">OpenACR draft YAML</a></li>'
        f'<li><a href="./openacr-validation.json">validation result</a></li>'
        f'<li><a href="./criterion-evidence.json">criterion evidence</a></li>'
        f'<li><a href="./reproduction-evidence.json">reproduction evidence</a></li>'
        f'<li><a href="./acr.html">ACR draft</a></li></ul>'
        '<p class="meta">The ACR is a derived draft, not an approved conformance report.</p></nav>'
    )
    html.append(_section_nav([
        ("scope", "Assessment scope"),
        ("summary", "Evidence summary"),
        ("reproduction", "Reproduction evidence"),
        ("position", "Why this is different"),
        ("criteria", "WCAG criterion evidence"),
        ("issues", "Issue evidence"),
        ("gaps", "Verification gaps"),
        ("method", "Method and limitations"),
        ("provenance", "Provenance"),
    ]))
    html.append('<section id="scope" aria-labelledby="scope-heading"><h2 id="scope-heading">Assessment scope</h2>')
    html.append('<p>This report describes one declared assessment target. It is not a statement about every Drupal installation, '
                'configuration or release.</p>')
    html.append(_facts([
        ("Product", esc(assessment.get("product"))),
        ("Release", esc(release)),
        ("Support status", esc(_support_label(support))),
        ("Assessment date", esc(display_date(analysis.get("generated_at")))),
        ("Target commit", f'<code>{esc(target.get("tag_commit_short") or "Not resolved")}</code>'),
        ("Evidence completeness", f'{esc(full_evidence)} full · {esc(inventory_evidence)} metadata-only'),
        ("Assessment identifier", esc(assessment.get("id"))),
    ]))
    if target.get("scope_note"):
        html.append(f'<p class="scope-note">{esc(target["scope_note"])}</p>')
    html.append('<h3>Complete assessment metadata</h3>')
    html.append(_facts(rows))
    html.append("</section>")
    html.append('<section id="summary" aria-labelledby="summary-heading"><h2 id="summary-heading">Evidence summary</h2>')
    html.append('<p><strong>This is not an accessibility score.</strong> The counts describe evidence states for the collected active issues. '
                'A low issue count does not mean the release is accessible; a high count does not prove a conformance failure.</p>')
    html.append(_metric_grid([
        ("Active findings", len(findings), "Collected active review-relevant issues represented as findings."),
        ("Full evidence", full_evidence, "Issue, comments and every merge-request state were collected."),
        ("Metadata-only", inventory_evidence, "Source, status, tags, component and version only."),
        ("Likely affected", likely, "Report-based evidence that the issue may affect this release; not a reproduction."),
        ("Unknown applicability", unknown, "Insufficient release-specific evidence to decide."),
        ("Needing verification", needs, "Findings that still need reproduction, testing or independent review."),
    ]))
    html.append(_summary_table(findings))
    html.append(_status_table(findings))
    html.append(
        f'<p class="meta">{esc(summary.get("findings", 0))} findings · '
        f'{esc(summary.get("fix_included_in_target", summary.get("fix_included_in_release", 0)))} fix commits contained in the target · '
        f'{esc(summary.get("unmapped_criteria", 0))} findings without a WCAG criterion tag · '
        f'{esc(summary.get("needs_verification", 0))} need further verification.</p>'
    )
    html.append("</section>")
    reproduction = build_reproduction_evidence(analysis)
    html.append('<section id="reproduction" aria-labelledby="reproduction-heading"><h2 id="reproduction-heading">Reproduction evidence</h2>')
    html.append('<p><strong>External evidence is not verification on this target.</strong> '
                'Drupal Core Lab records are listed for review, with their pinned commit and scope. '
                'No entry establishes conformance on this release.</p>')
    if reproduction["entries"]:
        html.append(f'<p>{reproduction["summary"]["records"]} external records; '
                    f'{reproduction["summary"]["in_active_collection"]} match active findings in this snapshot; '
                    f'{reproduction["summary"]["target_verified"]} verified on this target.</p>')
        html.append('<div class="table-scroll" tabindex="0" role="region" aria-label="External reproduction evidence"><table><caption>External Drupal Core Lab reproduction records</caption><thead><tr><th scope="col">Issue</th><th scope="col">External result</th><th scope="col">Source</th><th scope="col">This target</th><th scope="col">Review</th></tr></thead><tbody>')
        for item in reproduction["entries"]:
            issue = f'<a href="{esc(item.get("issue_url"))}">{esc(item.get("issue_id"))}</a>' if item.get("issue_url") else esc(item.get("issue_id"))
            source = f'<a href="{esc(item.get("source_url"))}">Core Lab</a>' if item.get("source_url") else "Not linked"
            html.append(f'<tr><td>{issue}</td><td>{esc(item.get("source_result"))}</td><td>{source}</td>'
                        f'<td>{esc(item.get("target_applicability"))} · not verified</td>'
                        f'<td>{esc(item.get("review_status"))}</td></tr>')
        html.append("</tbody></table></div>")
        html.append('<p class="meta">An external result remains external even when the issue appears in this target. '
                    'A target verification requires the exact release, configuration and recorded result.</p>')
    else:
        html.append('<p>No external reproduction record is available for this snapshot.</p>')
    html.append("</section>")
    html.append('<section id="position" aria-labelledby="position-heading"><h2 id="position-heading">Why this is different</h2>')
    html.append('<p>A VPAT is a template; a completed report is an ACR. Most vendor ACRs are periodic, sample-based snapshots reviewed by legal or product management, with the vendor issue queue kept separate. This report is an issue-queue attestation: it is generated from the full active Drupal Core Accessibility queue and keeps every cited issue linked. It is stronger on known-report completeness, traceability and recency; it is weaker on independent page sampling and manual assistive-technology coverage.</p>')
    html.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Comparison with a conventional vendor ACR"><table class="summary-table"><caption>Conventional vendor ACR and this issue-queue attestation</caption><thead><tr><th scope="col">Dimension</th><th scope="col">Conventional vendor ACR</th><th scope="col">This report</th></tr></thead><tbody>')
    for row in (
        ("Cadence", "Annual, biennial or procurement-driven", "Every weekly tracker snapshot"),
        ("Evidence", "Selected pages, flows or a WCAG-EM sample", "Full active Accessibility queue; detailed comments/MRs where collected"),
        ("Traceability", "Summary claims, often without issue links", "Every cited issue links to the public Drupal.org source"),
        ("Authoring", "Often folded into web or omitted", "Explicit Authoring Tool component and separate remarks"),
        ("Change", "Static until the next report", "Incremental; new issues and status changes appear next snapshot"),
        ("Independence", "Often a commissioned assessment", "Community-reported issue evidence; no independent WCAG-EM audit"),
    ):
        html.append(f'<tr><th scope="row">{esc(row[0])}</th><td>{esc(row[1])}</td><td>{esc(row[2])}</td></tr>')
    html.append('</tbody></table></div>')
    html.append('<p>This is not a WCAG-EM evaluation, a certification or a substitute for a procurement-specific ACR. A missing tagged issue is not evidence of support. Read the queue as reported barrier evidence and confirm every criterion with a reviewer.</p>')
    html.append('<p class="meta">Background: <a href="https://github.com/GSA/openacr/issues/180">GSA OpenACR issue #180</a> · <a href="https://www.drupal.org/docs/getting-started/accessibility/accessibility-conformance-report-acr-process">Drupal ACR process</a> · <a href="https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/">WCAG-EM 2.0</a>.</p>')
    html.append("</section>")
    html.append('<section id="criteria" aria-labelledby="criteria-heading"><h2 id="criteria-heading">WCAG criterion evidence</h2>')
    html.append('<p>Criteria are grouped from explicit Drupal.org tags such as <code>wcag143</code>. '
                'Tags are candidate evidence, not conformance results. Issues without a criterion tag are listed separately.</p>')
    html.append(_criterion_index(findings))
    for criterion in sorted(finding_groups):
        html.append(_criterion_section(criterion, finding_groups[criterion]))
    if unmapped:
        html.append('<section class="criterion" aria-labelledby="unmapped-heading">')
        html.append('<h3 id="unmapped-heading">Issues without a WCAG criterion tag</h3>')
        html.append('<p class="meta">These issues may still describe accessibility barriers. No criterion mapping is proposed here.</p><ul class="finding-list">')
        for finding in unmapped:
            html.append(
                "<li>"
                f'<a href="#{anchor_for(finding["issue_id"])}">{esc(finding.get("title") or finding["issue_id"])}</a> '
                f'<span class="state">{esc(app_label(finding["applicability"]))}</span></li>'
            )
        html.append("</ul></section>")
    html.append("</section>")
    html.append('<section id="issues" aria-labelledby="issues-heading"><h2 id="issues-heading">Issue evidence</h2>')
    html.append('<p>Detailed issues retain their source URL, tracker status, observation time, candidate criteria, comments and '
                'release-specific reasoning. Inventory records are compact metadata rows. Raw upstream responses are kept privately '
                'and are not published here.</p>')
    html.append(_issue_index(findings))
    html.append('<h3 id="canonical-issues-heading">Canonical issue records</h3>')
    html.append('<p class="meta">The full records follow, in issue-ID order. Each is the canonical target-specific evidence for its finding.</p>')
    for finding in sorted(findings, key=lambda item: item.get("issue_id") or ""):
        html.append(_issue_article(finding, issues.get(finding.get("issue_id"))))
    html.append("</section>")
    html.append('<section id="gaps" aria-labelledby="gaps-heading"><h2 id="gaps-heading">Verification gaps</h2>')
    html.append('<p>These are the findings that need reproduction, testing or independent review before an ACR statement can rely on them. '
                'Missing evidence is not a failed test.</p>')
    html.append(f'<p><strong>{esc(needs)} findings need verification.</strong> '
                f'{esc(likely)} likely affected; {esc(unknown)} unknown; all require a human decision before a conformance term is used. '
                'See the issue index for the source and evidence detail.</p>')
    html.append(_gaps(findings))
    html.append('<p>No issue in this report was reproduced against an installed Drupal 11.4.12 site in this phase. '
                'No screen-reader, keyboard, zoom or forced-colors testing of the assessed release is claimed.</p>')
    html.append("</section>")
    html.append('<section id="method" aria-labelledby="method-heading"><h2 id="method-heading">Method and limitations</h2>')
    html.append("<ol>"
                "<li>Paged the complete Drupal Core Accessibility queue (taxonomy term 1101) and kept only active review-relevant statuses: Active, Needs review, Needs work, RTBC and Patch. Fixed and closed issues are excluded.</li>"
                "<li>For a review-priority subset, retrieved the issue, its public comments and every merge request state through drupalorg-cli JSON output. Merged and closed MRs are included. The remaining active issues are complete inventory records (source, status, tags, component, version) with comments, MRs and commit history marked as not collected.</li>"
                "<li>Built a commit index for the target release branch and adjacent development branches, matched commit messages to issue IDs, and checked whether each commit is contained in the release tag using the public GitLab API.</li>"
                "<li>Applied documented classification rules. A tracker report is not a reproduction; commit inclusion is not behavioural verification; a closed issue is not proof of a release fix.</li>"
                "<li>Did not use AI, did not infer conformance and did not assign a percentage or score.</li>"
                "</ol>")
    html.append('<p class="meta">Discovery and tag resolution use the public Drupal.org API. Git containment uses '
                'git.drupalcode.org. The in-scope configuration intentionally enables the Default Admin theme; the standard '
                'profile in Drupal 11.4.12 uses Claro and Olivero, so this is a declared configuration rather than the stock default.</p>')
    try:
        release_changes = json.loads((Path(__file__).resolve().parents[2] / "config" / "release-changes.json").read_text(encoding="utf-8")).get("release_lines") or {}
    except (OSError, ValueError):
        release_changes = {}
    theme_info = release_changes.get(str(target.get("release_line") or "")) or {}
    if theme_info:
        front = ", ".join(theme_info.get("front_end_themes") or []) or "none recorded"
        admin = ", ".join(theme_info.get("admin_themes") or []) or "none recorded"
        removed = ", ".join(theme_info.get("removed") or [])
        theme_note = f"Theme availability for {target.get('release_line')}: front-end themes {front}; admin themes {admin}."
        if removed:
            theme_note += f" Removed in this line: {removed}."
        theme_note += " The core collection does not include the theme project queues; a theme ACR must cover those issues."
        html.append(f'<p class="scope-note">{esc(theme_note)}</p>')
    html.append('<h3>Limitations</h3><ul>'
                '<li>The report covers active review-relevant issues carrying the Accessibility tag; it is not a census of every barrier. '
                'Closed and fixed issues are excluded by policy. Some active issues are metadata-only inventory records; their '
                'commit/comment evidence was not collected in this snapshot.</li>'
                '<li>No issue was reproduced against an installed release in this phase. No screen-reader, keyboard, zoom, '
                'reduced-motion or forced-colors testing of the assessed release is claimed.</li>'
                '<li>Commit matching relies on issue numbers in commit messages. Commits that omit the issue number, or fixes '
                'delivered by configuration or contributed modules, are not matched.</li>'
                '<li>Commit containment is code inclusion, not proof that the barrier is behaviourally corrected.</li>'
                '<li>WCAG criterion tags are candidate relevance signals, not conformance determinations.</li>'
                '<li>An issue may describe a barrier that is fixed by a later release or by a downstream distribution; '
                'this report does not transfer those conclusions.</li>'
                '</ul>')
    html.append("</section>")
    html.append('<section id="provenance" aria-labelledby="provenance-heading"><h2 id="provenance-heading">Provenance and downloads</h2>')
    html.append(_facts([
        ("Evidence artifact digest", f'<code>{esc(analysis.get("evidence_digest"))}</code>'),
        ("Manifest digest", f'<code>{esc(analysis.get("manifest_digest"))}</code>'),
        ("Collection digest", f'<code>{esc(collection.get("collection_digest"))}</code>'),
        ("CLI version", esc((collection.get("cli_version") or "Not recorded"))),
        ("Commit index retrieved", esc(display_date((summary.get("commit_index") or {}).get("retrieved_at") or (collection.get("summary") or {}).get("retrieved_at")))),
        ("Commit index window", f'{esc((summary.get("commit_index") or {}).get("since"))} to generation time'),
        ("Raw upstream evidence", "Stored privately under private-evidence/ and excluded from publication"),
        ("Digest scope", esc(analysis.get("digest_scope"))),
    ]))
    html.append('<p>Download the machine-readable artifacts: '
                '<a href="./evidence.json">evidence.json</a> · '
                '<a href="./summary.json">summary.json</a> · '
                '<a href="./openacr.yaml">openacr.yaml</a> · '
                '<a href="./openacr-validation.json">openacr-validation.json</a> · '
                '<a href="./acr.html">ACR narrative</a> · '
                '<a href="./acr.md">acr.md</a>.</p>')
    html.append('<p class="meta">The OpenACR file is a schema- and catalog-validated <strong>draft skeleton</strong>. '
                'It intentionally contains no conformance values and uses a placeholder reviewer; a human must '
                'populate and approve it before publication. See <code>openacr-validation.json</code> for the check result.</p>')
    html.append("</section>")
    html.append("</main>")
    html.append(
        '<footer><p>Draft release evidence. Not an Accessibility Conformance Report. '
        f'Standards baseline: {esc(standard)}. '
        '<a href="https://www.w3.org/TR/WCAG22/">WCAG 2.2</a> · '
        '<a href="https://github.com/GSA/openacr">OpenACR</a> · '
        '<a href="https://www.drupal.org/project/drupal/issues">Drupal Core issue queue</a>.</p>'
        '<p class="meta">Report generated from reviewed source scripts; no browser JavaScript is required. Issue titles, excerpts and comments are quoted from public Drupal.org issues with source links and attribution; they remain subject to Drupal.org terms and are not relicensed under this project\'s MIT licence.</p></footer>'
    )
    html.append("</body></html>")
    (output / "index.html").write_text("\n".join(html) + "\n", encoding="utf-8")
    source_css = Path(css_source) if css_source else Path(__file__).resolve().parent / "static" / "report.css"
    shutil.copyfile(source_css, output / "report.css")
    (output / "evidence.json").write_text(
        json.dumps(compact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary_doc = {
        "target": target,
        "assessment": assessment,
        "summary": summary,
        "generated_at": analysis.get("generated_at"),
        "evidence_digest": analysis.get("evidence_digest"),
        "manifest_digest": analysis.get("manifest_digest"),
    }
    (output / "summary.json").write_text(
        json.dumps(summary_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "criterion-evidence.json").write_text(
        json.dumps(build_criterion_evidence(analysis), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "reproduction-evidence.json").write_text(
        json.dumps(reproduction, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output


def _short_state(value):
    return SHORT_APPLICABILITY.get(value, value or "Unknown")


def _support_label(value):
    return SUPPORT_STATUS_LABELS.get(value, value or "Unknown")



def _slug(value):
    return "".join(ch if ch.isalnum() else "-" for ch in str(value).lower()).strip("-") or "value"


def _support_class(value):
    return {
        "supported": "supported",
        "pre-release": "pre-release",
        "development": "development",
    }.get(value or "", "unknown")


def _artifact_links(target_id):
    return (
        '<ul class="artifact-links">'
        '<li><span class="label">Downloads:</span></li>'
        f'<li><a href="./{esc(target_id)}/evidence.json">evidence.json</a></li>'
        f'<li><a href="./{esc(target_id)}/summary.json">summary.json</a></li>'
        f'<li><a href="./{esc(target_id)}/openacr.yaml">OpenACR draft YAML</a></li>'
        f'<li><a href="./{esc(target_id)}/openacr-validation.json">validation</a></li>'
        f'<li><a href="./{esc(target_id)}/acr.html">ACR draft</a></li>'
        "</ul>"
    )


def _target_card(analysis):
    target = analysis.get("target") or {}
    summary = analysis.get("summary") or {}
    collection_summary = (analysis.get("collection") or {}).get("summary") or {}
    target_id = target.get("assessment_id")
    release = target.get("release") or target.get("ref") or "Unknown release"
    support = target.get("support_status") or "unknown"
    line = target.get("release_line") or "unknown"
    counts = summary.get("by_applicability") or {}
    full = collection_summary.get("detailed", "Not recorded")
    inventory = collection_summary.get("inventory", "Not recorded")
    with_mrs = collection_summary.get("with_merge_requests", "Not recorded")
    ref_type = target.get("ref_type") or "tag"
    fixed = summary.get("fix_included_in_target", summary.get("fix_included_in_release", 0))
    return (
        f'<li class="release-card" id="target-{esc(target_id)}" '
        f'data-support="{esc(support)}" data-line="{esc(_slug(line))}">'
        f'<h3><a href="./{esc(target_id)}/">{esc(target.get("product") or "Product")} {esc(release)}</a></h3>'
        '<div class="badges">'
        f'<span class="badge badge-{esc(_support_class(support))}">{esc(_support_label(support))}</span>'
        f'<span class="badge">{esc(ref_type)}</span>'
        f'<span class="badge">{esc(line)} line</span>'
        "</div>"
        '<dl class="release-meta">'
        f'<div><dt>Exact version</dt><dd>{esc(release)}</dd></div>'
        f'<div><dt>Release line</dt><dd>{esc(line)}</dd></div>'
        f'<div><dt>Snapshot</dt><dd>{esc(display_date(analysis.get("generated_at")))}</dd></div>'
        f'<div><dt>Findings represented</dt><dd>{esc(summary.get("findings", 0))}</dd></div>'
        f'<div><dt>Likely affected</dt><dd>{esc(counts.get("likely-affected", 0))}</dd></div>'
        f'<div><dt>Unknown applicability</dt><dd>{esc(counts.get("unknown", 0))}</dd></div>'
        f'<div><dt>Full evidence</dt><dd>{esc(full)}</dd></div>'
        f'<div><dt>Metadata-only</dt><dd>{esc(inventory)}</dd></div>'
        f'<div><dt>Issues with merge requests</dt><dd>{esc(with_mrs)}</dd></div>'
        "</dl>"
        f'<p class="summary-line">{esc(summary.get("findings", 0))} findings · {esc(fixed)} with a fix in the target · '
        f'{esc(counts.get("likely-affected", 0))} likely affected · {esc(counts.get("unknown", 0))} unknown. '
        "Counts are evidence states, not an accessibility score.</p>"
        '<p class="card-actions">'
        f'<a class="primary-action" href="./{esc(target_id)}/">Open evidence report</a>'
        f'<span class="meta">{esc(target.get("parent_project") or "Top-level product")}</span>'
        "</p>"
        f"{_artifact_links(target_id)}"
        "</li>"
    )


def _release_finder(analyses):
    lines = []
    for analysis in analyses:
        line = (analysis.get("target") or {}).get("release_line") or "unknown"
        if line not in lines:
            lines.append(line)
    index = ['<nav aria-label="Release index"><h3>Release index</h3><ul class="release-index">']
    for analysis in analyses:
        target = analysis.get("target") or {}
        target_id = target.get("assessment_id")
        index.append(
            f'<li><a href="#target-{esc(target_id)}">{esc(target.get("product") or "Product")} '
            f'{esc(target.get("release") or target.get("ref"))}</a> '
            f'<span class="meta">— {esc(target.get("release_line") or "unknown")} line, '
            f'{esc(_support_label(target.get("support_status")))}</span></li>'
        )
    index.append("</ul></nav>")
    filter_html = [
        '<form class="filters" aria-describedby="filter-note">',
        '<fieldset><legend>Support status</legend><div class="filter-options">',
        '<label><input type="radio" name="status" id="filter-status-all" checked> All releases</label>',
        '<label><input type="radio" name="status" id="filter-status-supported"> Supported release line</label>',
        '<label><input type="radio" name="status" id="filter-status-pre-release"> Pre-release</label>',
        '<label><input type="radio" name="status" id="filter-status-development"> Development branch</label>',
        "</div></fieldset>",
        '<fieldset><legend>Release line</legend><div class="filter-options">',
        '<label><input type="radio" name="line" id="filter-line-all" checked> All lines</label>',
    ]
    for line in lines:
        filter_html.append(
            f'<label><input type="radio" name="line" id="filter-line-{esc(_slug(line))}"> {esc(line)}</label>'
        )
    filter_html.extend(["</div></fieldset></form>"])
    css = []
    for line in lines:
        css.append(
            f'body:has(#filter-line-{_slug(line)}:checked) '
            f'.release-card:not([data-line="{_slug(line)}"]){{display:none}}'
        )
    return (
        '<section class="finder" aria-labelledby="finder-heading">'
        '<h3 id="finder-heading">Filter and jump to a release</h3>'
        '<p>Choose a support status or release line, or use the release index. '
        "The exact version is shown on every card and in the report title.</p>"
        + "".join(index)
        + "".join(filter_html)
        + '<p class="filter-note" id="filter-note">Filters use CSS only and do not remove any release from the page. '
        "If your browser does not support CSS filtering, all releases remain visible. "
        "For exact-version search, use your browser's Find command (Ctrl/Cmd+F).</p>"
        "</section>",
        "".join(css),
    )


def _matrix_table(issue_ids, issue_titles, analyses, caption):
    parts = ['<table class="matrix-table">', f"<caption>{esc(caption)}</caption>"]
    parts.append("<thead><tr><th scope=\"col\">Issue</th>")
    for analysis in analyses:
        target = analysis["target"]
        parts.append(
            f'<th scope="col"><a href="./{esc(target.get("assessment_id"))}/">{esc(target.get("release"))}</a>'
            f'<br><span class="meta">{esc(_support_label(target.get("support_status")))}</span></th>'
        )
    parts.append("</tr></thead><tbody>")
    for issue_id in issue_ids:
        anchor = anchor_for(issue_id)
        first_id = analyses[0]["target"]["assessment_id"]
        parts.append(f'<tr><th scope="row"><a href="./{esc(first_id)}/#{anchor}">{esc(issue_titles[issue_id])}</a></th>')
        for analysis in analyses:
            target = analysis["target"]
            finding = next((item for item in analysis.get("findings") or [] if item["issue_id"] == issue_id), None)
            if finding:
                parts.append(
                    f'<td><a href="./{esc(target["assessment_id"])}/#{anchor}">{esc(_short_state(finding["applicability"]))}</a></td>'
                )
            else:
                parts.append('<td>Not collected</td>')
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def _criterion_index(findings):
    groups = {}
    for finding in findings:
        for criterion in finding.get("wcag_candidates") or []:
            groups.setdefault(criterion, []).append(finding)
    parts = [
        '<h3 id="criterion-index-heading">Criterion index</h3>',
        '<p>Every WCAG criterion with an explicit issue tag, linked to its full evidence section. '
        'Counts are issue tags, not conformance results.</p>',
        '<div class="table-scroll" tabindex="0" role="region" aria-label="WCAG criterion index">',
        '<table class="index-table">',
        '<caption>WCAG criterion index: issues and evidence detail</caption>',
        '<thead><tr><th scope="col">Criterion</th><th scope="col">Principle</th><th scope="col">Title</th>'
        '<th scope="col">Issues</th><th scope="col">Full evidence</th><th scope="col">Metadata-only</th></tr></thead><tbody>',
    ]
    for criterion in sorted(groups):
        info = criterion_info(criterion)
        group = groups[criterion]
        full = sum(1 for item in group if item.get("evidence_status") != "inventory")
        inventory = len(group) - full
        section_id = "sc-" + criterion.replace(".", "-")
        principle = {
            "1": "Perceivable", "2": "Operable", "3": "Understandable", "4": "Robust",
        }.get(criterion[:1], "Other")
        parts.append(
            f'<tr><th scope="row"><a href="#{section_id}">{esc(criterion)}</a></th>'
            f'<td>{esc(principle)}</td><td>{esc(info["title"])}</td>'
            f'<td>{len(group)}</td><td>{full}</td><td>{inventory}</td></tr>'
        )
    parts.extend(["</tbody></table></div>"])
    return "".join(parts)


def _issue_index(findings):
    parts = [
        '<h3 id="issue-index-heading">Issue index</h3>',
        '<p>Compact scan of every finding. The complete evidence for each issue follows in the same order; '
        'links go to its canonical anchor.</p>',
        '<div class="table-scroll" tabindex="0" role="region" aria-label="Issue index. Scroll horizontally if needed.">',
        '<table class="index-table issue-index">',
        '<caption>Issue index: identity, component, criteria, status, applicability and evidence detail</caption>',
        '<thead><tr><th scope="col">Issue</th><th scope="col">Component</th><th scope="col">WCAG criteria</th>'
        '<th scope="col">Tracker status</th><th scope="col">Release applicability</th><th scope="col">Evidence</th>'
        '<th scope="col">Merge requests</th></tr></thead><tbody>',
    ]
    for finding in sorted(findings, key=lambda item: item.get("issue_id") or ""):
        anchor = anchor_for(finding["issue_id"])
        criteria = ", ".join(finding.get("wcag_candidates") or []) or "Untagged"
        evidence = "Metadata-only" if finding.get("evidence_status") == "inventory" else "Full"
        mrs = len(finding.get("merge_requests") or [])
        parts.append(
            f'<tr><th scope="row"><a href="#{anchor}">{esc(finding["issue_id"])}</a><br>'
            f'<span class="meta">{esc(finding.get("title") or "")}</span></th>'
            f'<td>{esc(finding.get("component") or "Not recorded")}</td>'
            f'<td>{esc(criteria)}</td>'
            f'<td>{esc(finding.get("tracker_status_label") or "Unknown")}</td>'
            f'<td>{esc(app_label(finding.get("applicability")))}</td>'
            f'<td>{esc(evidence)}</td><td>{mrs}</td></tr>'
        )
    parts.append("</tbody></table></div>")
    return "".join(parts)


def _metric_grid(rows):
    parts = ['<dl class="metric-grid">']
    for label, value, note in rows:
        parts.append(
            f'<div><dt>{esc(label)}</dt><dd>{esc(value)}'
            f'<span class="metric-note">{esc(note)}</span></dd></div>'
        )
    parts.append("</dl>")
    return "".join(parts)


def _section_nav(items):
    return (
        '<nav class="section-nav" aria-label="Report sections"><h2>On this page</h2><ol>'
        + "".join(f'<li><a href="#{esc(anchor)}">{esc(label)}</a></li>' for anchor, label in items)
        + "</ol></nav>"
    )


def _report_actions(target_id):
    return (
        '<section class="report-actions" aria-labelledby="report-actions-heading">'
        '<h2 id="report-actions-heading">Supporting outputs</h2><ul>'
        f'<li><a href="./{esc(target_id)}/evidence.json">evidence.json</a></li>'
        f'<li><a href="./{esc(target_id)}/summary.json">summary.json</a></li>'
        f'<li><a href="./{esc(target_id)}/openacr.yaml">OpenACR draft YAML</a></li>'
        f'<li><a href="./{esc(target_id)}/openacr-validation.json">validation result</a></li>'
        f'<li><a href="./{esc(target_id)}/acr.html">ACR draft</a></li>'
        "</ul><p class=\"meta\">The ACR is a draft derived from this evidence, not an approved conformance report.</p></section>"
    )


def render_landing(analyses, output_dir, targets_config=None):
    """Render the multi-target landing page and cross-release matrix.

    The page is static and has no script. The release finder uses CSS-only radio
    filters; all releases remain in the document and are visible without CSS
    filtering support. The full matrix stays in a disclosure with a real table.
    """
    analyses = list(analyses)
    if not analyses:
        raise ValueError("At least one analysis is required")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    targets_config = targets_config or {}
    policy = targets_config.get("policy") or {}
    product = targets_config.get("product") or analyses[0]["target"].get("product") or "Product"
    first_target = analyses[0]["target"]
    css_href = f"./{first_target['assessment_id']}/report.css"
    generated = max((analysis.get("generated_at") or "") for analysis in analyses)
    issue_titles = {}
    full = inventory = 0
    with_mrs = 0
    for analysis in analyses:
        collection_summary = (analysis.get("collection") or {}).get("summary") or {}
        full = max(full, int(collection_summary.get("detailed") or 0))
        inventory = max(inventory, int(collection_summary.get("inventory") or 0))
        with_mrs = max(with_mrs, int(collection_summary.get("with_merge_requests") or 0))
        for finding in analysis.get("findings") or []:
            issue_titles.setdefault(finding["issue_id"], finding.get("title") or finding["issue_id"])
    issue_ids = sorted(issue_titles)
    finder_html, line_css = _release_finder(analyses)

    html = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="description" content="Draft release-scoped accessibility evidence across Drupal Core release lines. Not Accessibility Conformance Reports.">',
        '<meta name="robots" content="noindex">',
        f"<title>{esc(product)} release evidence reports</title>",
        f'<link rel="stylesheet" href="{esc(css_href)}">',
        f"<style>{line_css}</style>",
        "</head>",
        "<body>",
        '<a class="skip" href="#main">Skip to main content</a>',
        '<header class="page-header">',
        '<p class="eyebrow">OpenACR Release Evidence</p>',
        f"<h1>{esc(product)} release evidence reports</h1>",
        '<p class="lede">Automatically generated accessibility evidence from Drupal Core issue queues, '
        'release metadata, and available development records. Explore issues by release, accessibility '
        'requirement, or component.</p>',
        '<p class="status-banner"><strong>These reports summarize collected evidence.</strong> '
        'They are not accessibility scores or verified conformance assessments. '
        'Closed and fixed issues are excluded; absence of a reported issue is not evidence of WCAG support.</p>',
        f'<dl class="snapshot-meta" aria-label="Evidence snapshot metadata">'
        f'<div><dt>Generated</dt><dd>{esc(display_date(generated))}</dd></div>'
        f'<div><dt>Release targets</dt><dd>{esc(len(analyses))}</dd></div>'
        f'<div><dt>Unique active issues</dt><dd>{esc(len(issue_ids))}</dd></div>'
        f'<div><dt>Full evidence</dt><dd>{esc(full)}</dd></div>'
        f'<div><dt>Metadata-only</dt><dd>{esc(inventory)}</dd></div>'
        f'<div><dt>Issues with merge requests</dt><dd>{esc(with_mrs)}</dd></div>'
        f'<div><dt>Collection source</dt><dd>Drupal.org issue queue</dd></div>'
        f'<div><dt>Standards baseline</dt><dd>WCAG 2.2 AA · Section 508</dd></div>'
        "</dl>",
        "</header>",
        '<main id="main" tabindex="-1">',
    ]
    # Release finder and cards
    html.append('<section aria-labelledby="targets-heading">')
    html.append('<h2 id="targets-heading">Find a release report</h2>')
    if policy.get("note"):
        html.append(f'<p>{esc(policy["note"])}</p>')
    if policy.get("source_url"):
        html.append(f'<p class="meta">Release policy: {safe_link(policy["source_url"], "Drupal core release cycle schedule")}. '
                    "Support status is a policy label, not a promise about a specific release.</p>")
    html.append(finder_html)
    html.append('<h3 id="release-list-heading">Release reports</h3>')
    html.append('<ul class="target-list" aria-labelledby="release-list-heading">')
    for analysis in analyses:
        html.append(_target_card(analysis))
    html.append("</ul>")
    html.append('<p class="meta">Targets marked pre-release or development are not supported releases. '
                'Their findings can change at any commit and must not be presented as release conformance claims.</p>')
    html.append("</section>")

    # Position: explain the difference from a periodic vendor ACR.
    html.append('<section id="position" aria-labelledby="position-heading"><h2 id="position-heading">Why this ACR is different</h2>')
    html.append('<p>Most vendor ACRs are periodic, sample-based snapshots reviewed by legal or product management; the vendor issue queue is separate and can remain open after the report is signed. This site publishes an issue-queue attestation generated from the full active Drupal Core Accessibility queue and regenerated weekly. Every cited issue stays linked to its public discussion.</p>')
    html.append('<ul><li><strong>Stronger on known-report completeness and traceability.</strong> Every active queue item is represented and linked, not just a page sample.</li><li><strong>Stronger on recency and backlog connection.</strong> New issues and status changes appear in the next snapshot.</li><li><strong>Weaker on independent manual coverage.</strong> This is not a WCAG-EM evaluation, not an independent audit and not a certification. A missing tagged issue is not evidence of support.</li></ul>')
    html.append('<p class="meta"><a href="https://github.com/mgifford/openacr-release-evidence/blob/main/docs/ACR-POSITION.md">Read the full position</a> · <a href="https://github.com/GSA/openacr/issues/180">GSA OpenACR issue #180</a> · <a href="https://www.drupal.org/docs/getting-started/accessibility/accessibility-conformance-report-acr-process">Drupal ACR process</a>.</p>')
    html.append("</section>")

    # ATAG
    atag_dir = output / "drupal-core-atag"
    if (atag_dir / "index.html").exists():
        html.append('<section aria-labelledby="atag-heading"><h2 id="atag-heading">ATAG 2.0 authoring evidence</h2>')
        html.append('<p>Drupal Core is also an authoring tool. ATAG-tagged issues are tracked separately from the WCAG release matrix; '
                    'ATAG and WCAG results are not inherited from each other. The ATAG report separates Part A (authoring tool UI accessibility) '
                    'from Part B (support for producing accessible content) and exports a WAI ATAG Report Tool JSON draft.</p>')
        html.append('<p><a href="./drupal-core-atag/">Open the ATAG 2.0 authoring evidence</a> · '
                    '<a href="./drupal-core-atag/atag-report.json">WAI ATAG Report Tool JSON</a> · '
                    '<a href="./drupal-core-atag/atag-evidence.json">atag-evidence.json</a></p>')
        html.append("</section>")

    # Matrix preview + full disclosure
    preview_count = min(12, len(issue_ids))
    html.append('<section aria-labelledby="matrix-heading"><h2 id="matrix-heading">Cross-release applicability matrix</h2>')
    html.append('<p>Each cell links to the issue-specific finding in that target report. A fix may be included in one target and absent from another; '
                'the table does not claim that an issue was reproduced on any target.</p>')
    html.append('<p class="meta">The preview shows the first 12 issues. The complete matrix remains available in a real data table below. '
                'At narrow widths the table scrolls horizontally; focus the table region and use arrow keys or horizontal scrolling.</p>')
    html.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Cross-target applicability matrix preview. Scroll horizontally to compare targets.">')
    html.append(_matrix_table(
        issue_ids[:preview_count], issue_titles, analyses,
        f"Preview: first {preview_count} of {len(issue_ids)} issues across {len(analyses)} declared {product} targets. "
        "Values are evidence states, not WCAG conformance results.",
    ))
    html.append("</div>")
    html.append(f'<p><a class="primary-action" href="./matrix.html">Open the complete {len(issue_ids)}-issue matrix</a></p>')
    html.append('<p class="meta">The complete matrix is a separate page so this release overview stays scannable; '
                'it contains every issue and every target as a real data table.</p>')
    html.append("</section>")

    html.append('<section aria-labelledby="responsibility-heading"><h2 id="responsibility-heading">Project responsibility and parent ACRs</h2>')
    html.append('<p>Drupal Core is the top-level product in this snapshot. Themes, recipes and distributions can publish '
                'their own ACRs and point to a parent Core ACR, which makes responsibility visible without copying Core '
                'conclusions into a downstream product. In particular, Claro and Olivero are core themes in the 10.x/11.x '
                'targets and contributed projects in the 12.x targets; they should have separate ACRs that reference the '
                'matching Core release rather than being silently folded into Core.</p>')
    html.append('<p class="meta">The current pipeline records a <code>parent_project</code> field and displays it, but it '
                'does not yet collect contributed-project queues or generate parent-linked ACRs. Drupal CMS and LocalGov '
                'Drupal need their own manifests, Composer locks and parent references.</p>')
    html.append("</section>")

    html.append('<section aria-labelledby="what-heading"><h2 id="what-heading">What this site publishes</h2>')
    html.append('<p>Only an explicit allowlist is deployed: this landing page, each report HTML and stylesheet, '
                '<code>evidence.json</code>, <code>summary.json</code>, the ACR draft, the OpenACR draft files '
                'and the ATAG evidence files. Raw CLI responses, private evidence snapshots, <code>collection.json</code> '
                'and <code>analysis.json</code> are not published.</p>')
    html.append("</section>")

    html.append('<section aria-labelledby="limits-heading"><h2 id="limits-heading">Limitations</h2><ul>')
    html.append('<li>The report covers active review-relevant Accessibility-tagged issues, not every barrier. Closed and fixed issues are excluded; some active issues are metadata-only inventory records.</li>')
    html.append('<li>No issue in this snapshot was reproduced against an installed target. Commit inclusion is not '
                'behavioural verification, and a closed issue is not proof of a release fix.</li>')
    html.append('<li>The generic <code>Admin theme</code> component is shared across release lines with different '
                'admin themes (Claro in 10.6/12 alpha; Default Admin in 11.4/12 beta/main). Reproduce before applying a '
                'finding across a theme boundary.</li>')
    html.append('<li>Pre-release and development targets are not supported releases. Drupal 10.x is expected to reach '
                'end of life when Drupal 12.0.0 is released; verify the current policy.</li>')
    html.append('<li>WCAG tags are candidate relevance signals, not conformance determinations.</li>')
    html.append("</ul></section>")
    html.append("</main>")
    html.append(
        '<footer><p>Draft target evidence. Not an Accessibility Conformance Report. '
        'Standards baseline: WCAG 2.2 AA. '
        '<a href="https://www.w3.org/TR/WCAG22/">WCAG 2.2</a> · '
        '<a href="https://github.com/GSA/openacr">OpenACR</a> · '
        '<a href="https://www.drupal.org/project/drupal/issues">Drupal Core issue queue</a>.</p>'
        '<p class="meta">Issue titles are quoted from public Drupal.org issues with source links and attribution; '
        'they remain subject to Drupal.org terms and are not relicensed under this project\'s MIT licence.</p></footer>'
    )
    html.append("</body></html>")
    (output / "index.html").write_text("\n".join(html) + "\n", encoding="utf-8")

    matrix = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="description" content="Complete cross-release accessibility applicability matrix. Evidence states, not conformance results.">',
        '<meta name="robots" content="noindex">',
        f"<title>{esc(product)} cross-release applicability matrix</title>",
        f'<link rel="stylesheet" href="{esc(css_href)}">',
        "</head>",
        "<body>",
        '<a class="skip" href="#main">Skip to main content</a>',
        '<header class="page-header">',
        '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'
        '<li><a href="./">All release reports</a></li>'
        '<li><span aria-current="page">Cross-release matrix</span></li></ol></nav>',
        '<p class="eyebrow">OpenACR Release Evidence · matrix</p>',
        f"<h1>{esc(product)} cross-release applicability matrix</h1>",
        '<p class="lede">Every unique active issue in this snapshot, compared across the declared release targets. '
        'Each cell links to the target-specific finding.</p>',
        '<p class="status-banner"><strong>Evidence states, not conformance results.</strong> '
        'A fix may be included in one target and absent from another; this table does not claim that an issue was reproduced on any target.</p>',
        f'<p class="meta">Generated {esc(display_date(generated))} · {esc(len(issue_ids))} issues × '
        f'{esc(len(analyses))} targets · <a href="./">Back to release reports</a></p>',
        "</header>",
        '<main id="main" tabindex="-1">',
        '<section aria-labelledby="matrix-heading">',
        '<h2 id="matrix-heading">Issue applicability by target</h2>',
        '<p class="meta">This is a two-dimensional data table. At narrow widths it scrolls horizontally; '
        'focus the table region and use arrow keys or horizontal scrolling.</p>',
        '<div class="table-scroll" tabindex="0" role="region" aria-label="Complete cross-target applicability matrix. Scroll horizontally to compare targets.">',
        _matrix_table(
            issue_ids, issue_titles, analyses,
            f"Issue applicability across {len(analyses)} declared {product} targets. Values are evidence states, not WCAG conformance results.",
        ),
        "</div>",
        "</section>",
        "</main>",
        '<footer><p>Draft target evidence. Not an Accessibility Conformance Report. '
        'Standards baseline: WCAG 2.2 AA. <a href="./">All release reports</a> · '
        '<a href="https://www.w3.org/TR/WCAG22/">WCAG 2.2</a> · '
        '<a href="https://github.com/GSA/openacr">OpenACR</a>.</p></footer>',
        "</body></html>",
    ]
    (output / "matrix.html").write_text("\n".join(matrix) + "\n", encoding="utf-8")
    return output / "index.html"
