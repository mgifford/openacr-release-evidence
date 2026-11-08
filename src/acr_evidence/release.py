"""Release-specific applicability from tracker reports, MRs and git containment.

Git inclusion is evidence about code presence, not proof that a barrier is
behaviourally corrected on an installed release. ``confirmed-fixed`` therefore
records the basis explicitly and leaves the finding unreviewed for a human.
"""
import json
import re
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError

from .adapters.http import fetch_json
from .collect import atomic_write_json
from .model import SCHEMA_VERSION, digest_artifact, sha256_json
from .normalize import classify_surface

GITLAB_PROJECT = "project/drupal"
GITLAB_PROJECT_ENCODED = urllib.parse.quote(GITLAB_PROJECT, safe="")
GITLAB_API = f"https://git.drupalcode.org/api/v4/projects/{GITLAB_PROJECT_ENCODED}"
COMMIT_ISSUE_RE = re.compile(r"#(\d{3,})")
SAFE_SHA = re.compile(r"^[0-9a-fA-F]{7,40}$")
COMMIT_CACHE_TTL_SECONDS = 6 * 60 * 60


class GitLabError(RuntimeError):
    pass


def _get(path, params=None):
    url = GITLAB_API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        return fetch_json(url)
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise GitLabError(f"GitLab {path} failed with HTTP {exc.code}") from exc
    except Exception as exc:
        raise GitLabError(f"GitLab {path} failed: {type(exc).__name__}") from exc


def _parse_time(value):
    if not value:
        return None
    moment = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def branch_for_release(release):
    match = re.match(r"^(\d+)\.(\d+)\.", str(release))
    if not match:
        raise ValueError(f"Cannot infer branch for release {release!r}")
    return f"{match.group(1)}.{match.group(2)}.x"


def get_tag(tag):
    payload = _get(f"/repository/tags/{urllib.parse.quote(str(tag), safe='')}")
    if not payload:
        return None
    commit = payload.get("commit") or {}
    return {
        "name": payload.get("name") or str(tag),
        "tag_commit": commit.get("id"),
        "tag_commit_short": commit.get("short_id"),
        "tag_date": commit.get("created_at"),
        "tag_message": commit.get("title"),
        "release_url": payload.get("release", {}).get("_links", {}).get("self") if payload.get("release") else None,
    }


def get_branch(branch):
    payload = _get(f"/repository/branches/{urllib.parse.quote(str(branch), safe='')}")
    if not payload:
        return None
    commit = payload.get("commit") or {}
    return {
        "name": payload.get("name") or str(branch),
        "commit": commit.get("id"),
        "commit_short": commit.get("short_id"),
        "date": commit.get("created_at"),
        "message": commit.get("title"),
    }


def list_branches():
    payload = _get("/repository/branches", {"per_page": 100})
    return [branch.get("name") for branch in (payload or [])]


def get_commits(branch, since=None, until=None, max_pages=10):
    commits = []
    for page in range(1, max_pages + 1):
        params = {"ref_name": branch, "per_page": 100, "page": page}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        payload = _get("/repository/commits", params)
        if not payload:
            break
        for commit in payload:
            commits.append({
                "sha": commit.get("id"),
                "short_id": commit.get("short_id"),
                "branch": branch,
                "created_at": commit.get("created_at"),
                "title": commit.get("title"),
                "url": commit.get("web_url"),
            })
        if len(payload) < 100:
            break
        time.sleep(0.4)
    return commits


def tags_containing(sha):
    if not SAFE_SHA.match(str(sha)):
        raise ValueError("Invalid git SHA")
    payload = _get(f"/repository/commits/{sha}/refs", {"type": "tag"})
    return [item.get("name") for item in (payload or [])]


def branches_containing(sha):
    if not SAFE_SHA.match(str(sha)):
        raise ValueError("Invalid git SHA")
    payload = _get(f"/repository/commits/{sha}/refs", {"type": "branch"})
    return [item.get("name") for item in (payload or [])]


def path_exists(ref, path):
    payload = _get("/repository/tree", {"ref": ref, "path": path, "per_page": 1})
    return bool(payload)


def _issue_numbers(title):
    return sorted({match.group(1) for match in COMMIT_ISSUE_RE.finditer(title or "")})


