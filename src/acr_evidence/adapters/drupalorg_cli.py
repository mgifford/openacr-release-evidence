"""Read-only bridge to mglaman/drupalorg-cli.

The CLI owns Drupal.org versus GitLab-work-item detection. Preserve CLI output
as PRIVATE evidence, not as conformance assertions or public HTML.

Verified against drupalorg-cli 0.15.0 on 2026-11-07. Important corrections over
the first prototype:
- ``issue:show`` supports ``--format=json`` and ``--with-comments``;
- ``mr:list`` defaults to *opened* MRs, so evidence collection must pass
  ``--state=all`` or merged/closed MRs are silently missed.
"""
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

MAX_OUTPUT_BYTES = 2_000_000
SAFE_REF = re.compile(
    r"^(?:[0-9]+|(?:project/)?[a-zA-Z0-9_-]+#[0-9]+|https://git\.drupalcode\.org/project/[a-zA-Z0-9_/-]+/-/work_items/[0-9]+)$"
)
SAFE_PROJECT = re.compile(r"^[a-zA-Z0-9_-]+$")
SAFE_COMMIT = re.compile(r"^[0-9a-fA-F]{7,40}$")

READ_COMMANDS = frozenset({
    "issue:show",
    "issue:search",
    "mr:list",
    "mr:show",
    "mr:diff",
    "mr:files",
    "mr:logs",
    "project:releases",
    "project:release-notes",
    "project:contains",
    "project:issues",
})

# Only these options may be passed through to the CLI. Unknown flags are
# rejected rather than trusted, because command arguments may be influenced by
# issue references.
ALLOWED_FLAG_PATTERNS = (
    re.compile(r"^--with-comments$"),
    re.compile(r"^--include-bot-comments$"),
    re.compile(r"^--state=(all|opened|closed|merged)$"),
    re.compile(r"^--limit=\d{1,3}$"),
    re.compile(r"^--core=[a-zA-Z0-9_.-]+$"),
    re.compile(r"^--category=(bug|task|feature|support|plan)$"),
    re.compile(r"^--status=(all|open|closed|rtbc|review)$"),
    re.compile(r"^--no-cache$"),
)


class DrupalOrgCliError(RuntimeError):
    pass


def _validate_flags(flags):
    for flag in flags or []:
        if not isinstance(flag, str) or not any(p.match(flag) for p in ALLOWED_FLAG_PATTERNS):
            raise ValueError("Unsafe or unsupported Drupal CLI option")


