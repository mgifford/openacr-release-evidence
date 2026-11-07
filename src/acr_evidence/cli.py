"""Command line interface for the initial evidence prototype."""
import argparse
import json
from pathlib import Path
from .build import build
from .git_release import commit_in_ref
from .openacr import export_worksheet
from .adapters.drupal import fetch_issues as fetch_drupal
from .adapters.drupalorg_cli import collect_issue, collect_releases, save_private_snapshot


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Release-scoped accessibility evidence, never an automated ACR")
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="Generate draft evidence and static website")
    b.add_argument("--manifest", required=True)
    b.add_argument("--issues", required=True)
    b.add_argument("--output", default="site")
    for cmd in ("fetch-drupal",):
        x = sub.add_parser(cmd, help="Retrieve explicit public issue IDs")
        x.add_argument("--ids", required=True, help="Comma-separated numeric issue IDs")
        x.add_argument("--output", required=True)
        x.add_argument("--project", required=True)
    c = sub.add_parser("collect-drupal", help="Archive Drupal.org/GitLab issue and MR details through drupalorg-cli")
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
    args = parser.parse_args(argv)
    if args.command == "build":
        result = build(load_json(args.manifest), load_json(args.issues), args.output)
        print(f"Wrote {len(result['findings'])} draft evidence findings to {args.output}/")
    elif args.command == "fetch-drupal":
        ids = [item.strip() for item in args.ids.split(",") if item.strip()]
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


if __name__ == "__main__":
    main()
