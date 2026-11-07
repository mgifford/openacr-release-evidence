"""Create a static, relative-path-safe evidence review site."""
from pathlib import Path
import json
import shutil
from .model import assess


def build(manifest, issues, output):
    result = assess(manifest, issues)
    dest = Path(output)
    dest.mkdir(parents=True, exist_ok=True)
    src = Path(__file__).resolve().parent / "static"
    if not src.is_dir():
        raise FileNotFoundError(f"Web assets missing: {src}")
    for file in ("index.html", "app.js", "style.css"):
        shutil.copyfile(src / file, dest / file)
    (dest / "evidence.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