def run_read(
    command,
    arguments,
    flags=None,
    format="llm",
    timeout=60,
    runner=subprocess.run,
    binary="drupalorg",
):
    """Allowlist commands and capture output; never shell out through a shell."""
    if command not in READ_COMMANDS:
        raise ValueError("Only read-only Drupal.org commands are permitted")
    if format not in {"json", "llm", "text", "md"}:
        raise ValueError("Unsupported Drupal CLI output format")
    if any(not isinstance(a, str) or a.startswith("-") for a in arguments):
        raise ValueError("Unsafe or unexpected command argument")
    _validate_flags(flags)
    if not shutil.which(binary) and runner is subprocess.run:
        raise DrupalOrgCliError("drupalorg executable not found; see docs/DRUPALORG-CLI.md")
    argv = [binary, command, *arguments, *(flags or []), f"--format={format}"]
    try:
        result = runner(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DrupalOrgCliError(f"Drupal CLI invocation failed: {type(exc).__name__}") from exc
    if result.returncode != 0:
        raise DrupalOrgCliError(
            f"Drupal CLI {command} returned exit code {result.returncode}; {result.stderr[:300]}"
        )
    content = result.stdout
    if len(content.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise DrupalOrgCliError("CLI output exceeds safety limit")
    if not content.strip():
        raise DrupalOrgCliError("CLI returned empty output")
    record = {
        "command": command,
        "arguments": arguments,
        "flags": flags or [],
        "format": format,
        "content": content,
    }
    if format == "json":
        try:
            record["json"] = json.loads(content)
        except ValueError as exc:
            raise DrupalOrgCliError("Drupal CLI returned invalid JSON") from exc
    return record


def _default_binary(binary=None):
    return binary or os.environ.get("ACR_DRUPALORG_BIN") or "drupalorg"


class DrupalOrgCli:
    """Small typed facade used by the ingestion pipeline and tests."""

    def __init__(self, binary=None, runner=subprocess.run, timeout=60):
        self.binary = _default_binary(binary)
        self.runner = runner
        self.timeout = timeout
        self._version = None

    def version(self):
        if self._version is not None:
            return self._version
        if not shutil.which(self.binary) and self.runner is subprocess.run:
            raise DrupalOrgCliError("drupalorg executable not found")
        try:
            result = self.runner(
                [self.binary, "--version"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise DrupalOrgCliError(f"Could not read drupalorg version: {type(exc).__name__}") from exc
        self._version = (result.stdout or "").strip().splitlines()[0] if result.stdout else ""
        return self._version

    def issue_show(self, reference, with_comments=True):
        flags = ["--with-comments"] if with_comments else []
        return run_read(
            "issue:show", [reference], flags=flags, format="json",
            timeout=self.timeout, runner=self.runner, binary=self.binary,
        )["json"]

    def mr_list(self, reference, state="all"):
        return run_read(
            "mr:list", [reference], flags=[f"--state={state}"], format="json",
            timeout=self.timeout, runner=self.runner, binary=self.binary,
        )["json"]

    def mr_show(self, reference, iid):
        if not str(iid).isdigit():
            raise ValueError("Merge request IID must be numeric")
        return run_read(
            "mr:show", [reference, str(iid)], format="json",
            timeout=self.timeout, runner=self.runner, binary=self.binary,
        )["json"]


def collect_issue(reference, include_mrs=True, runner=subprocess.run, binary=None, with_comments=True):
    """Archive an issue, its comments and all MR states as a private snapshot."""
    if not SAFE_REF.fullmatch(reference):
        raise ValueError("Reference must be Drupal NID or supported GitLab work-item reference")
    cli = DrupalOrgCli(binary=binary, runner=runner)
    try:
        version = cli.version()
    except DrupalOrgCliError:
        version = None
    issue = run_read(
        "issue:show", [reference], flags=["--with-comments"] if with_comments else [],
        format="json", runner=runner, binary=cli.binary,
    )
    commands = [issue]
    warnings = []
    merge_requests = None
    if include_mrs:
        try:
            mr_record = run_read(
                "mr:list", [reference], flags=["--state=all"], format="json",
                runner=runner, binary=cli.binary,
            )
            commands.append(mr_record)
            merge_requests = mr_record["json"]
        except DrupalOrgCliError as exc:
            warnings.append(f"MR listing unavailable: {exc}")
    return {
        "source": "drupalorg-cli",
        "reference": reference,
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cli_version": version,
        "commands": commands,
        "issue": issue["json"],
        "merge_requests": merge_requests,
        "warnings": warnings,
        "review_status": "raw-unreviewed",
        "release_applicability": "unknown",
    }


def collect_releases(project, runner=subprocess.run, binary=None):
    if not SAFE_PROJECT.fullmatch(project):
        raise ValueError("Invalid Drupal project machine name")
    return run_read(
        "project:releases", [project], format="json",
        runner=runner, binary=_default_binary(binary),
    )["json"]


def save_private_snapshot(path, record):
    """Create a new private snapshot, never overwriting historical evidence."""
    target = Path(path)
    resolved = target.resolve()
    parts = [part.casefold() for part in resolved.parts]
    if any(part == "site" or part == "public" or part.startswith("public-") for part in parts):
        raise ValueError("Raw issue snapshots must not be placed in a public directory")
    target.parent.mkdir(parents=True, exist_ok=True)
    # O_EXCL closes the check-then-write race; the mode applies at creation.
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    return target
