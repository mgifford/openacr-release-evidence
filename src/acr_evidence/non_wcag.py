"""Non-WCAG accessibility review prompts.

These are deliberately outside the ACR result terms. They document areas where a
product can create accessibility barriers without a clean WCAG AA success
criterion, and they remain evidence gaps rather than findings.
"""
import json
from pathlib import Path

CONSIDERATIONS_PATH = Path(__file__).resolve().parents[2] / "config" / "non-wcag-considerations.json"


def load_considerations(path=None):
    try:
        return json.loads(Path(path or CONSIDERATIONS_PATH).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"items": [], "note": ""}
