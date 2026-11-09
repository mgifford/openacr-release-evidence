"""Normalize Drupal.org and GitLab read-only output into a stable evidence schema.

The normalized record is intentionally source-independent at the top level so a
future GitHub or Jira adapter can emit the same shape. Raw upstream responses
are archived separately (private evidence), never merged into the public record.
"""
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from .atag import classify as classify_atag
from .model import (
    SCHEMA_VERSION,
    sha256_json,
    status_label,
    status_workflow,
    valid_public_url,
)

WCAG_TAG_RE = re.compile(r"^wcag(\d+)$", re.IGNORECASE)
ADMIN_PATH_RE = re.compile(r"/admin(?:/|\b)", re.IGNORECASE)
# Drupal's login/account area is /user, including /user/login and /user/1.
# All /user paths are authoring/account surfaces, not front-end web.
USER_PATH_RE = re.compile(r"(?:^|[\s(])/user(?:/[^\s?#)]*)?(?=$|[\s?#)])", re.IGNORECASE)
_SURFACE_POLICY = None


def _surface_policy():
    global _SURFACE_POLICY
    if _SURFACE_POLICY is None:
        _SURFACE_POLICY = {}
        try:
            import json
            path = Path(__file__).resolve().parents[2] / "config" / "surface-policy.json"
            _SURFACE_POLICY = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, ImportError):
            _SURFACE_POLICY = {}
    return _SURFACE_POLICY
LOGIN_RE = re.compile(
    r"\b(?:log\s*in|login|logged\s+in|sign\s*in|signin|administrator|admin\s+user)\b",
    re.IGNORECASE,
)
MACHINE_COMMENT_MARKERS = (
    "created an issue",
    "made their first commit",
    "see original summary",
    "created a merge request",
    "opened a merge request",
)


class _TextExtractor(HTMLParser):
    BLOCK_TAGS = {
        "p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6",
        "section", "article", "header", "footer", "tr", "table", "blockquote", "pre",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip_depth += 1
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip_depth = max(0, self.skip_depth - 1)
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)

    def text(self):
        text = "".join(self.parts).replace("\r\n", "\n").replace("\r", "\n")
        lines = [re.sub(r"[ \t\f\v]+", " ", line).strip() for line in text.split("\n")]
        return "\n".join(line for line in lines if line).strip()


def html_to_text(value):
    """Convert upstream HTML to plain text without executing or trusting it."""
    if not value:
        return ""
    parser = _TextExtractor()
    try:
        parser.feed(str(value))
        parser.close()
        return parser.text()
    except Exception:
        # A malformed fragment must not abort a collection run. A conservative
        # tag strip is better than dropping the source text entirely.
        return re.sub(r"<[^>]+>", " ", str(value)).strip()


