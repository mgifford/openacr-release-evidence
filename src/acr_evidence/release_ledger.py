"""Cross-release fix ledger for recently closed Accessibility issues.

This is deliberately separate from the active-issue ACR. A closed issue in the
ledger does not change any active criterion result; it explains whether the fix
is present in a newer release line and not in the selected target.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .release import annotate_commits, build_commit_index
from .model import SCHEMA_VERSION

AUTHORING_THEME_KEYS = ("olivero", "claro", "default_admin")


def _iso_from_epoch(value):
    try:
        return datetime.fromtimestamp(int(value), timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    except (TypeError, ValueError, OSError):
        return None


def collect_closed_issues(find_issues_func, project, project_id, tag_tid="1101", since=None, max_pages=20):
    """Collect recently changed closed-fixed Accessibility issues."""
    nodes = {}
    page = 0
    while page < max_pages:
        batch = find_issues_func(
            project=project, project_id=project_id, tag_tid=tag_tid,
            statuses=[7], since=since, limit=50, page=page,
        )
        if not batch:
            break
        for node in batch:
            nodes[str(node.get("nid"))] = node
        if len(batch) < 50:
            break
        page += 1
    return list(nodes.values())


def _removed_for_target(component, release_line, release_changes):
    info = (release_changes.get("release_lines") or {}).get(str(release_line)) or {}
    removed = {str(item).casefold() for item in info.get("removed") or []}
    name = str(component or "").casefold().strip()
    if name.endswith(" theme"):
        name = name[:-6].strip()
    return name in removed


def build_ledger(closed_nodes, targets, commit_index, release_changes=None, annotate=annotate_commits, since=None):
    """Build a deterministic transition ledger from closed nodes and commits."""
    release_changes = release_changes or {}
    by_issue = commit_index.get("by_issue") or {}
    target_order = [target["id"] for target in targets]
    tag_cache = {}
    branch_cache = {}
    entries = []
    for node in sorted(closed_nodes, key=lambda item: int(item.get("nid") or 0)):
        nid = str(node.get("nid"))
        commits = by_issue.get(nid, [])
        target_states = {}
        annotated = {}
        for target in targets:
            target_commits = annotate(
                commits, target.get("ref"), ref_type=target.get("ref_type") or "tag",
                tag_cache=tag_cache, branch_cache=branch_cache,
            )
            annotated[target["id"]] = target_commits
            if _removed_for_target(node.get("field_issue_component"), target.get("release_line"), release_changes):
                state = "removed"
            elif any(commit.get("in_target") for commit in target_commits):
                state = "included"
            elif target_commits:
                state = "not-included"
            else:
                state = "not-established"
            target_states[target["id"]] = state
        included = [target_id for target_id in target_order if target_states.get(target_id) == "included"]
        entries.append({
            "issue_id": f"drupal:{nid}",
            "source_id": nid,
            "source_url": f"https://www.drupal.org/node/{nid}",
            "title": node.get("title") or f"Drupal issue {nid}",
            "component": node.get("field_issue_component") or "Not recorded",
            "closed_at": _iso_from_epoch(node.get("changed")),
            "commits": [
                {
                    "sha": commit.get("sha"),
                    "title": commit.get("title"),
                    "web_url": commit.get("web_url"),
                    "tags": commit.get("tags") or [],
                    "branches": commit.get("branches") or [],
                    "targets": {
                        target["id"]: bool(next(
                            (item.get("in_target") for item in annotated.get(target["id"], [])
                             if item.get("sha") == commit.get("sha")),
                            False,
                        ))
                        for target in targets
                    },
                }
                for commit in commits
            ],
            "targets": target_states,
            "included_in": included,
            "backport_state": (
                "included" if included else
                "removed" if any(state == "removed" for state in target_states.values()) else
                "not-included" if any(state == "not-included" for state in target_states.values()) else
                "not-established"
            ),
        })
    summary = {}
    for state in ("included", "not-included", "not-established", "removed"):
        summary[state] = sum(1 for entry in entries if entry["backport_state"] == state)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "drupal-release-transition-ledger",
        "disclaimer": "Closed-fixed issue ledger only. It does not change active-issue ACR results.",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "since": since,
        "target_order": target_order,
        "targets": [
            {"id": target["id"], "release": target.get("release"), "release_line": target.get("release_line")}
            for target in targets
        ],
        "release_notes": "https://www.drupal.org/project/drupal/releases",
        "summary": {"issues": len(entries), **summary},
        "issues": entries,
    }


def write_ledger(ledger, output):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def collect_and_build_ledger(
    find_issues_func, project, project_id, targets_config, release_changes, output,
    tag_tid="1101", since=None, cache_dir=".cache/acr-evidence", refresh=False,
):
    since = since or (datetime.now(timezone.utc) - timedelta(days=180)).isoformat(timespec="seconds").replace("+00:00", "Z")
    closed = collect_closed_issues(find_issues_func, project, project_id, tag_tid=tag_tid, since=since)
    targets = targets_config.get("targets") or []
    branches = sorted({branch for target in targets for branch in target.get("branches") or []})
    cache_path = Path(cache_dir) / "commits" / "release-ledger.json"
    index = build_commit_index(branches, since=since, cache_path=cache_path, refresh=refresh)
    ledger = build_ledger(closed, targets, index, release_changes=release_changes, since=since)
    write_ledger(ledger, output)
    return ledger