def build_commit_index(
    branches,
    since=None,
    until=None,
    cache_path=None,
    refresh=False,
    now=None,
    max_pages=10,
):
    """Fetch and cache recent commits for the target and adjacent branches."""
    now = now or datetime.now(timezone.utc)
    cache_path = Path(cache_path) if cache_path else None
    if cache_path and cache_path.exists() and not refresh:
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            retrieved = _parse_time(cached.get("retrieved_at"))
            if retrieved and (now - retrieved).total_seconds() < COMMIT_CACHE_TTL_SECONDS:
                same_branches = set(branches).issubset(set(cached.get("branches") or []))
                same_window = cached.get("since") == since and cached.get("until") == until
                if same_branches and same_window:
                    return _index_from_commits(cached.get("commits") or [], retrieved.isoformat())
        except (OSError, ValueError):
            pass

    commits = []
    for branch in branches:
        commits.extend(get_commits(branch, since=since, until=until, max_pages=max_pages))
    retrieved_at = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    if cache_path:
        atomic_write_json(cache_path, {
            "retrieved_at": retrieved_at,
            "branches": list(branches),
            "since": since,
            "until": until,
            "commits": commits,
        })
    return _index_from_commits(commits, retrieved_at)


def _index_from_commits(commits, retrieved_at):
    """Deduplicate commits that appear on several branches.

    The same fix is often cherry-picked/merged onto 11.x, 11.5.x and main; the
    evidence should show one commit with several containing branches, not the
    same SHA repeated per branch.
    """
    merged = {}
    for raw in commits:
        commit = dict(raw)
        length = len(commit.get("sha") or "")
        if length < 7:
            continue
        branch = commit.pop("branch", None)
        branches = sorted(set(commit.get("branches") or ([branch] if branch else [])))
        commit["branches"] = branches
        commit["branch"] = branches[0] if branches else branch
        sha = commit["sha"]
        if sha in merged:
            merged[sha]["branches"] = sorted(set(merged[sha]["branches"]) | set(branches))
            merged[sha]["branch"] = merged[sha]["branches"][0] if merged[sha]["branches"] else None
        else:
            commit["issues"] = _issue_numbers(commit.get("title"))
            merged[sha] = commit
    by_issue = {}
    for commit in merged.values():
        for nid in commit["issues"]:
            by_issue.setdefault(nid, []).append(commit)
    ordered = sorted(merged.values(), key=lambda item: item.get("created_at") or "")
    return {"retrieved_at": retrieved_at, "commits": ordered, "by_issue": by_issue}


def annotate_commits(commits, target_ref, ref_type="tag", tag_cache=None, branch_cache=None):
    """Annotate commits with tag/branch containment for a tag or branch target.

    ``in_target`` is the authoritative field. ``in_release`` is retained for
    tag targets so existing report/digest consumers keep their meaning; it is
    always false for a development-branch target.
    """
    tag_cache = tag_cache if tag_cache is not None else {}
    branch_cache = branch_cache if branch_cache is not None else {}
    annotated = []
    for commit in commits:
        record = dict(commit)
        sha = record.get("sha")
        if sha not in tag_cache:
            tag_cache[sha] = tags_containing(sha)
        if sha not in branch_cache:
            branch_cache[sha] = branches_containing(sha)
        record["tags"] = tag_cache[sha]
        record["branches"] = branch_cache[sha]
        if ref_type == "tag":
            record["in_target"] = target_ref in tag_cache[sha]
            record["in_release"] = record["in_target"]
        else:
            record["in_target"] = target_ref in branch_cache[sha]
            record["in_release"] = False
        annotated.append(record)
    return annotated


def _evidence_urls(issue, commits):
    urls = [issue.get("url")]
    for commit in commits:
        urls.append(commit.get("url"))
    for mr in issue.get("merge_requests") or []:
        urls.append(mr.get("url"))
    seen = []
    for url in urls:
        if isinstance(url, str) and url.startswith("https://") and url not in seen:
            seen.append(url)
    return seen


