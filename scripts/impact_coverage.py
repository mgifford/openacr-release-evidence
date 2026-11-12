#!/usr/bin/env python3
"""Write the reference-data coverage report."""
from pathlib import Path
from acr_evidence.impact import coverage, load_dataset

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "reference-data-coverage.md"


def main():
    data = load_dataset()
    counts = coverage()
    lines = [
        "# Accessibility impact reference-data coverage",
        "",
        "Generated from `data/accessibility-impact/`.",
        "",
        "## WCAG 2.2 impact data",
        "",
        f"- Active criteria: {counts['active']}",
        f"- With a non-empty impact description: {counts['descriptions']}",
        f"- With at least one authoritative source: {counts['sources']}",
        f"- Proposed (not reviewed): {counts['proposed']}",
        f"- Reviewed: {counts['reviewed']}",
        f"- Validation errors: {len(counts['errors'])}",
        "",
        "## Standards crosswalks",
        "",
        f"- Section 508 FPC mapped: {counts['section508_mapped']} of {counts['active']}",
        f"- EN 301 549 V3.2.1 pending: {counts['en301549_pending']} of {counts['active']}",
        f"- EN 301 549 V4.1.1 pending: {counts['en301549_pending']} of {counts['active']}",
        "",
        "A pending EN 301 549 relationship is not an assertion that no relationship exists.",
        "",
        "## Review state",
        "",
        "All current impact descriptions are `proposed`. Source links are W3C Understanding",
        "pages. Section 508 categories are the existing CivicActions/Section508.gov mapping.",
        "No description is promoted to `reviewed` without human review.",
        "",
        "## Source data",
        "",
        "- Criteria: `data/accessibility-impact/wcag/2.2/criteria.json`",
        "- Historical 4.1.1: `data/accessibility-impact/wcag/2.2/historical.json`",
        "- Controlled vocabulary: `data/accessibility-impact/schema/groups.json`",
        "- Section 508 mapping: `data/accessibility-impact/mappings/section508-fpc.json`",
        "- EN 301 549 V3.2.1: `data/accessibility-impact/mappings/en301549-v3.2.1.json`",
        "- EN 301 549 V4.1.1: `data/accessibility-impact/mappings/en301549-v4.1.1.json`",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
