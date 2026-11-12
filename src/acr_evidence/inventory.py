"""Deterministic component inventory for a Drupal Core source tree.

The inventory answers three different questions separately:

* **bundled** - what ships in the release archive;
* **installed by the standard profile** - what the stock profile enables,
  including dependency closure;
* **default** - which installed themes the profile sets as default and admin.

It deliberately does not infer contributed lineage. A removed theme is absent
from a later inventory; whether its code moved to a contributed project is a
separate, curated relationship record. See :mod:`acr_evidence.lineage`.

No third-party YAML parser is used. Drupal ``.info.yml`` files are shallow, and
a small parser keeps the pipeline dependency-free and the extraction auditable.
"""
import json
import re
from pathlib import Path

from .model import digest_artifact, sha256_json

SCHEMA_VERSION = "1.0.0"
ARTIFACT_TYPE = "drupal-component-inventory"
EXTENSION_TYPES = ("module", "theme")
STATUSES = ("stable", "experimental", "deprecated", "obsolete", "unknown")

TOP_LEVEL_KEY_RE = re.compile(r"^([A-Za-z0-9_ -]+):\s*(.*)$")
LIST_ITEM_RE = re.compile(r"^\s+-\s*(.+)$")
DEPENDENCY_RE = re.compile(r"^(?:drupal:)?([a-z0-9_]+)")


def _strip_comment(value):
    """Remove a trailing YAML comment from an unquoted scalar."""
    if value[:1] in ("'", '"'):
        quote = value[0]
        end = value.find(quote, 1)
        return value[1:end] if end > 0 else value[1:]
    marker = value.find(" #")
    return value[:marker].rstrip() if marker >= 0 else value


def parse_info_yml(text):
    """Parse the shallow top-level keys of a Drupal ``.info.yml`` file.

    Supports scalar values and simple block sequences (``install:``,
    ``themes:``, ``dependencies:``). Nested maps are ignored because they carry
    no inventory identity. Unknown constructs are skipped rather than guessed.
    """
    data = {}
    current_key = None
    for raw in (text or "").splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            match = LIST_ITEM_RE.match(line)
            if match and current_key and isinstance(data.get(current_key), list):
                data[current_key].append(_strip_comment(match.group(1).strip()))
            continue
        match = TOP_LEVEL_KEY_RE.match(line)
        if not match:
            continue
        key = match.group(1).strip()
        value = _strip_comment(match.group(2).strip())
        if value == "":
            data[key] = []
        else:
            data[key] = value
        current_key = key
    return data


def _bool(value):
    return str(value).strip().lower() in ("true", "1", "yes")


def _normalise_base_theme(value):
    text = str(value or "").strip()
    if not text or text.casefold() in ("false", "none"):
        return None
    return text


def extension_status(info):
    """Return a normalised lifecycle status and the basis for it."""
    lifecycle = str(info.get("lifecycle") or "").strip().lower()
    if lifecycle:
        return (lifecycle if lifecycle in STATUSES else "unknown"), "lifecycle"
    for key in ("experimental",):
        if _bool(info.get(key)):
            return "experimental", key
    package = str(info.get("package") or "")
    if "experimental" in package.casefold():
        return "experimental", "package-label"
    return "stable", "no-lifecycle-field"


def _dependency_names(info):
    names = []
    for dependency in info.get("dependencies") or []:
        match = DEPENDENCY_RE.match(str(dependency).strip())
        if match:
            names.append(match.group(1))
    return sorted(set(names))


def _read_info(path):
    try:
        return parse_info_yml(path.read_text(encoding="utf-8"))
    except OSError:
        return None


