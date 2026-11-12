"""Deterministic component association for accessibility issues.

The association answers "which component does this issue describe?", not "is
this issue applicable to release X?" and not "does the release conform?".
Changed source paths are the strongest available signal; tracker components
and issue text are weaker and are labelled as such.

An issue may legitimately span several components. The model keeps one issue
identity and records multiple associations instead of duplicating the issue.
"""
import re

ASSOCIATION_LEVELS = (
    "explicit-metadata",
    "verified-source-code",
    "strong-candidate",
    "weak-inferred",
    "unknown",
)

MODULE_PATH_RE = re.compile(r"^core/modules/([a-z0-9_]+)/")
THEME_PATH_RE = re.compile(r"^core/themes/([a-z0-9_]+)/")
PROFILE_PATH_RE = re.compile(r"^core/profiles/([a-z0-9_]+)/")


def component_from_path(path):
    """Map a changed core path to ``(type, machine_name)`` or ``None``.

    Only deterministic path prefixes are used. A path under ``core/lib`` is
    core infrastructure, not a module, and returns ``None`` rather than being
    attributed to a nearby module.
    """
    value = str(path or "").strip().lstrip("./")
    for pattern, kind in (
        (MODULE_PATH_RE, "module"),
        (THEME_PATH_RE, "theme"),
        (PROFILE_PATH_RE, "profile"),
    ):
        match = pattern.match(value)
        if match:
            return kind, match.group(1)
    return None


def _aliases_for(component, component_aliases):
    if not component:
        return []
    values = (component_aliases or {}).get(component)
    if isinstance(values, str):
        values = [values]
    return [value for value in (values or []) if isinstance(value, str) and value.strip()]


def _mentions(text, machine_name):
    if not text or not machine_name:
        return False
    pattern = re.compile(r"(?<![a-z0-9_])" + re.escape(machine_name) + r"(?![a-z0-9_])", re.IGNORECASE)
    return bool(pattern.search(text))


def _association(kind, machine_name, level, basis, evidence):
    return {
        "type": kind,
        "component": machine_name,
        "level": level,
        "basis": basis,
        "evidence": evidence,
    }


def associate_issue(issue, *, changed_paths=None, known_components=None, component_aliases=None):
    """Associate one normalized issue with zero or more components.

    ``issue`` is a normalized collection record. ``changed_paths`` comes from
    merge-request/commit file lists; when absent, the function must not pretend
    that source-code verification happened. ``known_components`` is a set of
    ``(type, machine_name)`` tuples from the target inventory.
    """
    issue_id = issue.get("id") or f"{issue.get('source')}:{issue.get('source_id')}"
    associations = {}
    evidence = []

    def add(kind, machine_name, level, basis, source):
        key = (kind, machine_name)
        existing = associations.get(key)
        if existing is None:
            associations[key] = _association(kind, machine_name, level, basis, [source])
        elif level == "verified-source-code" and existing["level"] != "verified-source-code":
            associations[key] = _association(kind, machine_name, level, basis, [source])
        elif source not in existing["evidence"]:
            existing["evidence"].append(source)

    for path in changed_paths or []:
        found = component_from_path(path)
        if found:
            add(found[0], found[1], "verified-source-code", "changed-path", f"path:{path}")

    tracker_component = str(issue.get("component") or "").strip()
    aliases = _aliases_for(tracker_component, component_aliases)
    if len(aliases) == 1:
        add("component", aliases[0], "explicit-metadata", "tracker-component-alias", f"component:{tracker_component}")

    if known_components:
        for kind, machine_name in sorted(known_components):
            if tracker_component.casefold() == machine_name.casefold():
                add(kind, machine_name, "explicit-metadata", "tracker-component-machine-name", f"component:{tracker_component}")
        title = issue.get("title") or ""
        description = issue.get("description_text") or ""
        for kind, machine_name in sorted(known_components):
            if _mentions(title, machine_name):
                add(kind, machine_name, "strong-candidate", "title-mention", f"title:{machine_name}")
            elif _mentions(description, machine_name):
                add(kind, machine_name, "strong-candidate", "description-mention", f"description:{machine_name}")

    ordered = sorted(associations.values(), key=lambda item: (item["type"], item["component"]))
    primary = None
    if ordered:
        ranking = {level: index for index, level in enumerate(ASSOCIATION_LEVELS)}
        primary = min(ordered, key=lambda item: ranking[item["level"]])
    return {
        "issue_id": issue_id,
        "source_url": issue.get("url"),
        "associations": ordered,
        "primary": primary,
        "multiple": len(ordered) > 1,
        "level": primary["level"] if primary else "unknown",
        "note": (
            "Association is not release applicability. Verified source-code association requires "
            "a changed path from the issue's merge request or commit."
        ),
    }
