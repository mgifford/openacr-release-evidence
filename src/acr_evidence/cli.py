"""Command line interface for release-scoped accessibility evidence.

No command produces a conformance decision. ``collect`` gathers evidence,
``analyze`` applies documented applicability rules, and ``report`` renders an
accessible draft artifact for human review.
"""
import argparse
import json
from pathlib import Path

from .build import build
from .collect import collect_issues
from .git_release import commit_in_ref
from .atag import load_scope, render_atag_report
from .openacr import export_worksheet
from .openacr_export import OpenACRError, export_openacr, validate_file
from .release import analyze_collection
from .report import render_landing, render_report
from .adapters.drupal import fetch_issues as fetch_drupal
from .adapters.drupalorg_cli import collect_issue, collect_releases, save_private_snapshot


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path, obj):
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _split_ids(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _split_ints(value):
    if not value:
        return None
    return [int(item) for item in _split_ids(value)]


def _query_from_args(args, manifest):
    """Let a target manifest carry its reproducible collection configuration."""
    config = manifest.get("collection") or {}

    def pick(value, key, default=None):
        return value if value not in (None, "") else config.get(key, default)

    return {
        "project": pick(args.project, "project", "drupal"),
        "project_id": pick(args.project_id, "project_id"),
        "tag": pick(args.tag, "tag", "Accessibility"),
        "tag_tid": str(pick(args.tag_tid, "tag_tid", "1101")),
        "max_issues": int(pick(args.max_issues, "max_issues", 20)),
        "include_ids": _split_ids(args.ids) if args.ids else list(config.get("include_ids") or []),
        "statuses": _split_ints(args.statuses) if args.statuses else config.get("statuses"),
        "component": pick(args.component, "component"),
        "since": pick(args.since, "since"),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Release-scoped accessibility evidence, never an automated ACR"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="Generate draft evidence and static website from normalized legacy input")
    b.add_argument("--manifest", required=True)
    b.add_argument("--issues", required=True)
    b.add_argument("--output", default="site")

    for cmd in ("fetch-drupal",):
        x = sub.add_parser(cmd, help="Retrieve explicit public issue IDs (legacy REST adapter)")
        x.add_argument("--ids", required=True, help="Comma-separated numeric issue IDs")
        x.add_argument("--output", required=True)
        x.add_argument("--project", required=True)

    c = sub.add_parser("collect-drupal", help="Archive one Drupal.org/GitLab issue and all MR states through drupalorg-cli")
    c.add_argument("--issue", required=True, help="Issue NID or project-scoped GitLab work item reference")
    c.add_argument("--output", required=True, help="Private snapshot filename; must not exist")
    c.add_argument("--no-mrs", action="store_true")

    r = sub.add_parser("drupal-releases", help="Read release listing via drupalorg-cli")
    r.add_argument("--project", required=True)
    r.add_argument("--output", required=True)

    g = sub.add_parser("git-check", help="Check a commit is contained in a local git ref")
    g.add_argument("--repo", required=True)
    g.add_argument("--commit", required=True)
    g.add_argument("--ref", required=True)

    e = sub.add_parser("export-draft", help="Export INCOMPLETE YAML review worksheet, not OpenACR")
    e.add_argument("--evidence", required=True)
    e.add_argument("--output", required=True)

    col = sub.add_parser("collect", help="Collect and normalize Drupal issues with provenance and caching")
    col.add_argument("--manifest", required=True)
    col.add_argument("--project", default=None)
    col.add_argument("--project-id", default=None, help="Drupal.org project node ID (drupal core is 3060)")
    col.add_argument("--tag", default=None, help="Human-readable tag name for the collection record")
    col.add_argument("--tag-tid", default=None, help="Drupal.org taxonomy term ID (Accessibility is 1101)")
    col.add_argument("--max", type=int, default=None, dest="max_issues")
    col.add_argument("--ids", default=None, help="Comma-separated explicit Drupal NIDs for a reproducible sample")
    col.add_argument("--statuses", default=None, help="Comma-separated numeric Drupal status codes")
    col.add_argument("--component", default=None)
    col.add_argument("--since", default=None, help="Only include issues changed since this ISO timestamp")
    col.add_argument("--output", required=True)
    col.add_argument("--raw-dir", default="private-evidence/raw")
    col.add_argument("--cache-dir", default=".cache/acr-evidence")
    col.add_argument("--refresh", action="store_true")

    ana = sub.add_parser("analyze", help="Classify a collection against a Drupal Core release tag")
    ana.add_argument("--collection", required=True)
    ana.add_argument("--manifest", required=True)
    ana.add_argument("--release", required=True)
    ana.add_argument("--branch", default=None)
    ana.add_argument("--branches", default=None, help="Comma-separated branches to index")
    ana.add_argument("--since", default=None)
    ana.add_argument("--output", required=True)
    ana.add_argument("--cache-dir", default=".cache/acr-evidence")
    ana.add_argument("--refresh", action="store_true")

    multi = sub.add_parser("multi", help="Analyze a shared collection against multiple declared targets")
    multi.add_argument("--collection", required=True)
    multi.add_argument("--targets", default="config/drupal-core-targets.json")
    multi.add_argument("--output", required=True)
    multi.add_argument("--cache-dir", default=".cache/acr-evidence")
    multi.add_argument("--refresh", action="store_true")

    atag = sub.add_parser("atag-report", help="Render ATAG 2.0 authoring evidence and a WAI ATAG Report Tool JSON draft")
    atag.add_argument("--collection", required=True)
    atag.add_argument("--output", required=True)
    atag.add_argument("--scope", default=None, help="Optional curated ATAG Part A/B scope JSON")

    oa = sub.add_parser("openacr-export", help="Export and validate a draft OpenACR YAML skeleton")
    oa.add_argument("--analysis", required=True)
    oa.add_argument("--output", required=True)
    oa.add_argument("--catalog", default=None)
    oa.add_argument("--schema", default=None)

    ov = sub.add_parser("openacr-validate", help="Validate an edited OpenACR YAML against the official schema and catalog")
    ov.add_argument("--file", required=True)
    ov.add_argument("--catalog", default=None)
    ov.add_argument("--schema", default=None)
    ov.add_argument("--strict", action="store_true", help="Require a reviewed, non-draft document with populated adherence")

    rep = sub.add_parser("report", help="Render a static, no-JavaScript evidence report")
    rep.add_argument("--analysis", required=True)
    rep.add_argument("--output", required=True)
    rep.add_argument("--css", default=None)

    pipe = sub.add_parser("pipeline", help="Collect, analyze and render in one reproducible run")
    pipe.add_argument("--manifest", required=True)
    pipe.add_argument("--project", default=None)
    pipe.add_argument("--project-id", default=None)
    pipe.add_argument("--tag", default=None)
    pipe.add_argument("--tag-tid", default=None)
    pipe.add_argument("--max", type=int, default=None, dest="max_issues")
    pipe.add_argument("--ids", default=None)
    pipe.add_argument("--statuses", default=None)
    pipe.add_argument("--component", default=None)
    pipe.add_argument("--since", default=None)
    pipe.add_argument("--release", required=True)
    pipe.add_argument("--branch", default=None)
    pipe.add_argument("--branches", default=None)
    pipe.add_argument("--output", required=True)
    pipe.add_argument("--raw-dir", default="private-evidence/raw")
    pipe.add_argument("--cache-dir", default=".cache/acr-evidence")
    pipe.add_argument("--refresh", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "build":
        result = build(load_json(args.manifest), load_json(args.issues), args.output)
        print(f"Wrote {len(result['findings'])} draft evidence findings to {args.output}/")
    elif args.command == "fetch-drupal":
        ids = _split_ids(args.ids)
        if not ids or len(ids) > 100:
            parser.error("Supply between 1 and 100 explicit IDs")
        items = fetch_drupal(args.project, ids)
        save_json(args.output, items)
        print(f"Saved {len(items)} issue records to {args.output}")
    elif args.command == "collect-drupal":
        result = collect_issue(args.issue, include_mrs=not args.no_mrs)
        save_private_snapshot(args.output, result)
        print(f"Saved unreviewed Drupal/GitLab CLI snapshot to {args.output}")
    elif args.command == "drupal-releases":
        result = collect_releases(args.project)
        save_private_snapshot(args.output, result)
        print(f"Saved unreviewed release listing to {args.output}")
    elif args.command == "git-check":
        print(json.dumps(commit_in_ref(args.repo, args.commit, args.ref), indent=2))
    elif args.command == "export-draft":
        export_worksheet(load_json(args.evidence), args.output)
        print(f"Wrote incomplete authoring worksheet to {args.output}; NOT a validated OpenACR")
    elif args.command == "collect":
        manifest = load_json(args.manifest)
        query = _query_from_args(args, manifest)
        artifact = collect_issues(
            manifest, query, args.output,
            raw_dir=args.raw_dir, cache_dir=args.cache_dir, refresh=args.refresh,
        )
        summary = artifact["summary"]
        print(
            f"Collected {summary['collected']} of {summary['requested']} issues "
            f"({summary['cached']} cached, {summary['fetched']} fetched, {summary['failed']} failed) to {args.output}"
        )
    elif args.command == "analyze":
        collection = load_json(args.collection)
        manifest = load_json(args.manifest)
        branches = _split_ids(args.branches) if args.branches else None
        artifact = analyze_collection(
            collection, manifest, args.release,
            branch=args.branch, branches=branches, since=args.since,
            output=args.output, cache_dir=args.cache_dir, refresh=args.refresh,
        )
        summary = artifact["summary"]
        print(
            f"Analyzed {summary['findings']} findings against {args.release}; "
            f"{summary['fix_included_in_release']} fix commits in the release tag. Wrote {args.output}"
        )
    elif args.command == "multi":
        collection = load_json(args.collection)
        targets = load_json(args.targets)
        output = Path(args.output)
        analyses = []
        tag_cache = {}
        branch_cache = {}
        for target in targets.get("targets") or []:
            manifest = load_json(target["manifest"])
            target_dir = output / target["id"]
            artifact = analyze_collection(
                collection,
                manifest,
                release=manifest.get("release"),
                ref=target.get("ref"),
                ref_type=target.get("ref_type", "tag"),
                branches=target.get("branches"),
                support_status=target.get("support_status"),
                release_line=target.get("release_line"),
                parent_project=target.get("parent_project"),
                scope_note=target.get("scope_note"),
                target_id=target.get("id"),
                output=target_dir / "analysis.json",
                cache_dir=args.cache_dir,
                refresh=args.refresh,
                tag_cache=tag_cache,
                branch_cache=branch_cache,
            )
            render_report(artifact, target_dir)
            export_openacr(artifact, target_dir)
            analyses.append(artifact)
        render_landing(analyses, output, targets)
        for artifact in analyses:
            summary = artifact["summary"]
            print(
                f'{artifact["target"]["release"]}: {summary["by_applicability"]} · '
                f'{summary["fix_included_in_target"]} fixes in target'
            )
        print(f"Wrote {len(analyses)} reports and the cross-target matrix to {output}/index.html")
    elif args.command == "atag-report":
        scope = load_scope(args.scope) if args.scope else None
        result = render_atag_report(load_json(args.collection), args.output, scope=scope)
        print(
            f"Wrote ATAG evidence to {result['index']} "
            f"({result['summary']['issues']} ATAG-tagged issues; "
            f"{result['summary']['missing_accessibility_tag']} missing the Accessibility tag)"
        )
    elif args.command == "openacr-export":
        result = export_openacr(
            load_json(args.analysis), args.output,
            catalog_path=args.catalog, schema_path=args.schema,
        )
        print(f"Wrote validated draft OpenACR to {result['yaml']} ({result['validation']})")
    elif args.command == "openacr-validate":
        result = validate_file(
            args.file, catalog_path=args.catalog, schema_path=args.schema, strict=args.strict
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if not result["valid"]:
            raise SystemExit(1)
    elif args.command == "report":
        analysis = load_json(args.analysis)
        render_report(analysis, args.output, css_source=args.css)
        export_openacr(analysis, args.output)
        print(f"Wrote static evidence report and OpenACR draft to {args.output}/")
    elif args.command == "pipeline":
        manifest = load_json(args.manifest)
        output = Path(args.output)
        query = _query_from_args(args, manifest)
        collection = collect_issues(
            manifest, query, output / "collection.json",
            raw_dir=args.raw_dir, cache_dir=args.cache_dir, refresh=args.refresh,
        )
        branches = _split_ids(args.branches) if args.branches else None
        analysis = analyze_collection(
            collection, manifest, args.release,
            branch=args.branch, branches=branches, since=args.since,
            output=output / "analysis.json", cache_dir=args.cache_dir, refresh=args.refresh,
        )
        render_report(analysis, output)
        export_openacr(analysis, output)
        summary = analysis["summary"]
        print(
            f"Pipeline complete: {summary['findings']} findings, "
            f"{summary['fix_included_in_release']} fixes in {args.release}. "
            f"Open {output / 'index.html'}"
        )


if __name__ == "__main__":
    main()
