"""Drupal.org public REST adapter.

Discovery, issue detail, comments and tag resolution are read-only and preserve
the upstream values. Release applicability is never inferred here.
"""
import time
from urllib.parse import quote, urlencode

from .http import fetch_json

# Drupal.org project node IDs are stable but are not machine names. Resolve
# additional projects explicitly when their IDs are confirmed; do not guess.
KNOWN_PROJECT_IDS = {
    "drupal": "3060",
    "drupal_cms": "3466967",
    "localgov": "3154243",
}


def _as_timestamp(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
        return int(value)
    from datetime import datetime, timezone

    moment = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return int(moment.timestamp())


def _field(value):
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, dict):
        return value.get("value") or value.get("name") or value.get("machine_name") or value.get("id")
    return value


def find_issues(
    project="drupal",
    project_id=None,
    tag_tid="1101",
    statuses=None,
    component=None,
    since=None,
    limit=20,
    page=0,
):
    """List project issues, newest-changed first.

    Drupal.org's API supports project and taxonomy filters. Status, component
    and date filtering is applied locally so multiple values and explicit
    "unknown" handling stay deterministic.
    """
    project_id = project_id or KNOWN_PROJECT_IDS.get(project)
    if not project_id:
        raise ValueError(f"Unknown Drupal project id for {project!r}; supply project_id")
    params = {
        "type": "project_issue",
        "field_project": str(project_id),
        "limit": str(max(1, min(int(limit), 50))),
        "page": str(max(0, int(page))),
        "sort": "changed",
        "direction": "DESC",
    }
    if tag_tid:
        params["taxonomy_vocabulary_9"] = str(tag_tid)
    if statuses and len(statuses) == 1:
        params["field_issue_status"] = str(statuses[0])
    url = "https://www.drupal.org/api-d7/node.json?" + urlencode(params)
    payload = fetch_json(url)
    nodes = payload.get("list", [])
    since_ts = _as_timestamp(since)
    result = []
    for node in nodes:
        if statuses and int(node.get("field_issue_status", -1)) not in {int(s) for s in statuses}:
            continue
        if component and str(node.get("field_issue_component", "")).casefold() != str(component).casefold():
            continue
        if since_ts is not None and int(node.get("changed", 0)) < since_ts:
            continue
        result.append(node)
    return result


def get_node(nid):
    if not str(nid).isdigit():
        raise ValueError("Drupal issue IDs must be numeric")
    return fetch_json(f"https://www.drupal.org/api-d7/node/{quote(str(nid))}.json")


def get_term(tid):
    if not str(tid).isdigit():
        raise ValueError("Drupal taxonomy term IDs must be numeric")
    return fetch_json(f"https://www.drupal.org/api-d7/taxonomy_term/{quote(str(tid))}.json")


def resolve_terms(node, cache=None):
    """Resolve the terms attached to a node, preserving the upstream names."""
    cache = cache if cache is not None else {}
    names = {}
    for term in node.get("taxonomy_vocabulary_9") or []:
        tid = str(term.get("id"))
        if tid not in cache:
            cache[tid] = get_term(tid).get("name")
        names[tid] = cache[tid]
    return names


def fetch_comments(nid, limit=50, page=0):
    """Fallback comment reader; the preferred path uses drupalorg-cli JSON."""
    if not str(nid).isdigit():
        raise ValueError("Drupal issue IDs must be numeric")
    params = {"node": str(nid), "limit": str(max(1, min(int(limit), 100))), "page": str(page)}
    payload = fetch_json("https://www.drupal.org/api-d7/comment.json?" + urlencode(params))
    return payload.get("list", [])


def fetch_issues(project, ids, delay=1.0):
    """Legacy explicit-ID reader retained for compatibility and experiments."""
    result = []
    if not project or any(not str(i).isdigit() for i in ids):
        raise ValueError("Drupal issue IDs must be numeric")
    for index, issue_id in enumerate(ids):
        if index:
            time.sleep(delay)
        data = get_node(issue_id)
        name = (data.get("field_project") or [{}])
        if not isinstance(name, list):
            name = [name]
        machine_names = [v.get("machine_name") for v in name if isinstance(v, dict)]
        if machine_names and project not in machine_names:
            raise ValueError(f"Issue {issue_id} belongs to a different Drupal project")
        body = data.get("body", {})
        if isinstance(body, dict):
            body = body.get("und", body)
        if isinstance(body, list):
            body = body[0] if body else {}
        description = body.get("value", "") if isinstance(body, dict) else ""
        result.append({
            "source": "drupal", "id": str(issue_id),
            "url": f"https://www.drupal.org/project/{quote(project)}/issues/{issue_id}",
            "title": data.get("title", "Untitled Drupal issue"),
            "description": description[:10000],
            "status": str(_field(data.get("field_issue_status")) or "unknown"),
            "updated_at": str(data.get("changed", "")),
            "raw_version": _field(data.get("field_issue_version")),
            "component": _field(data.get("field_issue_component")),
            "wcag_candidates": []
        })
    return result
