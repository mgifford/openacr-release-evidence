"""Surface-level assessment policy for draft ACR results.

The policy converts the declared Drupal surface assessment plus the active
known-barrier register into draft terms. It does not create a verified audit:

- known issue on a surface -> Partially Supports;
- no known issue on an assessed surface -> Supports;
- documented feature absence -> Not Applicable;
- unassessed surface -> Not Evaluated;
- Does Not Support only with explicit broad-failure evidence.
"""
import json
from pathlib import Path

POLICY_PATH = Path(__file__).resolve().parents[2] / "config" / "surface-assessments.json"
PRODUCT_SCOPE_NA = {
    "1.2.1": "Drupal Core does not provide audio/video playback out of the box.",
    "1.2.3": "Drupal Core does not provide audio description or media alternatives out of the box.",
    "1.2.4": "Drupal Core has no live audio/video feature.",
    "1.2.5": "Drupal Core has no video player or audio-description feature.",
}


def load_policy(path=None):
    try:
        return json.loads(Path(path or POLICY_PATH).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"surfaces": {}, "does_not_support": []}


def _surface_issues(issues, surface):
    return [
        item for item in issues
        if (item.get("surface") or {}).get("surface", "web") == surface
    ]


def criterion_results(criterion, issues, policy=None):
    policy = policy or load_policy()
    surfaces = policy.get("surfaces") or {}
    broad_failure = {
        (item.get("criterion"), item.get("surface"))
        for item in policy.get("does_not_support") or []
    }
    results = {"web": "Not Evaluated", "authoring-tool": "Not Evaluated"}
    if str(criterion) in PRODUCT_SCOPE_NA:
        return {
            "web": "Not Applicable",
            "electronic-docs": "Not Applicable",
            "software": "Not Applicable",
            "authoring-tool": "Not Applicable",
        }
    for name, surface in (("web", "web"), ("authoring-tool", "authoring")):
        if (str(criterion), name) in broad_failure:
            results[name] = "Does Not Support"
        elif _surface_issues(issues, surface):
            results[name] = "Partially Supports"
        elif (surfaces.get(name) or {}).get("status") == "assessed":
            results[name] = "Supports"
    return {
        "web": results["web"],
        "electronic-docs": "Not Applicable",
        "software": "Not Applicable",
        "authoring-tool": results["authoring-tool"],
    }


def component_results(issues, policy=None):
    policy = policy or load_policy()
    web = any((item.get("surface") or {}).get("surface", "web") == "web" for item in issues)
    authoring = any((item.get("surface") or {}).get("surface", "web") == "authoring" for item in issues)
    return {
        "web": "Partially Supports" if web else "Supports",
        "electronic-docs": "Not Applicable",
        "software": "Not Applicable",
        "authoring-tool": "Partially Supports" if authoring else "Supports",
    }


def assessment_note(criterion, surface, result):
    if result == "Supports":
        return (
            f"No active tagged issue on the {surface} surface. Supports is based on the declared "
            "Drupal surface assessment and the current known-barrier register; it is not a WCAG-EM verification."
        )
    if result == "Partially Supports":
        return f"Known active issue evidence on the {surface} surface; reported barriers are listed below."
    if result == "Not Applicable":
        return "Feature absent from the declared product scope."
    if result == "Does Not Support":
        return "Explicit broad-failure evidence is recorded in the assessment policy."
    return "Surface assessment is not established; no result is assigned."