def _discover(root, base, kind):
    """Return ``{machine_name: (path, info)}`` for direct children only."""
    found = {}
    directory = root / base
    if not directory.is_dir():
        return found
    for child in sorted(directory.iterdir()):
        if not child.is_dir():
            continue
        if kind == "profile" and child.name == "tests":
            # Test-only profiles are not part of the shipped profile set.
            continue
        info_path = child / f"{child.name}.info.yml"
        info = _read_info(info_path)
        if info is None or str(info.get("type") or kind) != kind:
            continue
        if kind == "profile" and _bool(info.get("hidden")):
            # Test-only profiles are bundled code but not a shipped profile choice.
            continue
        found[child.name] = (info_path, info)
    return found


def _closure(roots, components):
    seen = set()
    stack = [str(item) for item in roots]
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        if name not in components:
            continue
        seen.add(name)
        stack.extend(_dependency_names(components[name]))
    return seen


def _theme_config(root, profile):
    candidates = [
        root / "core" / "profiles" / profile / "config" / "install" / "system.theme.yml",
        root / "core" / "config" / "install" / "system.theme.yml",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return parse_info_yml(candidate.read_text(encoding="utf-8"))
    return {}


def build_inventory(
    root,
    *,
    product="Drupal Core",
    ref,
    ref_type="tag",
    commit=None,
    profile="standard",
    repository="https://git.drupalcode.org/project/drupal",
    retrieved_at,
):
    """Build a deterministic inventory artifact from a source tree.

    ``root`` must contain ``core/modules``, ``core/themes`` and
    ``core/profiles``. The caller supplies the exact ref, commit and retrieval
    time so the artifact can be traced to a release tag.
    """
    root = Path(root)
    modules = _discover(root, "core/modules", "module")
    themes = _discover(root, "core/themes", "theme")
    profiles = _discover(root, "core/profiles", "profile")

    module_info = {name: info for name, (_path, info) in modules.items()}
    theme_info = {name: info for name, (_path, info) in themes.items()}
    profile_info = {name: info for name, (_path, info) in profiles.items()}

    selected_profile = profile_info.get(profile) or {}
    install_roots = selected_profile.get("install") or []
    theme_roots = selected_profile.get("themes") or []
    installed_modules = _closure(install_roots, module_info)
    installed_themes = _closure(theme_roots, theme_info)
    theme_config = _theme_config(root, profile)
    default_theme = str(theme_config.get("default") or "").strip() or None
    admin_theme = str(theme_config.get("admin") or "").strip() or None
    if default_theme and default_theme not in installed_themes:
        installed_themes.add(default_theme)
    if admin_theme and admin_theme not in installed_themes:
        installed_themes.add(admin_theme)

    components = []
    for kind, discovered in (("module", modules), ("theme", themes)):
        for name, (path, info) in discovered.items():
            status, status_basis = extension_status(info)
            installed = name in (installed_modules if kind == "module" else installed_themes)
            components.append({
                "machine_name": name,
                "type": kind,
                "label": str(info.get("name") or name),
                "status": status,
                "status_basis": status_basis,
                "bundled": True,
                "installed_by_standard_profile": installed,
                "default_theme": bool(kind == "theme" and default_theme == name),
                "admin_theme": bool(kind == "theme" and admin_theme == name),
                "hidden": _bool(info.get("hidden")),
                "base_theme": _normalise_base_theme(info.get("base theme")),
                "package": str(info.get("package") or "").strip() or None,
                "dependencies": _dependency_names(info),
                "source_path": path.relative_to(root).as_posix(),
            })
    components.sort(key=lambda item: (item["type"], item["machine_name"]))

    profile_names = sorted(profile_info)
    counts = {
        "modules_bundled": len(modules),
        "themes_bundled": len(themes),
        "profiles_bundled": len(profiles),
        "modules_installed_by_standard_profile": len(installed_modules & set(module_info)),
        "themes_installed_by_standard_profile": len(installed_themes & set(theme_info)),
        "modules_experimental": sum(
            1 for item in components if item["type"] == "module" and item["status"] == "experimental"
        ),
        "themes_experimental": sum(
            1 for item in components if item["type"] == "theme" and item["status"] == "experimental"
        ),
        "modules_deprecated": sum(
            1 for item in components if item["type"] == "module" and item["status"] == "deprecated"
        ),
        "themes_deprecated": sum(
            1 for item in components if item["type"] == "theme" and item["status"] == "deprecated"
        ),
        "modules_obsolete": sum(
            1 for item in components if item["type"] == "module" and item["status"] == "obsolete"
        ),
        "themes_obsolete": sum(
            1 for item in components if item["type"] == "theme" and item["status"] == "obsolete"
        ),
    }
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "disclaimer": (
            "Declared component inventory extracted from a source tree. "
            "It is not an accessibility assessment, conformance result or score."
        ),
        "source": {
            "product": product,
            "repository": repository,
            "ref": str(ref),
            "ref_type": ref_type,
            "commit": commit,
            "retrieved_at": retrieved_at,
            "method": "direct .info.yml extraction from the exact ref; no release-note inference",
        },
        "scope": {
            "bundled": "Every module, theme and profile directory with a matching .info.yml in the ref.",
            "installed": (
                f"Closure of the {profile} profile's install list over bundled module dependencies, "
                "plus its declared themes and the themes set in system.theme.yml."
            ),
            "default": "system.theme.yml default/admin values for the named profile, not a site configuration.",
        },
        "profile": {
            "name": profile,
            "install_list": sorted(str(item) for item in install_roots),
            "themes": sorted(str(item) for item in theme_roots),
            "default_theme": default_theme,
            "admin_theme": admin_theme,
        },
        "profiles": profile_names,
        "counts": counts,
        "components": components,
        "digest_scope": "sha256 over this artifact excluding generated_at and evidence_digest",
    }
    artifact["content_digest"] = sha256_json({
        "source": {k: v for k, v in artifact["source"].items() if k != "retrieved_at"},
        "profile": artifact["profile"],
        "components": artifact["components"],
    })
    artifact["evidence_digest"] = digest_artifact(artifact)
    return artifact


