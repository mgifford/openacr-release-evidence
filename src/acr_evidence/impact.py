"""Load and validate the reusable accessibility-impact knowledge layer."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data" / "accessibility-impact"
CRITERIA_PATH = DATA / "wcag" / "2.2" / "criteria.json"
GROUPS_PATH = DATA / "schema" / "groups.json"
HISTORICAL_PATH = DATA / "wcag" / "2.2" / "historical.json"
_CACHE = None


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_dataset():
    global _CACHE
    if _CACHE is None:
        _CACHE = {
            "criteria": _load(CRITERIA_PATH),
            "groups": _load(GROUPS_PATH),
            "historical": _load(HISTORICAL_PATH),
        }
    return _CACHE


def get_criterion_impact(criterion):
    """Return the public impact view for one active WCAG criterion."""
    data = load_dataset()
    record = next((item for item in data["criteria"]["active_criteria"] if item["id"] == str(criterion)), None)
    if record is None:
        return None
    vocab = data["groups"]
    groups = [
        {"id": key, "label": vocab["groups"][key]["label"]}
        for key in record["user_impact"]["groups"]
    ]
    needs = [
        {"id": key, "label": vocab["functional_needs"][key]}
        for key in record["user_impact"]["functional_needs"]
    ]
    return {
        "id": record["id"],
        "title": record["title"],
        "level": record["level"],
        "introduced_in": record["introduced_in"],
        "groups": groups,
        "functional_needs": needs,
        "barrier": record["user_impact"]["barrier"],
        "description": record["user_impact"]["description"],
        "sources": record.get("sources") or [],
        "standards_mappings": record.get("standards_mappings") or {},
        "review_status": record.get("review_status"),
        "last_reviewed": record.get("last_reviewed"),
    }


def validate_dataset():
    data = load_dataset()
    vocab = data["groups"]
    errors = []
    ids = [item["id"] for item in data["criteria"]["active_criteria"]]
    if len(ids) != 86:
        errors.append(f"expected 86 active criteria, got {len(ids)}")
    if len(set(ids)) != len(ids):
        errors.append("duplicate criterion IDs")
    if "4.1.1" in ids:
        errors.append("4.1.1 must not be active in WCAG 2.2")
    for item in data["criteria"]["active_criteria"]:
        if not item["user_impact"]["description"].strip():
            errors.append(f"{item['id']}: empty description")
        if not item["user_impact"]["barrier"].strip():
            errors.append(f"{item['id']}: empty barrier")
        if not item.get("sources"):
            errors.append(f"{item['id']}: missing source")
        for group in item["user_impact"]["groups"]:
            if group not in vocab["groups"]:
                errors.append(f"{item['id']}: unknown group {group}")
        for need in item["user_impact"]["functional_needs"]:
            if need not in vocab["functional_needs"]:
                errors.append(f"{item['id']}: unknown need {need}")
        if item.get("review_status") not in {"proposed", "reviewed", "reviewed-no-mapping"}:
            errors.append(f"{item['id']}: invalid review status")
    return errors


def coverage():
    data = load_dataset()
    active = data["criteria"]["active_criteria"]
    fpc_mapped = sum(1 for item in active if item["standards_mappings"]["section508_fpc"]["categories"])
    en_pending = sum(1 for item in active if item["standards_mappings"]["en301549"]["v3.2.1"] == "pending")
    return {
        "active": len(active),
        "descriptions": sum(1 for item in active if item["user_impact"]["description"].strip()),
        "sources": sum(1 for item in active if item.get("sources")),
        "proposed": sum(1 for item in active if item.get("review_status") == "proposed"),
        "reviewed": sum(1 for item in active if item.get("review_status") == "reviewed"),
        "section508_mapped": fpc_mapped,
        "en301549_pending": en_pending,
        "errors": validate_dataset(),
    }
