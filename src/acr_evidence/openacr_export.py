"""Export and validate a Civicactions/GSA OpenACR 0.1.0 draft.

The generated YAML is a *skeleton*, not a conformance claim. It passes the
official schema and catalog checks but deliberately contains no adherence
levels. A human reviewer must replace the placeholder author, assess each
criterion, populate components/adherence, and revalidate before publishing.
"""
import json
from pathlib import Path

from .model import sha256_json

STANDARDS_DIR = Path(__file__).resolve().parent / "standards" / "openacr"
DEFAULT_SCHEMA = STANDARDS_DIR / "openacr-0.1.0.json"
DEFAULT_CATALOG_SCHEMA = STANDARDS_DIR / "openacr-catalog-0.1.0.json"
DEFAULT_CATALOG = STANDARDS_DIR / "2.5-edition-wcag-2.2-508-en.yaml"
OPENACR_SOURCE = {
    "repository": "https://github.com/Civicactions/openacr",
    "upstream": "https://github.com/GSA/openacr",
    "ref": "ca-main",
    "commit": "d6d18a93d8b043f7edfec13834f2d6b9557c5dbd",
    "retrieved_at": "2026-11-07",
}
PLACEHOLDER_EMAIL = "reviewer@example.invalid"


class OpenACRError(RuntimeError):
    pass


def _yaml():
    try:
        import yaml
    except ImportError as exc:
        raise OpenACRError("Install optional dependency: pip install -e '.[openacr]'") from exc
    return yaml


def _jsonschema():
    try:
        import jsonschema
    except ImportError as exc:
        raise OpenACRError("Install optional dependency: pip install -e '.[openacr]'") from exc
    return jsonschema


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_catalog(path=None):
    document = _yaml().safe_load(Path(path or DEFAULT_CATALOG).read_text(encoding="utf-8"))
    if not isinstance(document, dict) or "chapters" not in document:
        raise OpenACRError("Catalog is missing chapters")
    return document


def _chapter_criteria(catalog):
    return {
        chapter["id"]: {criterion["id"] for criterion in chapter.get("criteria") or []}
        for chapter in catalog.get("chapters") or []
    }


def _criterion_components(catalog):
    return {
        chapter["id"]: {
            criterion["id"]: set(criterion.get("components") or [])
            for criterion in chapter.get("criteria") or []
        }
        for chapter in catalog.get("chapters") or []
    }


def build_draft(analysis, catalog, catalog_name="2.5-edition-wcag-2.2-508-en"):
    """Build a complete, draft OpenACR skeleton with no adherence values."""
    target = analysis.get("target") or {}
    assessment = analysis.get("assessment") or {}
    installation = assessment.get("installation") or {}
    product = assessment.get("product") or "Drupal Core"
    release = target.get("release") or assessment.get("release") or "unknown"
    generated = analysis.get("generated_at") or ""
    report_date = generated[:10] if len(generated) >= 10 else "unknown"
    description = installation.get("configuration") or "Drupal Core accessibility evidence target."
    chapters = {}
    for chapter in catalog.get("chapters") or []:
        chapters[chapter["id"]] = {
            "notes": (
                "DRAFT: no conformance values are populated. Evidence report: index.html. "
                "A reviewer must assess every criterion in this chapter and select the applicable "
                "components and adherence levels."
            ),
            "criteria": [{"num": criterion["id"]} for criterion in chapter.get("criteria") or []],
        }
    notes = (
        f"DRAFT OpenACR skeleton for {product} {release} ({target.get('ref_type') or 'tag'} "
        f"{target.get('ref') or 'unknown'}). Evidence report: index.html. Machine-readable "
        f"evidence: evidence.json. Evidence digest: {analysis.get('evidence_digest')}. "
        "No WCAG conformance values are populated. The author is a placeholder; a human reviewer "
        "must replace it, assess every criterion, select components and adherence levels, and run "
        "`acr-evidence openacr-validate --file openacr.yaml --strict` before publishing. "
        "This file has not been round-tripped through the Civicactions/GSA ACR editor."
    )
    return {
        "title": f"{product} {release} Accessibility Conformance Report — DRAFT",
        "product": {
            "name": product,
            "version": release,
            "description": description,
        },
        "author": {
            "name": "Unassigned reviewer (draft)",
            "email": PLACEHOLDER_EMAIL,
        },
        "report_date": report_date,
        "last_modified_date": report_date,
        "version": 1,
        "notes": notes,
        "evaluation_methods_used": (
            "Public Drupal.org issue-queue evidence collection, commit/tag containment analysis, "
            "and explicit WCAG candidate tag grouping. No manual keyboard, screen-reader or "
            "assistive-technology testing of the target was performed in this phase. A human "
            "reviewer must complete the evaluation and select the OpenACR adherence values."
        ),
        "legal_disclaimer": (
            "DRAFT for human review. This is not a final Accessibility Conformance Report, does not "
            "certify conformance, and must not be published as a vendor ACR until reviewed and approved."
        ),
        "repository": "https://github.com/mgifford/openacr-release-evidence",
        "feedback": "https://github.com/mgifford/openacr-release-evidence/issues",
        "catalog": catalog_name,
        "chapters": chapters,
        "draft": True,
        "target": {
            "product": product,
            "release": release,
            "ref": target.get("ref"),
            "ref_type": target.get("ref_type"),
            "support_status": target.get("support_status"),
            "release_line": target.get("release_line"),
            "parent_project": target.get("parent_project"),
            "assessment_id": target.get("assessment_id"),
            "evidence_digest": analysis.get("evidence_digest"),
            "evidence_report": "index.html",
        },
        "standard_source": OPENACR_SOURCE,
    }


