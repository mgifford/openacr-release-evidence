"""Collect and normalize Drupal issues with caching and failure isolation.

Discovery uses the public Drupal.org REST API (one filtered list request).
Per-issue detail and MR discovery use drupalorg-cli JSON output, including all
MR states. Raw responses are archived privately; the normalized artifact never
contains raw upstream payloads.
"""
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .adapters import drupal as drupal_rest
from .adapters.drupalorg_cli import DrupalOrgCli, DrupalOrgCliError, save_private_snapshot
from .model import (
    ACR_REVIEW_STATUSES,
    SCHEMA_VERSION,
    digest_artifact,
    is_acr_review_status,
    sha256_json,
)
from .normalize import normalize_drupal_issue

DEFAULT_TAG_TID = "1101"  # Drupal.org "Accessibility" term, verified 2026-11-07
DEFAULT_CACHE_TTL_SECONDS = 6 * 60 * 60


def _parse_time(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _fresh(record, ttl, now):
    retrieved = _parse_time(record.get("retrieved_at"))
    if not retrieved:
        return False
    return (now - retrieved).total_seconds() < ttl and bool(record.get("issue")) and bool(record.get("node"))


def _read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def atomic_write_json(path, value, mode=0o600):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        os.chmod(temporary, mode)
        os.replace(temporary, target)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    return target


def _safe_terms(rest, node, cache, warnings):
    try:
        return rest.resolve_terms(node, cache)
    except Exception:
        # Resolve each term independently so one bad taxonomy record does not
        # invalidate the whole issue.
        names = {}
        for term in node.get("taxonomy_vocabulary_9") or []:
            tid = str(term.get("id"))
            try:
                if tid not in cache:
                    cache[tid] = rest.get_term(tid).get("name")
                names[tid] = cache[tid]
            except Exception as exc:
                names[tid] = f"Unknown term {tid}"
                warnings.append(f"Term {tid} unavailable: {type(exc).__name__}")
        return names


def _snapshot_path(raw_dir, nid, retrieved_at):
    stamp = str(retrieved_at).replace(":", "").replace("-", "").replace("+0000", "Z")
    return Path(raw_dir) / f"{nid}-{stamp}.json"


def collect_issues(
    manifest,
    query,
    output,
    raw_dir="private-evidence/raw",
    cache_dir=".cache/acr-evidence",
    refresh=False,
    cache_ttl=DEFAULT_CACHE_TTL_SECONDS,
    cli=None,
    rest=None,
    now=None,
):
    """Collect, normalize and write a collection artifact.

    Returns the artifact. A failure on one issue is recorded and does not
    prevent other issues from being saved.
    """
    rest = rest or drupal_rest
    cli = cli or DrupalOrgCli()
    now = now or datetime.now(timezone.utc)
    project = query.get("project") or "drupal"
    project_id = query.get("project_id") or drupal_rest.KNOWN_PROJECT_IDS.get(project)
    tag_tid = str(query.get("tag_tid") or DEFAULT_TAG_TID)
    include_ids = [str(item) for item in (query.get("include_ids") or []) if str(item).isdigit()]
    max_issues = int(query.get("max_issues") or 5000)
    if include_ids:
        max_issues = min(max_issues, len(include_ids))
    statuses = {int(item) for item in (query.get("statuses") or ACR_REVIEW_STATUSES)}
    detail_ids = {str(item) for item in (query.get("detail_ids") or []) if str(item).isdigit()}
    detail_limit = int(60 if query.get("detail_limit") is None else query.get("detail_limit"))
    max_pages = int(query.get("max_pages") or 200)
    cache_root = Path(cache_dir) / "issues"
    cache_root.mkdir(parents=True, exist_ok=True)
    term_cache = {}
    nodes = {}
    discovered = 0
    errors = []

    # Discovery: explicit IDs are preferred for a reproducible sample. Otherwise
    # page the newest-changed issues matching the configured filter.
    if include_ids:
        for nid in include_ids[:max_issues]:
            try:
                node = rest.get_node(nid)
            except Exception as exc:
                errors.append({"nid": nid, "stage": "discovery", "error": f"{type(exc).__name__}: {exc}"})
                continue
            machine = (node.get("field_project") or {}).get("machine_name")
            if project and machine and machine != project:
                errors.append({"nid": nid, "stage": "discovery", "error": f"Issue belongs to {machine}, not {project}"})
                continue
            nodes[nid] = node
    else:
        # Page the entire queue. Status filtering is applied locally because the
        # Drupal.org API does not reliably apply field_issue_status filters.
        page = 0
        while page < max_pages and len(nodes) < max_issues:
            batch = rest.find_issues(
                project=project,
                project_id=project_id,
                tag_tid=tag_tid,
                statuses=None,
                component=query.get("component"),
                since=query.get("since"),
                limit=min(50, max_issues - len(nodes)),
                page=page,
            )
            if not batch:
                break
            discovered += len(batch)
            for node in batch:
                code = node.get("field_issue_status")
                if statuses and not is_acr_review_status(code):
                    continue
                nodes[str(node.get("nid"))] = node
                if len(nodes) >= max_issues:
                    break
            if len(batch) < 50:
                break
            page += 1

    # Full CLI/comment/MR evidence is expensive at queue scale. Select a
    # review-priority subset for detail; the rest remain complete inventory
    # records with source URL, status, tags and component.
    if detail_ids:
        detail = {nid for nid in nodes if nid in detail_ids}
    else:
        priority = {14: 0, 8: 1, 13: 2, 1: 3, 15: 4}
        ordered = sorted(
            nodes.items(),
            key=lambda item: (
                priority.get(int(item[1].get("field_issue_status") or 0), 9),
                -int(item[1].get("changed") or 0),
            ),
        )
        detail = {nid for nid, _ in ordered[:max(0, detail_limit)]}

    try:
        cli_version = cli.version()
    except Exception:
        cli_version = None

    normalized = []
    cached_count = 0
    fetched_count = 0
    inventory_count = 0
    for nid, node in list(nodes.items())[:max_issues]:
        full_detail = nid in detail
        cache_file = cache_root / f"{nid}.json"
        record = None
        if full_detail and cache_file.exists() and not refresh:
            try:
                candidate = _read_json(cache_file)
                if _fresh(candidate, cache_ttl, now):
                    record = candidate
                    cached_count += 1
            except (OSError, ValueError):
                record = None

        if record is None and not full_detail:
            warnings = []
            term_names = _safe_terms(rest, node, term_cache, warnings)
            retrieved_at = now.isoformat(timespec="seconds").replace("+00:00", "Z")
            record = {
                "nid": nid,
                "retrieved_at": retrieved_at,
                "issue": {},
                "node": node,
                "merge_requests": {},
                "term_names": term_names,
                "warnings": warnings,
                "cli_version": None,
                "evidence_status": "inventory",
            }
            try:
                snapshot = _snapshot_path(raw_dir, nid, retrieved_at)
                save_private_snapshot(snapshot, record)
                record["raw_ref"] = str(snapshot)
            except (FileExistsError, OSError, ValueError) as exc:
                warnings.append(f"Raw inventory snapshot not saved: {exc}")
            inventory_count += 1
        elif record is None:
            warnings = []
            try:
                issue = cli.issue_show(nid)
            except (DrupalOrgCliError, ValueError, OSError) as exc:
                errors.append({"nid": nid, "stage": "issue", "error": f"{type(exc).__name__}: {exc}"})
                continue
            merge_requests = None
            try:
                merge_requests = cli.mr_list(nid)
            except (DrupalOrgCliError, ValueError, OSError) as exc:
                warnings.append(f"MR listing unavailable: {type(exc).__name__}")
            retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            record = {
                "nid": nid,
                "retrieved_at": retrieved_at,
                "issue": issue,
                "node": node,
                "merge_requests": merge_requests,
                "term_names": _safe_terms(rest, node, term_cache, warnings),
                "warnings": warnings,
                "cli_version": cli_version,
                "evidence_status": "full",
            }
            try:
                snapshot = _snapshot_path(raw_dir, nid, retrieved_at)
                save_private_snapshot(snapshot, record)
                record["raw_ref"] = str(snapshot)
            except (FileExistsError, OSError, ValueError) as exc:
                # Raw archival failure must not silently discard provenance.
                warnings.append(f"Raw snapshot not saved: {exc}")
            # Cache after the raw snapshot so raw_ref and warnings persist.
            atomic_write_json(cache_file, record)
            fetched_count += 1
        else:
            warnings = list(record.get("warnings") or [])
            if record.get("evidence_status") == "inventory":
                inventory_count += 1

        try:
            evidence_status = record.get("evidence_status") or "full"
            normalized.append(
                normalize_drupal_issue(
                    record["issue"],
                    record["node"],
                    record.get("merge_requests"),
                    record.get("term_names") or {},
                    record["retrieved_at"],
                    record.get("raw_ref") or str(_snapshot_path(raw_dir, nid, record["retrieved_at"])),
                    adapter="drupal.org-api" if evidence_status == "inventory" else "drupalorg-cli",
                    cli_version=record.get("cli_version") or cli_version,
                    evidence_status=evidence_status,
                )
            )
        except Exception as exc:
            errors.append({"nid": nid, "stage": "normalize", "error": f"{type(exc).__name__}: {exc}"})
            continue

    normalized.sort(key=lambda item: item["id"])
    by_workflow = {}
    by_status = {}
    with_mrs = 0
    with_wcag = 0
    comment_count = 0
    for issue in normalized:
        workflow = issue["status"]["workflow_state"]
        by_workflow[workflow] = by_workflow.get(workflow, 0) + 1
        label = issue["status"]["label"]
        by_status[label] = by_status.get(label, 0) + 1
        if issue["merge_requests"]:
            with_mrs += 1
        if issue["wcag_candidates"]:
            with_wcag += 1
        comment_count += len(issue["comments"])

    retrieved_times = [issue.get("provenance", {}).get("retrieved_at") for issue in normalized]
    retrieved_times = [value for value in retrieved_times if value]
    summary = {
        "requested": len(nodes),
        "retrieved_at": max(retrieved_times) if retrieved_times else now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "collected": len(normalized),
        "cached": cached_count,
        "fetched": fetched_count,
        "failed": len([error for error in errors if error.get("stage") != "discovery"]),
        "with_merge_requests": with_mrs,
        "with_wcag_tags": with_wcag,
        "detailed": len([issue for issue in normalized if issue.get("evidence_status") == "full"]),
        "inventory": len([issue for issue in normalized if issue.get("evidence_status") == "inventory"]),
        "excluded_by_status": max(0, discovered - len(nodes)),
        "statuses": sorted(statuses),
        "comments": comment_count,
        "by_workflow": dict(sorted(by_workflow.items())),
        "by_status": dict(sorted(by_status.items())),
        "errors": errors,
    }
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "drupal-accessibility-evidence-collection",
        "disclaimer": "Collected evidence only; applicability and conformance have not been determined here.",
        "assessment": {k: v for k, v in manifest.items() if k != "applicability_overrides"},
        "generated_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "collection": {
            "query": {**query, "project": project, "project_id": project_id, "tag_tid": tag_tid},
            "cli_version": cli_version,
            "raw_dir": str(raw_dir),
            "cache_dir": str(cache_dir),
            "errors": errors,
        },
        "issues": normalized,
        "summary": summary,
        "manifest_digest": sha256_json(manifest),
        "digest_scope": "sha256 over this artifact excluding generated_at and evidence_digest",
    }
    artifact["evidence_digest"] = digest_artifact(artifact)
    atomic_write_json(output, artifact, mode=0o644)
    return artifact
