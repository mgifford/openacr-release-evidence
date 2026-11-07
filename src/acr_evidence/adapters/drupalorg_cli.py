"""Read-only bridge to mglaman/drupalorg-cli.

The CLI owns Drupal.org versus GitLab-work-item detection. Preserve CLI output
as PRIVATE evidence, not as conformance assertions or public HTML.
"""
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

MAX_OUTPUT_BYTES = 2_000_000
SAFE_REF = re.compile(r"^(?:[0-9]+|(?:project/)?[a-zA-Z0-9_-]+#[0-9]+|https://git\.drupalcode\.org/project/[a-zA-Z0-9_/-]+/-/work_items/[0-9]+)$")
SAFE_PROJECT = re.compile(r"^[a-zA-Z0-9_-]+$")
SAFE_COMMIT = re.compile(r"^[0-9a-fA-F]{7,40}$")


class DrupalOrgCliError(RuntimeError):
    pass


def run_read(command, arguments, binary="drupalorg", timeout=60, runner=subprocess.run):
    """Allowlist commands and capture output; never shell out through a shell."""
    if command not in {"issue:show", "mr:list", "project:releases", "project:contains", "project:issues", "mr:show", "mr:status"}:
        raise ValueError("Only read-only Drupal.org commands are permitted")
    if any(not isinstance(a, str) or a.startswith("-") for a in arguments):
        raise ValueError("Unsafe or unexpected command argument")
    if not shutil.which(binary) and runner is subprocess.run:
        raise DrupalOrgCliError("drupalorg executable not found; see docs/DRUPALORG-CLI.md")
    argv = [binary, command, *arguments, "--format=llm"]
    try:
        result = runner(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DrupalOrgCliError(f"Drupal CLI invocation failed: {type(exc).__name__}") from exc
    if result.returncode != 0:
        raise DrupalOrgCliError(f"Drupal CLI {command} returned exit code {result.returncode}; {result.stderr[:300]}")
    content = result.stdout
    if len(content.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise DrupalOrgCliError("CLI output exceeds safety limit")
    if not content.strip():
        raise DrupalOrgCliError("CLI returned empty output")
    return {"command": command, "arguments": arguments, "format": "llm", "content": content}


def collect_issue(reference, include_mrs=True, runner=subprocess.run, binary="drupalorg"):
    if not SAFE_REF.fullmatch(reference):
        raise ValueError("Reference must be Drupal NID or supported GitLab work-item reference")
    commands = [run_read("issue:show", [reference], binary=binary, runner=runner)]
    # MRs may be absent or unavailable. Preserve that uncertainty explicitly.
    warnings = []
    if include_mrs:
        try:
            commands.append(run_read("mr:list", [reference], binary=binary, runner=runner))
        except DrupalOrgCliError as exc:
            warnings.append(f"MR listing unavailable: {exc}")
    return {
        "source": "drupalorg-cli",
        "reference": reference,
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commands": commands,
        "warnings": warnings,
        "review_status": "raw-unreviewed",
        "release_applicability": "unknown",
    }


def collect_releases(project, runner=subprocess.run, binary="drupalorg"):
    if not SAFE_PROJECT.fullmatch(project):
        raise ValueError("Invalid Drupal project machine name")
    return run_read("project:releases", [project], binary=binary, runner=runner)


def save_private_snapshot(path, record):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError("Refusing to overwrite historical Drupal evidence snapshot")
    # Caller must not place snapshots under a published site directory.
    if "site" in target.parts or "public" in target.parts:
        raise ValueError("Raw issue snapshots must not be placed in a public directory")
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        target.chmod(0o600)
    except OSError:
        pass