def _schema_errors(document, schema_path):
    jsonschema = _jsonschema()
    schema = load_json(schema_path or DEFAULT_SCHEMA)
    validator = jsonschema.Draft7Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(document), key=lambda item: "/".join(str(part) for part in item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "(root)"
        errors.append(f"schema: {location}: {error.message}")
    return errors


def _catalog_errors(document, catalog, strict=False):
    errors = []
    chapters = _chapter_criteria(catalog)
    components = _criterion_components(catalog)
    term_ids = {term["id"] for term in catalog.get("terms") or []}
    component_ids = {component["id"] for component in catalog.get("components") or []}
    doc_chapters = document.get("chapters") or {}
    for chapter_id, chapter_data in doc_chapters.items():
        if chapter_id not in chapters:
            errors.append(f"catalog: unknown chapter {chapter_id!r}")
            continue
        if not isinstance(chapter_data, dict):
            errors.append(f"catalog: chapter {chapter_id!r} is not an object")
            continue
        criteria = chapter_data.get("criteria") or []
        seen = set()
        for criterion in criteria:
            if not isinstance(criterion, dict) or "num" not in criterion:
                errors.append(f"catalog: chapter {chapter_id!r} has a criterion without num")
                continue
            num = str(criterion["num"])
            seen.add(num)
            if num not in chapters[chapter_id]:
                errors.append(f"catalog: criterion {num!r} is not in chapter {chapter_id!r}")
                continue
            for component in criterion.get("components") or []:
                if not isinstance(component, dict) or "name" not in component:
                    errors.append(f"catalog: criterion {num!r} has a component without name")
                    continue
                name = str(component["name"])
                if name not in component_ids:
                    errors.append(f"catalog: component {name!r} has no definition")
                if name not in components[chapter_id].get(num, set()):
                    errors.append(f"catalog: component {name!r} is not supported by criterion {num!r}")
                level = (component.get("adherence") or {}).get("level")
                if level:
                    if level not in term_ids:
                        errors.append(f"catalog: adherence {level!r} has no term definition")
                    if chapter_id in {"success_criteria_level_a", "success_criteria_level_aa"} and level == "not-evaluated":
                        errors.append(
                            f"policy: not-evaluated is restricted to AAA; criterion {num!r} is in {chapter_id!r}"
                        )
        if strict:
            missing = chapters[chapter_id] - seen
            if missing and not chapter_data.get("disabled"):
                errors.append(
                    f"strict: chapter {chapter_id!r} is missing criteria {', '.join(sorted(missing))}"
                )
            if not chapter_data.get("disabled"):
                for criterion in criteria:
                    if not isinstance(criterion, dict) or not criterion.get("components"):
                        number = criterion.get("num") if isinstance(criterion, dict) else None
                        errors.append(
                            f"strict: criterion {number!r} has no components/adherence"
                        )
    if strict:
        if document.get("draft") is not False:
            errors.append("strict: set draft: false only after human review")
        author = document.get("author") or {}
        email = str(author.get("email") or "")
        if not email or email.endswith(".invalid") or email == PLACEHOLDER_EMAIL:
            errors.append("strict: replace the placeholder reviewer email")
        if str(author.get("name") or "").startswith("Unassigned"):
            errors.append("strict: replace the placeholder reviewer name")
    return errors


def validate_document(document, catalog=None, schema_path=None, strict=False):
    catalog = catalog or load_catalog()
    errors = _schema_errors(document, schema_path)
    errors.extend(_catalog_errors(document, catalog, strict=strict))
    return {
        "valid": not errors,
        "draft": bool(document.get("draft")),
        "strict": bool(strict),
        "schema": "openacr-0.1.0.json",
        "catalog": "2.5-edition-wcag-2.2-508-en",
        "source": OPENACR_SOURCE,
        "errors": errors,
    }


def export_openacr(analysis, output_dir, catalog_path=None, schema_path=None, strict=False):
    """Write openacr.yaml and openacr-validation.json for one target report."""
    yaml = _yaml()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog(catalog_path)
    document = build_draft(analysis, catalog)
    result = validate_document(document, catalog=catalog, schema_path=schema_path, strict=strict)
    yaml_path = output / "openacr.yaml"
    validation_path = output / "openacr-validation.json"
    yaml_path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    result["checked_at"] = analysis.get("generated_at")
    result["document_digest"] = sha256_json(document)
    validation_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if not result["valid"]:
        raise OpenACRError("Generated OpenACR failed validation: " + "; ".join(result["errors"][:5]))
    return {"yaml": yaml_path, "validation": validation_path, "result": result}


def validate_file(path, catalog_path=None, schema_path=None, strict=False):
    yaml = _yaml()
    document = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    result = validate_document(
        document, catalog=load_catalog(catalog_path), schema_path=schema_path, strict=strict
    )
    result["file"] = str(path)
    return result
