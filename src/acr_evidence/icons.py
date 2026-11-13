"""WCAG 2.2 pictogram mapping and safe sprite helpers.

The icons are decorative when rendered beside the criterion number and title;
the adjacent text remains the accessible name. Never give both the icon and the
link a separate copy of the criterion name.
"""
import json
import re
import shutil
import xml.etree.ElementTree as ET
from functools import lru_cache
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAPPING_PATH = ROOT / "config" / "wcag22-icons.json"
SPRITE_PATH = Path(__file__).resolve().parent / "static" / "wcag22_icons.svg"
SPRITE_NAME = "wcag22_icons.svg"
SPRITE_HREF = f"./{SPRITE_NAME}"
SVG_NS = "{http://www.w3.org/2000/svg}"


@lru_cache(maxsize=2)
def load_mapping(path=None):
    """Return the mapping keyed by WCAG number, plus its metadata."""
    document = json.loads(Path(path or MAPPING_PATH).read_text(encoding="utf-8"))
    mapping = {}
    for item in document.get("mapping") or []:
        number = str(item.get("number") or "")
        if number:
            mapping[number] = item
    return document, mapping


def icon_id(criterion):
    """Return the sprite symbol id for a WCAG number, or None."""
    _document, mapping = load_mapping()
    item = mapping.get(str(criterion))
    return item.get("id") if item else None


def icon_description(criterion):
    _document, mapping = load_mapping()
    item = mapping.get(str(criterion))
    return item.get("icon_description") if item else None


def icon_markup(criterion, href=SPRITE_HREF):
    """Return a decorative icon reference, or an empty string if unmapped."""
    symbol = icon_id(criterion)
    if not symbol:
        return ""
    return (
        f'<svg class="wcag-icon" viewBox="0 0 100 100" aria-hidden="true" focusable="false">'
        f'<use href="{escape(href)}#{escape(symbol)}"></use></svg>'
    )


def _local_name(tag):
    return tag.rsplit("}", 1)[-1]


def validate_sprite(path=None):
    """Reject scripts, event handlers, external references and duplicate ids.

    This is a local, author-controlled asset, but SVG is active XML. The check
    is deliberately small and fail-closed for the build pipeline.
    """
    source = Path(path or SPRITE_PATH).read_text(encoding="utf-8")
    if re.search(r"<!DOCTYPE|<!ENTITY", source, re.IGNORECASE):
        raise ValueError("SVG sprite must not contain a DOCTYPE or entity declaration")
    root = ET.fromstring(source)
    ids = []
    symbols = []
    for element in root.iter():
        name = _local_name(element.tag)
        if name == "script":
            raise ValueError("SVG sprite must not contain script elements")
        for attribute, value in element.attrib.items():
            if _local_name(attribute).startswith("on"):
                raise ValueError("SVG sprite must not contain event-handler attributes")
            if _local_name(attribute) in {"href", "src"} and value and not value.startswith("#"):
                raise ValueError("SVG sprite must not reference external resources")
        if name == "symbol":
            symbol_id = element.get("id")
            if not symbol_id:
                raise ValueError("SVG symbol is missing an id")
            ids.append(symbol_id)
            symbols.append(element)
    if len(ids) != len(set(ids)):
        raise ValueError("SVG sprite contains duplicate symbol ids")
    return {"symbols": len(symbols), "ids": ids}


def copy_sprite(destination):
    """Copy the validated sprite to the report root."""
    validate_sprite()
    target = Path(destination) / SPRITE_NAME
    shutil.copyfile(SPRITE_PATH, target)
    return target
