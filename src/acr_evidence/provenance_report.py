"""Derive issue-to-component provenance from merge-request changed paths.

This is deterministic source evidence: a public merge request names the files it
changes, and those paths map to a module, theme or profile. It is still not a
release reproduction and does not change applicability or conformance.
"""
import json
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .adapters.http import fetch_json
from .collect import atomic_write_json
from .model import SCHEMA_VERSION, digest_artifact
from .provenance import ASSOCIATION_LEVELS, associate_issue

GITLAB_PROJECT = "project/drupal"
GITLAB_API = (
    "https://git.drupalcode.org/api/v4/projects/"
    + urllib.parse.quote(GITLAB_PROJECT, safe="")
)
CACHE_TTL_SECONDS = 6 * 60 * 60


def _parse_time(value):
    if not value:
        return None
    try:
        moment = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def _cache_path(cache_dir, iid):
    return Path(cache_dir) / "mr-changes" / f"{int(iid)}.json"


def _core_paths(payload):
    paths = set()
    for change in payload.get("changes") or []:
        for key in ("old_path", "new_path"):
            value = change.get(key)
            if isinstance(value, str) and value.startswith("core/"):
                paths.add(value)
    return sorted(paths)


def fetch_merge_request_changes(
    iid,
    *,
    cache_dir=".cache/acr-evidence",
    refresh=False,
    now=None,
    fetcher=None,
):
    """Return public MR metadata and changed core paths, using a short cache."""
    now = now or datetime.now(timezone.utc)
    path = _cache_path(cache_dir, iid)
    if path.exists() and not refresh:
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
            retrieved = _parse_time(cached.get("retrieved_at"))
            if retrieved and (now - retrieved).total_seconds() < CACHE_TTL_SECONDS:
                return cached
        except (OSError, ValueError):
            pass
    url = f"{GITLAB_API}/merge_requests/{int(iid)}/changes"
    live = fetcher is None
    fetcher = fetcher or fetch_json
    try:
        payload = fetcher(url)
    except Exception as exc:
        return {
            "iid": int(iid),
            "retrieved_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "error": type(exc).__name__,
            "changed_paths": [],
        }
    if live:
        time.sleep(0.2)
    record = {
        "iid": int(iid),
        "state": payload.get("state"),
        "title": payload.get("title"),
        "web_url": payload.get("web_url"),
        "retrieved_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "changed_paths": _core_paths(payload),
    }
    atomic_write_json(path, record)
    return record


def _known_components(inventory_dir):
    known = set()
    for path in sorted(Path(inventory_dir).glob("drupal-core-*.json")):
        try:
            inventory = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for item in inventory.get("components") or []:
            if item.get("type") in ("module", "theme", "profile"):
                known.add((item["type"], item["machine_name"]))
    return known


def build_artifact(
    collection,
    *,
    inventory_dir="data/component-inventory",
    cache_dir=".cache/acr-evidence",
    refresh=False,
    now=None,
    fetcher=None,
):
    """Build one shared provenance artifact from normalized issues and MRs."""
    now = now or datetime.now(timezone.utc)
    known = _known_components(inventory_dir)
    issues = []
    by_level = {}
    changed_issues = 0
    mr_count = 0
    errors = []
    for issue in collection.get("issues") or []:
        mrs = issue.get("merge_requests") or []
        if not mrs:
            continue
        changed = []
        mr_records = []
        for merge_request in mrs:
            iid = merge_request.get("iid")
            if not iid:
                continue
            mr_count += 1
            record = fetch_merge_request_changes(
                iid, cache_dir=cache_dir, refresh=refresh, now=now, fetcher=fetcher
            )
            if record.get("error"):
                errors.append({"issue_id": issue.get("id"), "iid": iid, "error": record["error"]})
            changed.extend(record.get("changed_paths") or [])
            mr_records.append(record)
        changed = sorted(set(changed))
        if changed:
            changed_issues += 1
        association = associate_issue(
            issue,
            changed_paths=changed,
            known_components=known,
        )
        level = association["level"]
        by_level[level] = by_level.get(level, 0) + 1
        issues.append({
            "issue_id": issue.get("id"),
            "source_url": issue.get("url"),
            "title": issue.get("title"),
            "tracker_component": issue.get("component"),
            "merge_requests": mr_records,
            "changed_paths": changed,
            "associations": association["associations"],
            "primary": association["primary"],
            "multiple": association["multiple"],
            "level": level,
            "note": association["note"],
        })
    issues.sort(key=lambda item: item.get("issue_id") or "")
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "issue-component-provenance",
        "disclaimer": (
            "Source-code association from public merge-request file paths. "
            "This is not release applicability, a reproduction or a conformance result."
        ),
        "generated_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "method": (
            "GitLab merge-request changes API; only public core/ file paths are retained. "
            "Associations ignore test-only paths so a test edit does not assign the issue "
            "to every module it touches. Raw diffs and file contents are not stored."
        ),
        "sources": {
            "collection_digest": collection.get("evidence_digest"),
            "gitlab_project": f"https://git.drupalcode.org/{GITLAB_PROJECT}",
        },
        "summary": {
            "issues_with_merge_requests": len(issues),
            "merge_requests": mr_count,
            "issues_with_changed_paths": changed_issues,
            "by_level": dict(sorted(by_level.items())),
            "errors": errors,
            "levels": list(ASSOCIATION_LEVELS),
        },
        "issues": issues,
        "digest_scope": "sha256 over this artifact excluding generated_at and evidence_digest",
    }
    artifact["evidence_digest"] = digest_artifact(artifact)
    return artifact


def apply_target(artifact, target, inventory):
    """Return a target-scoped copy with component presence flags."""
    components = {
        (item.get("type"), item.get("machine_name")): item
        for item in (inventory or {}).get("components") or []
    }
    issues = []
    for issue in artifact.get("issues") or []:
        associations = []
        for association in issue.get("associations") or []:
            key = (association.get("type"), association.get("component"))
            item = components.get(key)
            enriched = dict(association)
            enriched["present_in_bundled_release"] = bool(item)
            enriched["installed_by_standard_profile"] = bool(
                item and item.get("installed_by_standard_profile")
            )
            associations.append(enriched)
        issues.append({**issue, "associations": associations})
    target_artifact = {
        **artifact,
        "target": {
            "assessment_id": target.get("id"),
            "product": target.get("product") or (inventory or {}).get("source", {}).get("product"),
            "release": target.get("release") or target.get("ref"),
            "ref": target.get("ref"),
            "inventory_ref": (inventory or {}).get("source", {}).get("ref"),
        },
        "issues": issues,
    }
    target_artifact["evidence_digest"] = digest_artifact(target_artifact)
    return target_artifact


def write_target_artifacts(artifact, targets_config, output_dir, inventory_dir="data/component-inventory"):
    """Write one `issue-provenance.json` per declared target."""
    output = Path(output_dir)
    written = []
    for target in targets_config.get("targets") or []:
        release = target.get("ref")
        inventory_path = Path(inventory_dir) / f"drupal-core-{release}.json"
        try:
            inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            inventory = {}
        target_artifact = apply_target(artifact, target, inventory)
        destination = output / target["id"] / "issue-provenance.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(target_artifact, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(destination)
    return written
