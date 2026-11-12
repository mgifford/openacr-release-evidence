"""Surface-level assessment policy for draft ACR results.

This module deliberately does **not** convert issue-queue absence or presence
into a conformance result.

* A reported issue is evidence that somebody reported a possible barrier. It is
  not a reproduction on the target release, so it does not by itself justify
  ``Partially Supports``.
* An empty queue is not evidence that a requirement is met, so it does not
  justify ``Supports``.
* ``Not Applicable`` still requires documented feature absence.
* ``Does Not Support`` still requires explicit broad-failure evidence in the
  declared policy.

Everything else is ``Not Evaluated``: a human reviewer must assign an ACR result
after testing or other reviewed evidence.
"""
import json
from pathlib import Path

POLICY_PATH = Path(__file__).resolve().parents[2] / "config" / "surface-assessments.json"
PRODUCT_SCOPE_NA = {
    "1.2.1": "Drupal Core does not provide audio/video playback out of the box.",
    "1.2.3": "Drupal Core does not provide audio description or media alternatives out of the box.",
    "1.2.4": "Drupal Core has no live audio/video feature.",
    "1.2.5": "Drupal Core has no video player or audio-description feature.",
    "1.4.2": "Drupal Core has no native audio playback or automatic audio feature to control; contrib media players are separate products.",
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
    """Return reviewed conformance terms, never inferred from the queue alone.

    ``issues`` is accepted for API compatibility and for callers that want to
    show reported barriers separately. It must not change the adherence result:
    an unreproduced report is not a conformance finding.
    """
    policy = policy or load_policy()
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
    for name in ("web", "authoring-tool"):
        if (str(criterion), name) in broad_failure:
            results[name] = "Does Not Support"
    return {
        "web": results["web"],
        "electronic-docs": "Not Applicable",
        "software": "Not Applicable",
        "authoring-tool": results["authoring-tool"],
    }


def component_results(issues, policy=None):
    """Return component-level terms without inferring them from issue counts."""
    return {
        "web": "Not Evaluated",
        "electronic-docs": "Not Applicable",
        "software": "Not Applicable",
        "authoring-tool": "Not Evaluated",
    }


def assessment_note(criterion, surface, result):
    if result == "Supports":
        return (
            f"A reviewer recorded positive evidence for the {surface} surface. "
            "This value is not produced automatically by the pipeline."
        )
    if result == "Partially Supports":
        return (
            f"A reviewer recorded partial evidence for the {surface} surface. "
            "Reported issues alone do not produce this value."
        )
    if result == "Not Applicable":
        return "Feature absent from the declared product scope, with a documented basis."
    if result == "Does Not Support":
        return "Explicit broad-failure evidence is recorded in the assessment policy."
    return (
        "No reviewed conformance result is recorded. Reported issues are listed separately; "
        "an unreproduced report or an empty queue does not decide this criterion."
    )
