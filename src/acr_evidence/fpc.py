"""Section 508 functional performance mapping from WCAG criteria.

The mapping is descriptive: it groups existing WCAG results by functional
impact. It is not an independent functional-performance test and does not
populate OpenACR FPC values.
"""
import csv
from pathlib import Path

MAPPING_PATH = Path(__file__).resolve().parents[2] / "config" / "fpc-wcag-mapping.csv"
LABELS = {
    "WV": "Without Vision",
    "LV": "With Limited Vision",
    "WPC": "Without Perception of Color",
    "WH": "Without Hearing",
    "LH": "With Limited Hearing",
    "WS": "Without Speech",
    "LM": "With Limited Manipulation",
    "LRS": "With Limited Reach and Strength",
    "LLCLA": "With Limited Language, Cognitive, and Learning Abilities",
}
DISABILITY_LABELS = {
    "WV": "Vision",
    "LV": "Limited vision",
    "WPC": "Colour perception",
    "WH": "Hearing",
    "LH": "Limited hearing",
    "WS": "Speech",
    "LM": "Motor/manipulation",
    "LRS": "Reach/strength",
    "LLCLA": "Cognitive/learning",
}
COLUMNS = {
    "Without Vision (WV)": "WV",
    "Limited Vision (LV)": "LV",
    "Without Perception of Color (WPC)": "WPC",
    "Without Hearing (WH)": "WH",
    "Limited Hearing (LH)": "LH",
    "Without Speech (WS)": "WS",
    "Limited Manipulation (LM)": "LM",
    "Limited Reach and Strength (LRS)": "LRS",
    "Limited Language, Cognitive, and Learning Abilities (LLCLA)": "LLCLA",
}


def load_mapping(path=None):
    """Return FPC category -> WCAG criteria."""
    mapping = {key: [] for key in LABELS}
    try:
        with open(path or MAPPING_PATH, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                criterion = (row.get("WCAG 2.0 SC") or "").strip()
                if not criterion:
                    continue
                number = criterion.split(" ", 1)[0]
                for column, key in COLUMNS.items():
                    if (row.get(column) or "").strip():
                        mapping[key].append(number)
    except OSError:
        return {}
    return {key: sorted(set(values)) for key, values in mapping.items()}


def disability_labels(criterion, path=None):
    """Return disability groups mapped to one WCAG criterion."""
    mapping = load_mapping(path)
    labels = []
    for key, criteria in mapping.items():
        if str(criterion) in criteria:
            labels.append(DISABILITY_LABELS[key])
    return sorted(set(labels))


def summarize(results_by_criterion, path=None):
    """Summarize mapped WCAG results by FPC category.

    ``results_by_criterion`` maps a WCAG criterion to a surface result dict
    (Web/Authoring Tool/Electronic Documents/Software). Only the assessed Web
    and Authoring Tool surfaces are considered.
    """
    mapping = load_mapping(path)
    rows = []
    for key in ("WV", "LV", "WPC", "WH", "LH", "WS", "LM", "LRS", "LLCLA"):
        criteria = mapping.get(key) or []
        statuses = []
        for criterion in criteria:
            result = results_by_criterion.get(criterion) or {}
            statuses.extend([result.get("web"), result.get("authoring-tool")])
        statuses = [value for value in statuses if value]
        if "Does Not Support" in statuses:
            status = "Does Not Support"
        elif "Partially Supports" in statuses:
            status = "Partially Supports"
        elif "Supports" in statuses:
            status = "Supports"
        elif statuses and all(value == "Not Applicable" for value in statuses):
            status = "Not Applicable"
        else:
            status = "Not Evaluated"
        rows.append({
            "id": key,
            "label": LABELS[key],
            "status": status,
            "criteria": criteria,
        })
    return {
        "source": "https://github.com/CivicActions/accessibility-data-reference",
        "source_data": "mapping-wcag-to-fpc.csv",
        "note": "Mapped from WCAG evidence; not an independent functional-performance evaluation.",
        "rows": rows,
    }
