"""Small WCAG 2.2 criterion catalogue used for report labels only.

Titles and levels come from the W3C WCAG 2.2 Recommendation. This is not a
conformance catalogue: an issue tag does not establish a criterion result.
"""
SPEC = "https://www.w3.org/TR/WCAG22/"

CRITERIA = {
    "1.1.1": ("Non-text Content", "A", "#non-text-content"),
    "1.2.1": ("Audio-only and Video-only (Prerecorded)", "A", "#audio-only-and-video-only-prerecorded"),
    "1.2.2": ("Captions (Prerecorded)", "A", "#captions-prerecorded"),
    "1.2.3": ("Audio Description or Media Alternative (Prerecorded)", "A", "#audio-description-or-media-alternative-prerecorded"),
    "1.2.4": ("Captions (Live)", "AA", "#captions-live"),
    "1.2.5": ("Audio Description (Prerecorded)", "AA", "#audio-description-prerecorded"),
    "1.2.6": ("Sign Language (Prerecorded)", "AAA", "#sign-language-prerecorded"),
    "1.2.7": ("Extended Audio Description (Prerecorded)", "AAA", "#extended-audio-description-prerecorded"),
    "1.2.8": ("Media Alternative (Prerecorded)", "AAA", "#media-alternative-prerecorded"),
    "1.2.9": ("Audio-only (Live)", "AAA", "#audio-only-live"),
    "1.3.1": ("Info and Relationships", "A", "#info-and-relationships"),
    "1.3.2": ("Meaningful Sequence", "A", "#meaningful-sequence"),
    "1.3.3": ("Sensory Characteristics", "A", "#sensory-characteristics"),
    "1.3.4": ("Orientation", "AA", "#orientation"),
    "1.3.5": ("Identify Input Purpose", "AA", "#identify-input-purpose"),
    "1.4.1": ("Use of Color", "A", "#use-of-color"),
    "1.4.3": ("Contrast (Minimum)", "AA", "#contrast-minimum"),
    "1.4.4": ("Resize Text", "AA", "#resize-text"),
    "1.4.5": ("Images of Text", "AA", "#images-of-text"),
    "1.4.10": ("Reflow", "AA", "#reflow"),
    "1.4.11": ("Non-text Contrast", "AA", "#non-text-contrast"),
    "1.4.12": ("Text Spacing", "AA", "#text-spacing"),
    "1.4.13": ("Content on Hover or Focus", "AA", "#content-on-hover-or-focus"),
    "2.1.1": ("Keyboard", "A", "#keyboard"),
    "2.1.2": ("No Keyboard Trap", "A", "#no-keyboard-trap"),
    "2.2.1": ("Timing Adjustable", "A", "#timing-adjustable"),
    "2.2.2": ("Pause, Stop, Hide", "A", "#pause-stop-hide"),
    "2.4.1": ("Bypass Blocks", "A", "#bypass-blocks"),
    "2.4.2": ("Page Titled", "A", "#page-titled"),
    "2.4.3": ("Focus Order", "A", "#focus-order"),
    "2.4.4": ("Link Purpose (In Context)", "A", "#link-purpose-in-context"),
    "2.4.6": ("Headings and Labels", "AA", "#headings-and-labels"),
    "2.4.7": ("Focus Visible", "AA", "#focus-visible"),
    "2.4.11": ("Focus Not Obscured (Minimum)", "AA", "#focus-not-obscured-minimum"),
    "2.5.3": ("Label in Name", "A", "#label-in-name"),
    "2.5.7": ("Dragging Movements", "AA", "#dragging-movements"),
    "2.5.8": ("Target Size (Minimum)", "AA", "#target-size-minimum"),
    "3.1.1": ("Language of Page", "A", "#language-of-page"),
    "3.2.3": ("Consistent Navigation", "AA", "#consistent-navigation"),
    "3.2.4": ("Consistent Identification", "AA", "#consistent-identification"),
    "3.2.5": ("Change on Request", "AAA", "#on-request"),
    "3.3.1": ("Error Identification", "A", "#error-identification"),
    "3.3.2": ("Labels or Instructions", "A", "#labels-or-instructions"),
    "3.3.3": ("Error Suggestion", "AA", "#error-suggestion"),
    "3.3.7": ("Redundant Entry", "A", "#redundant-entry"),
    "3.3.8": ("Accessible Authentication (Minimum)", "AA", "#accessible-authentication-minimum"),
    "4.1.2": ("Name, Role, Value", "A", "#name-role-value"),
    "4.1.3": ("Status Messages", "AA", "#status-messages"),
}


_CATALOG_INDEX = None


def _catalog_index():
    global _CATALOG_INDEX
    if _CATALOG_INDEX is None:
        _CATALOG_INDEX = {}
        try:
            from .openacr_export import load_catalog
            levels = {
                "success_criteria_level_a": "A",
                "success_criteria_level_aa": "AA",
                "success_criteria_level_aaa": "AAA",
            }
            for chapter in load_catalog().get("chapters") or []:
                level = levels.get(chapter.get("id"), "unknown")
                for item in chapter.get("criteria") or []:
                    _CATALOG_INDEX[str(item.get("id"))] = (
                        item.get("handle") or f"WCAG criterion {item.get('id')}",
                        level,
                        "#" + (item.get("alt_id") or ""),
                    )
        except (ImportError, OSError, ValueError):
            _CATALOG_INDEX = {}
    return _CATALOG_INDEX


def criterion_info(criterion):
    key = str(criterion)
    title, level, anchor = CRITERIA.get(key) or _catalog_index().get(
        key, (f"WCAG criterion {key}", "unknown", "")
    )
    return {
        "id": key,
        "title": title,
        "level": level,
        "url": SPEC + anchor,
    }


APPLICABILITY_MEANINGS = {
    "confirmed-affected": "A reproduction on the target release demonstrates the barrier.",
    "likely-affected": "Report evidence suggests the barrier is present, but it was not reproduced.",
    "confirmed-fixed": "A fix commit is contained in the release tag; behavioural verification is still required.",
    "not-introduced": "The affected feature or code is absent from the target release.",
    "not-in-scope": "The component is outside the declared assessment scope.",
    "unknown": "Insufficient target-specific evidence; do not infer applicability or support.",
}

SHORT_APPLICABILITY = {
    "confirmed-affected": "Confirmed affected",
    "likely-affected": "Likely affected",
    "confirmed-fixed": "Fix included",
    "not-introduced": "Not introduced",
    "not-in-scope": "Not in scope",
    "unknown": "Unknown",
}

SUPPORT_STATUS_LABELS = {
    "supported": "Supported release line",
    "pre-release": "Pre-release",
    "development": "Development branch",
    "eol": "End of life",
    "unknown": "Unknown support status",
}

APPLICABILITY_LABELS = {
    "confirmed-affected": "Confirmed affected (reproduction evidence)",
    "likely-affected": "Likely affected (report evidence; not reproduced)",
    "confirmed-fixed": "Fix included in release (not independently verified)",
    "not-introduced": "Not introduced in this release",
    "not-in-scope": "Not in this assessment's scope",
    "unknown": "Unknown (insufficient target-specific evidence)",
}
