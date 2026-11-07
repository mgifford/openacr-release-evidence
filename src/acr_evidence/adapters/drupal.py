"""Drupal.org public issue detail adapter; does not infer release applicability."""
import time
from urllib.parse import quote
from .http import fetch_json


def _field(value):
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, dict):
        return value.get("value") or value.get("name") or value.get("machine_name") or value.get("id")
    return value


def fetch_issues(project, ids, delay=1.0):
    result = []
    if not project or any(not str(i).isdigit() for i in ids):
        raise ValueError("Drupal issue IDs must be numeric")
    for index, issue_id in enumerate(ids):
        if index:
            time.sleep(delay)
        data = fetch_json(f"https://www.drupal.org/api-d7/node/{quote(str(issue_id))}.json")
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