def classify_issue(issue, manifest, target, commits, feature_present=True):
    """Classify one issue against one declared target.

    ``feature_present`` may be True, False, or None. False is only justified by
    code/feature evidence, never by absence of an issue report. A target may be
    a release tag or a development branch; the reason always names the target.
    """
    component = issue.get("component")
    components = {str(item).casefold() for item in (manifest.get("components") or [])}
    in_scope = not components or not component or str(component).casefold() in components
    ref_type = target.get("ref_type") or "tag"
    target_label = target.get("ref_label") or (
        f"tag {target.get('tag')}" if ref_type == "tag" else f"branch {target.get('ref')}"
    )
    included = [
        commit for commit in commits
        if commit.get("in_target", commit.get("in_release"))
    ]
    not_included = [
        commit for commit in commits
        if not commit.get("in_target", commit.get("in_release"))
    ]
    workflow = (issue.get("status") or {}).get("workflow_state") or "unknown"
    surface = issue.get("surface") or classify_surface(issue)
    created_at = _parse_time(issue.get("created_at"))
    target_date = _parse_time(target.get("tag_date") or target.get("target_date"))
    after_release = bool(created_at and target_date and created_at > target_date)
    commit_branches = sorted({
        branch
        for commit in commits
        for branch in (commit.get("branches") or [commit.get("branch")])
        if branch
    })
    included_shas = ", ".join(c.get("short_id") or c.get("sha", "")[:8] for c in included)
    excluded_shas = ", ".join(c.get("short_id") or c.get("sha", "")[:8] for c in not_included)

    if not in_scope:
        applicability = "not-in-scope"
        basis = "manifest-scope"
        reason = (
            f"Component {component!r} is not listed in the assessment target's in-scope components; "
            "it is excluded from this ACR scope. This is not a conformance result."
        )
    elif issue.get("evidence_status") == "inventory":
        applicability = "unknown"
        basis = "inventory-only"
        reason = (
            f"This active issue is included as a complete inventory record for {target_label}, but its comments, "
            "merge requests and commit history were not collected in this snapshot. Review the source issue and "
            "collect detailed evidence before drawing a release conclusion."
        )
    elif feature_present is False:
        applicability = "not-introduced"
        basis = "code-presence"
        reason = (
            f"The affected feature or code is not present in {target_label}; "
            "the defect was never introduced into this target. This must be verified against the installed target."
        )
    elif feature_present is None:
        applicability = "unknown"
        basis = "insufficient-evidence"
        reason = f"Could not establish whether the affected feature or code is present in {target_label}."
    elif included and workflow == "closed-fixed":
        applicability = "confirmed-fixed"
        basis = "git-inclusion"
        if ref_type == "branch":
            reason = (
                f"Fix commit(s) {included_shas} are contained in {target_label}. This is a development-branch "
                "target, not a release claim; behavioural verification is still required."
            )
        else:
            reason = (
                f"Fix commit(s) {included_shas} are contained in {target_label} "
                f"({target.get('tag_commit_short')}). Commit inclusion is not behavioural verification on the "
                "installed release; an independent reviewer must confirm the fix."
            )
    elif commits:
        applicability = "likely-affected"
        basis = "git-non-inclusion"
        reason = (
            f"Fix commit(s) {excluded_shas} were found on {', '.join(commit_branches) or 'a branch'} but are "
            f"not contained in {target_label}. The barrier likely remains in this target; "
            "reproduce it on the installed target before confirming."
        )
    elif workflow == "closed-fixed":
        applicability = "unknown"
        basis = "tracker-closed-without-commit"
        reason = (
            "The tracker marks the issue closed (fixed), but no matching fix commit was found. "
            "Do not infer target applicability from the tracker status alone."
        )
    elif workflow in {"closed-other", "postponed"}:
        applicability = "unknown"
        basis = "closed-non-fix"
        reason = (
            "The tracker is closed for a non-fix reason (or postponed) and no matching target fix was found. "
            "Do not infer that the barrier is present or absent in this target."
        )
    elif after_release:
        applicability = "unknown"
        basis = "report-after-release"
        reason = (
            f"The issue was reported after the target date ({target.get('tag_date') or target.get('target_date')}) "
            f"and no fix was found in {target_label}. It may describe a later regression or a pre-existing barrier; "
            "reproduce on the target before assigning applicability."
        )
    else:
        applicability = "likely-affected"
        basis = "tracker-report"
        reason = (
            f"An open accessibility report exists and no fix commit was found in {target_label}. "
            "This is not a reproduction result; the barrier likely affects the target and requires review."
        )

    finding = {
        "schema_version": SCHEMA_VERSION,
        "assessment_id": target.get("assessment_id") or manifest.get("id"),
        "target": {
            "product": target.get("product"),
            "release": target.get("release"),
            "ref": target.get("ref"),
            "ref_type": ref_type,
            "support_status": target.get("support_status"),
            "release_line": target.get("release_line"),
            "parent_project": target.get("parent_project"),
        },
        "issue_id": issue.get("id"),
        "source_url": issue.get("url"),
        "title": issue.get("title"),
        "component": component,
        "tracker_status": (issue.get("status") or {}).get("code"),
        "tracker_status_label": (issue.get("status") or {}).get("label"),
        "tracker_version": issue.get("version"),
        "evidence_status": issue.get("evidence_status") or "full",
        "created_at": issue.get("created_at"),
        "observed_at": (issue.get("provenance") or {}).get("retrieved_at"),
        "wcag_candidates": issue.get("wcag_candidates") or [],
        "atag": issue.get("atag"),
        "surface": surface,
        "applicability": applicability,
        "basis": basis,
        "reason": reason,
        "fix_included_in_target": bool(included),
        "fix_included_in_release": bool(included) if ref_type == "tag" else False,
        "commits": [
            {
                "sha": commit.get("sha"),
                "short_id": commit.get("short_id"),
                "url": commit.get("url"),
                "branch": commit.get("branch"),
                "branches": commit.get("branches") or [],
                "created_at": commit.get("created_at"),
                "title": commit.get("title"),
                "in_target": bool(commit.get("in_target", commit.get("in_release"))),
                "in_release": bool(commit.get("in_release")),
            }
            for commit in commits
        ],
        "merge_requests": issue.get("merge_requests") or [],
        "evidence_urls": _evidence_urls(issue, commits),
        "review_status": "unreviewed",
        "synthetic": bool(issue.get("synthetic")),
    }
    return finding