def iso_utc(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
        moment = datetime.fromtimestamp(int(value), timezone.utc)
    else:
        moment = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        moment = moment.astimezone(timezone.utc)
    return moment.isoformat(timespec="seconds").replace("+00:00", "Z")


def wcag_from_labels(labels):
    """Map Drupal.org issue tags such as ``wcag143`` to ``1.4.3``.

    Only explicitly tagged criteria are proposed. No text-mining or model
    inference happens here: this is deterministic normalization.
    """
    from .wcag import CRITERIA

    found = []
    for label in labels or []:
        match = WCAG_TAG_RE.match(str(label).strip())
        if not match:
            continue
        digits = match.group(1)
        options = []
        for first in range(1, min(3, len(digits) - 1)):
            for second in range(first + 1, min(4, len(digits))):
                parts = (digits[:first], digits[first:second], digits[second:])
                if not all(1 <= len(part) <= 2 for part in parts):
                    continue
                one, two, three = (int(part) for part in parts)
                if 1 <= one <= 4 and 1 <= two <= 5 and 1 <= three <= 20:
                    options.append(f"{one}.{two}.{three}")
        # Prefer a criterion in the local WCAG catalogue; otherwise keep the
        # single unambiguous numeric split. Never invent a mapping from prose.
        known = [option for option in options if option in CRITERIA]
        if known:
            criterion = known[0]
        elif len(options) == 1:
            criterion = options[0]
        else:
            continue
        if criterion not in found:
            found.append(criterion)
    return sorted(found)


def classify_surface(issue):
    """Classify an issue as authoring or web using explicit evidence.

    Priority: explicit issue override, component mapping, `/admin`, `/user`
    paths, named authoring terms, login/reproduction steps, then web. This is a
    draft classification for review, not a conformance decision.
    """
    issue = issue or {}
    policy = _surface_policy()
    issue_id = issue.get("id") or ""
    override = (policy.get("issue_overrides") or {}).get(issue_id)
    if override in {"web", "authoring"}:
        return {"surface": override, "basis": "issue-override"}
    if issue.get("surface") in {"web", "authoring"}:
        return {"surface": issue["surface"], "basis": issue.get("surface_basis") or "explicit"}

    component = str(issue.get("component") or "").strip().casefold()
    themes = {str(key).casefold(): value for key, value in (policy.get("themes") or {}).items()}
    if component and component in themes:
        return {"surface": themes[component], "basis": f"theme:{component}"}
    authoring_components = {str(value).casefold() for value in policy.get("authoring_components") or []}
    if component and component in authoring_components:
        return {"surface": "authoring", "basis": f"component:{component}"}

    parts = [issue.get("title") or "", issue.get("description_text") or ""]
    for comment in issue.get("comments") or []:
        parts.append(comment.get("body_text") or "")
    text = "\n".join(parts)
    if ADMIN_PATH_RE.search(text):
        return {"surface": "authoring", "basis": "admin-path"}
    if USER_PATH_RE.search(text):
        return {"surface": "authoring", "basis": "user-path"}
    lowered = text.casefold()
    for term in policy.get("authoring_terms") or []:
        if str(term).casefold() in lowered:
            return {"surface": "authoring", "basis": f"term:{term}"}
    if LOGIN_RE.search(text):
        return {"surface": "authoring", "basis": "login-step"}
    return {"surface": "web", "basis": "default-web"}


def _author_url(author_id):
    return f"https://www.drupal.org/user/{author_id}" if author_id else None


def normalize_comment(raw, nid, source_project="drupal"):
    cid = str(raw.get("cid") or raw.get("id") or "")
    body_html = raw.get("body_value") or raw.get("body") or ""
    body_text = html_to_text(body_html)
    author_id = raw.get("author_id") or raw.get("uid")
    lowered = body_text.lower()
    return {
        "id": cid,
        "url": f"https://www.drupal.org/node/{nid}#comment-{cid}" if cid else None,
        "author": raw.get("author_name") or (str(author_id) if author_id else "Unknown"),
        "author_id": str(author_id) if author_id else None,
        "author_url": _author_url(author_id),
        "created_at": iso_utc(raw.get("created") or raw.get("created_at")),
        "body_html": body_html,
        "body_text": body_text,
        "machine_generated": any(marker in lowered for marker in MACHINE_COMMENT_MARKERS),
        "content_hash": sha256_json(raw),
    }


def normalize_merge_request(raw):
    return {
        "iid": raw.get("iid"),
        "url": raw.get("web_url"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "target_branch": raw.get("target_branch"),
        "source_branch": raw.get("source_branch"),
        "head_sha": raw.get("head_sha"),
        "merge_commit_sha": raw.get("merge_commit_sha"),
        "squash_commit_sha": raw.get("squash_commit_sha"),
        "merged_at": iso_utc(raw.get("merged_at")),
        "updated_at": iso_utc(raw.get("updated_at")),
        "author": raw.get("author"),
    }


def normalize_drupal_issue(
    issue,
    node,
    mrs,
    term_names,
    retrieved_at,
    raw_ref,
    adapter="drupalorg-cli",
    cli_version=None,
    evidence_status="full",
):
    """Build a versioned normalized issue from CLI JSON + API node + MR list."""
    node = node or {}
    issue = issue or {}
    mrs = mrs or {}
    nid = str(issue.get("nid") or node.get("nid") or "")
    if not nid:
        raise ValueError("Issue response has no nid")
    project = (
        issue.get("field_project_machine_name")
        or (node.get("field_project") or {}).get("machine_name")
        or "drupal"
    )
    term_ids = [str(term.get("id")) for term in (node.get("taxonomy_vocabulary_9") or []) if term]
    labels = [term_names[tid] for tid in term_ids if tid in term_names]
    status_code = issue.get("field_issue_status", node.get("field_issue_status"))
    try:
        status_code = int(status_code)
    except (TypeError, ValueError):
        pass
    created = issue.get("created_at") or iso_utc(issue.get("created") or node.get("created"))
    updated = issue.get("changed_at") or iso_utc(issue.get("changed") or node.get("changed"))
    url = node.get("url") or f"https://www.drupal.org/project/{project}/issues/{nid}"
    if not valid_public_url(url):
        url = f"https://www.drupal.org/project/{project}/issues/{nid}"
    comments = [
        normalize_comment(comment, nid, source_project=project)
        for comment in (issue.get("comments") or [])
    ]
    merge_requests = [
        normalize_merge_request(mr) for mr in (mrs.get("merge_requests") or [])
    ]
    description_html = (
        ""
        if evidence_status == "inventory"
        else issue.get("body_value") or (node.get("body") or {}).get("value") or ""
    )
    provenance = {
        "source_system": "drupal.org",
        "source_project": project,
        "adapter": adapter,
        "adapter_version": cli_version,
        "retrieved_at": retrieved_at,
        "source_url": url,
        "content_hash": sha256_json({"issue": issue, "node": node, "merge_requests": mrs}),
        "raw_ref": raw_ref,
    }
    atag = classify_atag(
        labels,
        issue.get("field_issue_component") or node.get("field_issue_component"),
        f"drupal:{nid}",
    )
    surface = classify_surface({
        "title": issue.get("title") or node.get("title"),
        "component": issue.get("field_issue_component") or node.get("field_issue_component"),
        "description_text": html_to_text(description_html),
        "comments": comments,
    })
    return {
        "schema_version": SCHEMA_VERSION,
        "id": f"drupal:{nid}",
        "project_scoped_id": f"drupal:{project}:{nid}",
        "source_system": "drupal.org",
        "source_project": project,
        "source_id": nid,
        "url": url,
        "title": issue.get("title") or node.get("title") or "Untitled issue",
        "description_html": description_html,
        "description_text": html_to_text(description_html),
        "labels": labels,
        "status": {
            "code": status_code,
            "label": status_label(status_code),
            "workflow_state": status_workflow(status_code),
            "raw_label": issue.get("status"),
        },
        "created_at": created,
        "updated_at": updated,
        "component": issue.get("field_issue_component")
        or node.get("field_issue_component"),
        "version": issue.get("field_issue_version")
        or node.get("field_issue_version"),
        "priority": issue.get("priority"),
        "category": issue.get("category"),
        "evidence_status": evidence_status,
        "comments": comments,
        "merge_requests": merge_requests,
        "wcag_candidates": wcag_from_labels(labels),
        "atag": atag,
        "surface": surface,
        "provenance": provenance,
    }