def _component_map(inventory):
    return {
        (item["type"], item["machine_name"]): item
        for item in inventory.get("components") or []
    }


def compare_inventories(old, new, *, note=None):
    """Compare two inventory artifacts without inferring lineage.

    Additions and removals are facts about package membership. A removal is
    **not** a fix and does not establish that a contributed successor exists.
    """
    old_map = _component_map(old)
    new_map = _component_map(new)
    added = []
    removed = []
    changed = []
    for key in sorted(set(new_map) - set(old_map)):
        added.append(new_map[key])
    for key in sorted(set(old_map) - set(new_map)):
        removed.append(old_map[key])
    for key in sorted(set(old_map) & set(new_map)):
        before = old_map[key]
        after = new_map[key]
        fields = {}
        for field in ("status", "installed_by_standard_profile", "default_theme", "admin_theme"):
            if before.get(field) != after.get(field):
                fields[field] = {"before": before.get(field), "after": after.get(field)}
        if fields:
            changed.append({
                "type": key[0],
                "machine_name": key[1],
                "changes": fields,
            })
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "drupal-component-inventory-comparison",
        "disclaimer": (
            "Package membership changes only. Removed does not mean fixed; added does not mean "
            "adopted from a contributed project."
        ),
        "note": note,
        "from": {
            "ref": (old.get("source") or {}).get("ref"),
            "commit": (old.get("source") or {}).get("commit"),
            "inventory_evidence_digest": old.get("evidence_digest"),
        },
        "to": {
            "ref": (new.get("source") or {}).get("ref"),
            "commit": (new.get("source") or {}).get("commit"),
            "inventory_evidence_digest": new.get("evidence_digest"),
        },
        "count_deltas": {
            key: (new.get("counts") or {}).get(key, 0) - (old.get("counts") or {}).get(key, 0)
            for key in sorted(set(old.get("counts") or {}) | set(new.get("counts") or {}))
        },
        "profile": {
            "from": old.get("profile"),
            "to": new.get("profile"),
        },
        "added": added,
        "removed": removed,
        "changed": changed,
    }


def write_json(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target