def analyze_collection(
    collection,
    manifest,
    release=None,
    branch=None,
    branches=None,
    since=None,
    output=None,
    cache_dir=".cache/acr-evidence",
    refresh=False,
    feature_map=None,
    now=None,
    ref=None,
    ref_type="tag",
    target_id=None,
    support_status=None,
    release_line=None,
    parent_project=None,
    scope_note=None,
    tag_cache=None,
    branch_cache=None,
):
    """Analyze a normalized collection against a release tag or branch target.

    ``ref_type="tag"`` treats containment in the tag as the target condition.
    ``ref_type="branch"`` treats containment in the branch as the target
    condition; the resulting findings describe a development target, not a
    release. Callers should pass target metadata from an explicit policy file.
    """
    now = now or datetime.now(timezone.utc)
    release = release or manifest.get("release")
    ref = ref or release
    if ref_type not in {"tag", "branch"}:
        raise ValueError("ref_type must be 'tag' or 'branch'")
    if ref_type == "tag":
        ref_info = get_tag(ref)
        if not ref_info:
            raise GitLabError(f"Release tag {ref!r} not found in {GITLAB_PROJECT}")
        ref_commit = ref_info.get("tag_commit")
        ref_short = ref_info.get("tag_commit_short")
        ref_date = ref_info.get("tag_date")
        branch = branch or branch_for_release(release)
        ref_label = f"tag {ref}"
        source_url = f"https://git.drupalcode.org/{GITLAB_PROJECT}/-/tags/{ref}"
    else:
        ref_info = get_branch(ref)
        if not ref_info:
            raise GitLabError(f"Branch {ref!r} not found in {GITLAB_PROJECT}")
        ref_commit = ref_info.get("commit")
        ref_short = ref_info.get("commit_short")
        ref_date = ref_info.get("date")
        branch = branch or ref
        ref_label = f"branch {ref}"
        source_url = f"https://git.drupalcode.org/{GITLAB_PROJECT}/-/tree/{ref}"
    target = {
        "assessment_id": target_id or manifest.get("id"),
        "product": manifest.get("product"),
        "release": release,
        "ref": ref,
        "ref_type": ref_type,
        "ref_label": ref_label,
        "tag": ref if ref_type == "tag" else None,
        "branch": branch,
        "tag_commit": ref_commit,
        "tag_commit_short": ref_short,
        "tag_date": ref_date,
        "support_status": support_status or "unknown",
        "release_line": release_line or branch,
        "parent_project": parent_project,
        "scope_note": scope_note,
    }
    if branches is None:
        if ref_type == "branch":
            branches = [ref]
        else:
            match = re.match(r"^(\d+)\.(\d+)\.", str(release))
            if match:
                major, minor = int(match.group(1)), int(match.group(2))
                branches = sorted({branch, "main", "11.x", f"{major}.{minor + 1}.x"})
            else:
                branches = [branch]
    if since is None:
        moment = _parse_time(ref_date) or now
        since = (moment - timedelta(days=180)).isoformat(timespec="seconds").replace("+00:00", "Z")
    safe_ref = re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(ref))
    cache_path = Path(cache_dir) / "commits" / f"{GITLAB_PROJECT.replace('/', '-')}-{ref_type}-{safe_ref}.json"
    index = build_commit_index(
        branches, since=since, cache_path=cache_path, refresh=refresh, now=now,
    )
    findings = []
    tag_cache = tag_cache if tag_cache is not None else {}
    branch_cache = branch_cache if branch_cache is not None else {}
    for issue in collection.get("issues") or []:
        nid = issue.get("source_id")
        if issue.get("evidence_status") == "inventory":
            # Do not spend GitLab API calls or imply commit evidence for
            # metadata-only inventory records.
            commits = []
        else:
            commits = index["by_issue"].get(str(nid), [])
            commits = annotate_commits(
                commits, ref, ref_type=ref_type, tag_cache=tag_cache, branch_cache=branch_cache,
            )
        component = issue.get("component")
        if feature_map is not None and component in feature_map:
            feature_present = feature_map[component]
        else:
            feature_present = True if component and component.casefold() in {
                str(item).casefold() for item in (manifest.get("components") or [])
            } else None
        findings.append(classify_issue(issue, manifest, target, commits, feature_present=feature_present))
    findings.sort(key=lambda item: item.get("issue_id") or "")
    by_applicability = {}
    by_workflow = {}
    by_evidence_status = {}
    for finding in findings:
        by_applicability[finding["applicability"]] = by_applicability.get(finding["applicability"], 0) + 1
        evidence_status = finding.get("evidence_status") or "full"
        by_evidence_status[evidence_status] = by_evidence_status.get(evidence_status, 0) + 1
        workflow = "unknown"
        for issue in collection.get("issues") or []:
            if issue.get("id") == finding["issue_id"]:
                workflow = (issue.get("status") or {}).get("workflow_state") or "unknown"
                break
        by_workflow[workflow] = by_workflow.get(workflow, 0) + 1
    criteria = sorted({criterion for finding in findings for criterion in finding["wcag_candidates"]})
    summary = {
        "findings": len(findings),
        "by_applicability": dict(sorted(by_applicability.items())),
        "by_workflow": dict(sorted(by_workflow.items())),
        "by_evidence_status": dict(sorted(by_evidence_status.items())),
        "fix_included_in_target": sum(1 for finding in findings if finding["fix_included_in_target"]),
        "fix_included_in_release": sum(
            1 for finding in findings
            if ref_type == "tag" and finding["fix_included_in_release"]
        ),
        "needs_verification": sum(
            1 for finding in findings if finding["applicability"] in {"likely-affected", "unknown", "confirmed-fixed"}
        ),
        "unmapped_criteria": sum(1 for finding in findings if not finding["wcag_candidates"]),
        "criteria": criteria,
        "commit_index": {
            "ref": ref,
            "ref_type": ref_type,
            "branches": branches,
            "since": since,
            "commits": len(index["commits"]),
            "retrieved_at": index["retrieved_at"],
        },
    }
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "drupal-release-applicability-draft",
        "disclaimer": (
            "Draft target applicability evidence. Not a WCAG conformance report or certification. "
            "No issue status, commit inclusion or model output establishes conformance."
        ),
        "assessment": {k: v for k, v in manifest.items() if k != "applicability_overrides"},
        "target": target,
        "generated_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "collection": {
            "query": (collection.get("collection") or {}).get("query"),
            "collection_digest": collection.get("evidence_digest"),
            "summary": collection.get("summary"),
            "cli_version": (collection.get("collection") or {}).get("cli_version"),
        },
        "issues": collection.get("issues") or [],
        "findings": findings,
        "summary": summary,
        "sources": {
            "gitlab_project": f"https://git.drupalcode.org/{GITLAB_PROJECT}",
            "target": source_url,
            "commit_index": index["retrieved_at"],
        },
        "manifest_digest": sha256_json(manifest),
        "digest_scope": "sha256 over this artifact excluding generated_at and evidence_digest",
    }
    artifact["evidence_digest"] = digest_artifact(artifact)
    if output:
        atomic_write_json(output, artifact, mode=0o644)
    return artifact
