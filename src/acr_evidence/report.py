"""Render a static, no-JavaScript evidence report.

All upstream text is escaped. The report is intentionally usable without
JavaScript, from a GitHub Pages repository subpath, and at 320 CSS pixels.
"""
import json
import shutil
from html import escape
from pathlib import Path

from .wcag import APPLICABILITY_LABELS, APPLICABILITY_MEANINGS, criterion_info

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
        "<caption>Tracker workflow states among the selected issues. Tracker status is not release applicability.</caption>",
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
        _facts([
            ("Release applicability", f'<strong>{esc(app_label(finding["applicability"]))}</strong>'),
            ("Why", esc(finding.get("reason"))),
            ("Evidence basis", esc(finding.get("basis"))),
            ("Fix included in release?", "Yes" if finding.get("fix_included_in_release") else "No"),
            ("Tracker status (not release status)", esc(finding.get("tracker_status_label") or "Unknown")),
            ("Version field at last fetch", esc(finding.get("tracker_version") or "Not recorded")),
            ("Component", esc(finding.get("component") or "Not recorded")),
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
    if issue:
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
        return "<p>No findings require further verification in this sample.</p>"
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


def render_report(analysis, output_dir, css_source=None):
    """Write index.html, report.css, evidence.json and summary.json."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    assessment = analysis.get("assessment") or {}
    target = analysis.get("target") or {}
    summary = analysis.get("summary") or {}
    collection = analysis.get("collection") or {}
    findings = analysis.get("findings") or []
    issues = {issue.get("id"): issue for issue in (analysis.get("issues") or [])}
    synthetic = bool(assessment.get("synthetic"))
    standard = ", ".join(assessment.get("standards") or []) or "Not recorded"
    installation = assessment.get("installation") or {}
    enabled_themes = installation.get("enabled_themes") or {}
    theme_text = ", ".join(f"{key}: {value}" for key, value in enabled_themes.items()) or "Not recorded"
    title = (
        f"{assessment.get('product', 'Product')} {target.get('release', assessment.get('release', ''))} "
        "accessibility evidence — draft"
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
        ("Git tag", esc(target.get("tag") or assessment.get("ref"))),
        ("Tag commit", f'{esc(target.get("tag_commit_short") or "Not resolved")}'
                       f' <span class="meta">{esc(target.get("tag_commit") or "")}</span>'),
        ("Tag date", esc(display_date(target.get("tag_date")))),
        ("Assessment identifier", esc(assessment.get("id"))),
        ("Assessment date", esc(display_date(analysis.get("generated_at")))),
        ("Standards baseline", esc(standard)),
        ("Profile", esc(installation.get("profile") or "Not recorded")),
        ("Drupal Core version", esc(installation.get("drupal_core_version") or "Not recorded")),
        ("Composer lock SHA-256", esc(installation.get("composer_lock_sha256") or "Not recorded")),
        ("Enabled themes", esc(theme_text)),
        ("In-scope components", esc(", ".join(assessment.get("components") or []) or "Not recorded")),
        ("Configuration note", esc(installation.get("configuration") or "Not recorded")),
        ("Collection source", "Drupal.org REST API for discovery and tags; drupalorg-cli JSON for issues, comments and all MR states"),
        ("Collection timestamp", esc((collection.get("summary") or {}).get("retrieved_at") or analysis.get("generated_at"))),
        ("Issues collected", esc(len(issues))),
        ("Comments captured", esc((collection.get("summary") or {}).get("comments", "Not recorded"))),
        ("Issues with merge requests", esc((collection.get("summary") or {}).get("with_merge_requests", "Not recorded"))),
        ("Issues with WCAG tags", esc((collection.get("summary") or {}).get("with_wcag_tags", "Not recorded"))),
        ("Findings", esc(len(findings))),
        ("Fix commits included in tag", esc(summary.get("fix_included_in_release", 0))),
        ("Findings needing verification", esc(summary.get("needs_verification", 0))),
    ]

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
        '<p class="eyebrow">OpenACR Release Evidence</p>',
        f"<h1>{esc(title)}</h1>",
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
    html.append(
        '<nav aria-label="On this page"><h2 class="visually-hidden">On this page</h2><ul>'
        '<li><a href="#scope">Assessment scope</a></li>'
        '<li><a href="#summary">Evidence summary</a></li>'
        '<li><a href="#criteria">WCAG criterion evidence</a></li>'
        '<li><a href="#issues">Issue evidence</a></li>'
        '<li><a href="#gaps">Verification gaps</a></li>'
        '<li><a href="#method">Method and limitations</a></li>'
        '<li><a href="#provenance">Provenance</a></li>'
        "</ul></nav>"
    )
    html.append('<main id="main" tabindex="-1">')
    html.append('<section id="scope" aria-labelledby="scope-heading"><h2 id="scope-heading">Assessment scope</h2>')
    html.append('<p>This report describes one declared assessment target. It is not a statement about every Drupal installation, '
                'configuration or release.</p>')
    html.append(_facts(rows))
    html.append("</section>")
    html.append('<section id="summary" aria-labelledby="summary-heading"><h2 id="summary-heading">Evidence summary</h2>')
    html.append('<p><strong>This is not an accessibility score.</strong> The table counts evidence states for the selected issues. '
                'A low issue count does not mean the release is accessible; a high count does not prove a conformance failure.</p>')
    html.append(_summary_table(findings))
    html.append(_status_table(findings))
    html.append(
        f'<p class="meta">{esc(summary.get("findings", 0))} findings · '
        f'{esc(summary.get("fix_included_in_release", 0))} fix commits contained in the release tag · '
        f'{esc(summary.get("unmapped_criteria", 0))} findings without a WCAG criterion tag · '
        f'{esc(summary.get("needs_verification", 0))} need further verification.</p>'
    )
    html.append("</section>")
    html.append('<section id="criteria" aria-labelledby="criteria-heading"><h2 id="criteria-heading">WCAG criterion evidence</h2>')
    html.append('<p>Criteria are grouped from explicit Drupal.org tags such as <code>wcag143</code>. '
                'Tags are candidate evidence, not conformance results. Issues without a criterion tag are listed separately.</p>')
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
    html.append('<p>Each issue retains its source URL, tracker status, observation time, candidate criteria and release-specific reasoning. '
                'Raw upstream responses are kept privately and are not published here.</p>')
    for finding in sorted(findings, key=lambda item: item.get("issue_id") or ""):
        html.append(_issue_article(finding, issues.get(finding.get("issue_id"))))
    html.append("</section>")
    html.append('<section id="gaps" aria-labelledby="gaps-heading"><h2 id="gaps-heading">Verification gaps</h2>')
    html.append('<p>These are the findings that need reproduction, testing or independent review before an ACR statement can rely on them.</p>')
    html.append(_gaps(findings))
    html.append('<p>No issue in this report was reproduced against an installed Drupal 11.4.12 site in this phase. '
                'No screen-reader, keyboard, zoom or forced-colors testing of the assessed release is claimed.</p>')
    html.append("</section>")
    html.append('<section id="method" aria-labelledby="method-heading"><h2 id="method-heading">Method and limitations</h2>')
    html.append("<ol>"
                "<li>Selected Drupal Core issues explicitly tagged <em>Accessibility</em> (taxonomy term 1101) and, for this controlled sample, an explicit list of issue IDs covering open, fixed and not-yet-released cases.</li>"
                "<li>Retrieved each issue, its public comments and every merge request state through drupalorg-cli JSON output. Merged and closed MRs are included; the earlier prototype requested only opened MRs.</li>"
                "<li>Built a commit index for the target release branch and adjacent development branches, matched commit messages to issue IDs, and checked whether each commit is contained in the release tag using the public GitLab API.</li>"
                "<li>Applied documented classification rules. A tracker report is not a reproduction; commit inclusion is not behavioural verification; a closed issue is not proof of a release fix.</li>"
                "<li>Did not use AI, did not infer conformance and did not assign a percentage or score.</li>"
                "</ol>")
    html.append('<p class="meta">Discovery and tag resolution use the public Drupal.org API. Git containment uses '
                'git.drupalcode.org. The in-scope configuration intentionally enables the Default Admin theme; the standard '
                'profile in Drupal 11.4.12 uses Claro and Olivero, so this is a declared configuration rather than the stock default.</p>')
    html.append('<h3>Limitations</h3><ul>'
                '<li>The sample is purposive, not exhaustive. Only issues carrying the Accessibility tag were considered. '
                'The absence of a reported issue is not evidence of WCAG support.</li>'
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
                '<a href="./evidence.json">evidence.json</a> and '
                '<a href="./summary.json">summary.json</a>.</p>')
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
        json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
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
    return output
