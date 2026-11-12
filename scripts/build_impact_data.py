#!/usr/bin/env python3
"""Build the WCAG 2.2 impact dataset deterministically from checked-in sources."""
import csv
import json
from datetime import date
from pathlib import Path

from acr_evidence.openacr_export import load_catalog

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "accessibility-impact"
GROUPS = {
    "WV": ["blind"],
    "LV": ["low_vision"],
    "WPC": ["color_vision_deficiency"],
    "WH": ["deaf"],
    "LH": ["hard_of_hearing"],
    "WS": ["speech_disability"],
    "LM": ["limited_dexterity"],
    "LRS": ["mobility_disability"],
    "LLCLA": ["cognitive_disability", "learning_disability"],
}
MISSING_GROUPS = {
    "2.1.4": ["limited_dexterity", "speech_disability"],
    "2.3.1": ["photosensitive_epilepsy"],
    "2.5.1": ["limited_dexterity", "mobility_disability"],
    "2.5.2": ["limited_dexterity", "mobility_disability"],
    "2.5.3": ["speech_disability", "limited_dexterity"],
    "2.5.4": ["mobility_disability", "limited_dexterity"],
    "3.2.6": ["cognitive_disability", "learning_disability"],
    "3.3.7": ["cognitive_disability", "learning_disability"],
    "1.3.4": ["mobility_disability"],
    "1.3.5": ["cognitive_disability", "learning_disability"],
    "1.4.10": ["low_vision", "mobility_disability"],
    "1.4.11": ["low_vision", "color_vision_deficiency"],
    "1.4.12": ["low_vision", "cognitive_disability"],
    "1.4.13": ["low_vision", "mobility_disability", "cognitive_disability"],
    "2.4.11": ["low_vision", "mobility_disability"],
    "2.5.7": ["limited_dexterity", "mobility_disability"],
    "2.5.8": ["limited_dexterity", "low_vision", "mobility_disability"],
    "3.3.8": ["cognitive_disability", "learning_disability"],
    "4.1.3": ["blind", "low_vision", "cognitive_disability"],
    "1.2.6": ["deaf", "hard_of_hearing"],
    "1.2.7": ["blind", "low_vision"],
    "1.2.8": ["blind", "low_vision", "cognitive_disability"],
    "1.2.9": ["deaf", "hard_of_hearing"],
    "1.3.6": ["cognitive_disability"],
    "1.4.6": ["low_vision"],
    "1.4.7": ["hard_of_hearing", "cognitive_disability"],
    "1.4.8": ["low_vision", "cognitive_disability"],
    "1.4.9": ["low_vision"],
    "2.1.3": ["blind", "mobility_disability", "limited_dexterity"],
    "2.2.3": ["cognitive_disability", "mobility_disability"],
    "2.2.4": ["cognitive_disability", "learning_disability"],
    "2.2.5": ["cognitive_disability", "learning_disability"],
    "2.2.6": ["cognitive_disability", "limited_dexterity"],
    "2.3.2": ["photosensitive_epilepsy"],
    "2.3.3": ["vestibular_disorder", "photosensitive_epilepsy"],
    "2.4.8": ["cognitive_disability", "learning_disability"],
    "2.4.9": ["cognitive_disability", "learning_disability"],
    "2.4.10": ["cognitive_disability", "learning_disability", "blind"],
    "2.4.12": ["low_vision", "mobility_disability"],
    "2.4.13": ["low_vision", "mobility_disability"],
    "2.5.5": ["limited_dexterity", "low_vision"],
    "2.5.6": ["mobility_disability", "limited_dexterity"],
    "3.1.3": ["cognitive_disability", "learning_disability"],
    "3.1.4": ["cognitive_disability", "learning_disability"],
    "3.1.5": ["cognitive_disability", "learning_disability"],
    "3.1.6": ["cognitive_disability", "learning_disability", "hard_of_hearing"],
    "3.2.5": ["cognitive_disability", "learning_disability"],
    "3.3.5": ["cognitive_disability", "learning_disability"],
    "3.3.6": ["cognitive_disability", "learning_disability"],
    "3.3.9": ["cognitive_disability", "learning_disability"],
}
BARRIERS = {
    "1.1.1": "Images, icons, charts and controls without useful text alternatives can be unusable or misidentified.",
    "1.2.1": "Audio-only or silent video content without an alternative excludes people who cannot hear or see it.",
    "1.2.2": "Prerecorded speech without captions excludes people who cannot hear the audio.",
    "1.2.3": "Visual information in video without audio description or a media alternative may be missed.",
    "1.3.1": "Missing or incorrect structure, labels and relationships make content hard to interpret with assistive technology.",
    "1.3.2": "A confusing reading order can make the meaning of content unintelligible.",
    "1.3.3": "Instructions that rely only on shape, colour, size or position can be misunderstood.",
    "1.4.1": "Meaning conveyed only by colour can be missed by people who cannot distinguish those colours.",
    "1.4.2": "Automatically playing audio can interfere with hearing aids, speech output or concentration.",
    "2.1.1": "Controls that require a pointer cannot be operated by keyboard or switch users.",
    "2.1.2": "A keyboard trap can prevent a person from leaving a component or page.",
    "2.1.4": "Single-key shortcuts can be triggered accidentally by speech input or unsteady hands.",
    "2.2.1": "Short or uncontrollable time limits can prevent completion of a task.",
    "2.2.2": "Moving, blinking or auto-updating content can distract or prevent reading.",
    "2.3.1": "Flashing content can trigger seizures in people with photosensitive epilepsy.",
    "2.4.1": "Repeated blocks without a bypass mechanism make navigation slow and tiring.",
    "2.4.2": "A missing or uninformative page title makes pages hard to identify.",
    "2.4.3": "Illogical focus order can disorient keyboard and screen-reader users.",
    "2.4.4": "Ambiguous link text makes destinations unclear without surrounding context.",
    "2.5.1": "Multi-point or path-based gestures exclude people who cannot perform them.",
    "2.5.2": "Actions that fire on pointer-down can cause accidental activation for people with tremor.",
    "2.5.3": "Visible labels that do not match accessible names break speech-input activation.",
    "2.5.4": "Requiring device motion to operate a control excludes people with limited mobility.",
    "3.1.1": "An unmarked page language can make screen-reader pronunciation incorrect.",
    "3.2.1": "Unexpected context changes on focus can disorient and cause errors.",
    "3.2.2": "Unexpected context changes on input can cause people to lose their place.",
    "3.2.6": "Help mechanisms in inconsistent locations increase cognitive and navigation effort.",
    "3.3.1": "Errors that are not described in text can be impossible to identify and correct.",
    "3.3.2": "Missing labels or instructions make form completion guesswork.",
    "3.3.7": "Requiring the same information again burdens memory and cognitive processing.",
    "4.1.2": "Custom controls without name, role and value are not usable with assistive technology.",
    "1.2.4": "Live speech without captions excludes people who cannot hear it in real time.",
    "1.2.5": "Video without audio description can omit visual information needed to understand it.",
    "1.3.4": "Locking orientation can exclude people who use a device in a fixed position.",
    "1.3.5": "Inputs without a programmatic purpose make autofill and personalisation harder.",
    "1.4.3": "Low text contrast makes content unreadable for people with low vision or colour loss.",
    "1.4.4": "Text that cannot be resized prevents magnification users from reading it.",
    "1.4.5": "Images of text cannot be resized, restyled or read reliably by assistive technology.",
    "1.4.10": "Two-dimensional layouts and horizontal scrolling make zoomed content hard to follow.",
    "1.4.11": "Low-contrast controls and boundaries are hard to see or locate.",
    "1.4.12": "Fixed text spacing prevents people from applying their own reading settings.",
    "1.4.13": "Hover or focus content that cannot be dismissed or read blocks interaction.",
    "2.4.5": "A single navigation route can make content hard to find for people with different strategies.",
    "2.4.6": "Unclear headings and labels make page structure and purpose harder to understand.",
    "2.4.7": "A missing visible focus indicator makes keyboard operation hard to track.",
    "2.4.11": "Sticky headers, banners or overlays can hide the focused control.",
    "2.5.7": "Dragging-only interactions exclude people who cannot sustain a drag.",
    "2.5.8": "Small or closely spaced targets cause misactivation for people with tremor or low vision.",
    "3.1.2": "Unmarked language changes cause incorrect screen-reader pronunciation.",
    "3.2.3": "Inconsistent navigation makes it harder to predict where things are.",
    "3.2.4": "Inconsistent identification of controls makes repeated tasks error-prone.",
    "3.3.3": "Errors without suggestions leave people unsure how to recover.",
    "3.3.4": "Irreversible legal, financial or data actions without confirmation risk serious loss.",
    "3.3.8": "Cognitive tests or puzzles can block people with cognitive disabilities from authenticating.",
    "4.1.3": "Status messages that are not announced leave screen-reader users unaware of changes.",
    "1.2.6": "Sign-language users may not understand prerecorded audio without sign-language interpretation.",
    "1.2.7": "Extended visual information may not fit into standard audio-description pauses.",
    "1.2.8": "Complex media without a full text alternative may be inaccessible.",
    "1.2.9": "Live audio without captions excludes people who cannot hear it.",
    "1.3.6": "Controls without programmatic purpose cannot support personalisation or assistive technology.",
    "1.4.6": "Higher contrast needs may not be met by minimum contrast alone.",
    "1.4.7": "Background noise can make speech hard to understand for hard-of-hearing users.",
    "1.4.8": "Fixed line length, alignment and spacing can make text hard to read.",
    "1.4.9": "Images of text cannot be adapted to individual reading needs.",
    "2.1.3": "Any pointer-only operation can exclude keyboard-only users.",
    "2.2.3": "Any time limit can prevent task completion for people who need more time.",
    "2.2.4": "Uncontrollable interruptions break attention and task continuity.",
    "2.2.5": "Losing data on re-authentication forces people to repeat work.",
    "2.2.6": "Unexpected timeouts can cause data loss and confusion.",
    "2.3.2": "Flashing above the general threshold can trigger seizures.",
    "2.3.3": "Motion triggered by interaction can cause dizziness or nausea.",
    "2.4.8": "Without location cues, people may not know where they are in a site.",
    "2.4.9": "Link text that is ambiguous without context makes destinations unclear.",
    "2.4.10": "Missing section headings make long content harder to scan and navigate.",
    "2.4.12": "Focus can be hidden by additional visual content, not just the minimum overlays.",
    "2.4.13": "Insufficient focus appearance makes keyboard focus hard to perceive.",
    "2.5.5": "Even larger targets may be insufficient for people with significant dexterity limits.",
    "2.5.6": "Restricting input to one mechanism excludes people who switch methods.",
    "3.1.3": "Unusual words and idioms can be misunderstood without definitions.",
    "3.1.4": "Unexpanded abbreviations can be unclear to people with cognitive or language differences.",
    "3.1.5": "Complex text can be inaccessible without a simpler version or support.",
    "3.1.6": "Ambiguous pronunciation can make text unclear when read aloud.",
    "3.2.5": "Unexpected context changes can disorient people who did not request them.",
    "3.3.5": "Without help, people may not know how to complete a task.",
    "3.3.6": "Without review or confirmation, errors in important submissions can cause loss.",
    "3.3.9": "Even enhanced authentication can block people who cannot solve cognitive tests.",
}
INTRO_2_1 = {"1.3.4", "1.3.5", "1.3.6", "1.4.10", "1.4.11", "1.4.12", "1.4.13", "2.1.4", "2.2.6", "2.5.1", "2.5.2", "2.5.3", "2.5.4", "2.5.5", "2.5.6", "4.1.3"}
INTRO_2_2 = {"2.4.11", "2.4.12", "2.4.13", "2.5.7", "2.5.8", "3.2.6", "3.3.7", "3.3.8", "3.3.9"}


def fpc_categories():
    mapping = {}
    with open(ROOT / "config" / "fpc-wcag-mapping.csv", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            criterion = (row.get("WCAG 2.0 SC") or "").split(" ", 1)[0]
            categories = [key for key, column in {
                "WV": "Without Vision (WV)", "LV": "Limited Vision (LV)",
                "WPC": "Without Perception of Color (WPC)", "WH": "Without Hearing (WH)",
                "LH": "Limited Hearing (LH)", "WS": "Without Speech (WS)",
                "LM": "Limited Manipulation (LM)", "LRS": "Limited Reach and Strength (LRS)",
                "LLCLA": "Limited Language, Cognitive, and Learning Abilities (LLCLA)",
            }.items() if (row.get(column) or "").strip()]
            mapping[criterion] = categories
    return mapping


def groups_for(criterion, fpc):
    groups = MISSING_GROUPS.get(criterion)
    if groups:
        return groups
    result = []
    for key in fpc.get(criterion, []):
        result.extend(GROUPS.get(key, []))
    return sorted(set(result))


SHORT_GROUP_LABELS = {
    "blind": "blind people",
    "low_vision": "people with low vision",
    "color_vision_deficiency": "people with colour vision deficiency",
    "deaf": "Deaf people",
    "hard_of_hearing": "hard-of-hearing people",
    "deafblind": "Deafblind people",
    "speech_disability": "people with speech disabilities",
    "mobility_disability": "people with mobility disabilities",
    "limited_dexterity": "people with limited dexterity or tremor",
    "cognitive_disability": "people with cognitive disabilities",
    "learning_disability": "people with learning disabilities",
    "photosensitive_epilepsy": "people with photosensitive epilepsy",
    "vestibular_disorder": "people with vestibular disorders",
}


def main():
    catalog = load_catalog()
    vocab = json.loads((DATA / "schema" / "groups.json").read_text(encoding="utf-8"))
    fpc = fpc_categories()
    active = []
    historical = []
    for chapter in catalog["chapters"]:
        if not chapter["id"].startswith("success_criteria"):
            continue
        for criterion in chapter.get("criteria") or []:
            cid = str(criterion["id"])
            level = {"success_criteria_level_a": "A", "success_criteria_level_aa": "AA", "success_criteria_level_aaa": "AAA"}[chapter["id"]]
            barrier = BARRIERS.get(cid)
            if cid == "4.1.1":
                historical.append({
                    "id": cid, "title": criterion.get("handle"), "level": level,
                    "introduced_in": "2.0", "removed_in": "2.2", "status": "removed",
                    "user_impact": {"groups": ["blind", "low_vision", "cognitive_disability"],
                                    "functional_needs": ["assistive_technology_compatibility"],
                                    "barrier": barrier or "Historical Parsing criterion; removed from WCAG 2.2.",
                                    "description": "WCAG 4.1.1 Parsing was removed from WCAG 2.2. It is retained for historical WCAG 2.0/2.1 references."},
                    "sources": [{"type": "w3c_understanding", "url": "https://www.w3.org/WAI/WCAG22/Understanding/parsing.html"}],
                    "standards_mappings": {"section508_fpc": {"status": "reviewed", "categories": fpc.get(cid, [])}, "en301549": {"v3.2.1": "pending", "v4.1.1": "pending"}},
                    "review_status": "reviewed", "last_reviewed": "2026-11-12",
                })
                continue
            if not barrier:
                raise SystemExit(f"missing barrier for {cid}")
            groups = groups_for(cid, fpc) or ["cognitive_disability"]
            needs = sorted({need for group in groups for need in vocab["groups"][group]["functional_needs"]})
            def phrase(group):
                label = vocab["groups"][group]["label"]
                if label == "People who are blind":
                    return "blind people"
                if label.startswith("People with "):
                    return "people with " + label[len("People with "):]
                return label[0].lower() + label[1:]
            label = ", ".join(phrase(group) for group in groups)
            active.append({
                "id": cid,
                "title": criterion.get("handle") or "",
                "level": level,
                "introduced_in": "2.2" if cid in INTRO_2_2 else ("2.1" if cid in INTRO_2_1 else "2.0"),
                "status": "active",
                "user_impact": {
                    "groups": groups,
                    "functional_needs": needs,
                    "affects_short": "; ".join(SHORT_GROUP_LABELS[group] for group in groups),
                    "barrier_short": barrier,
                    "barrier": barrier,
                    "description": f"{barrier} This can affect {label}.",
                },
                "sources": [{
                    "type": "w3c_understanding",
                    "url": f"https://www.w3.org/WAI/WCAG22/Understanding/{criterion.get('alt_id') or ''}.html",
                    "title": f"Understanding {cid} {criterion.get('handle') or ''}",
                }],
                "standards_mappings": {
                    "section508_fpc": {"status": "reviewed" if fpc.get(cid) else "reviewed-no-mapping", "categories": fpc.get(cid, [])},
                    "en301549": {"v3.2.1": "pending", "v4.1.1": "pending"},
                },
                "review_status": "proposed",
                "last_reviewed": None,
            })
    if len(active) != 86:
        raise SystemExit(f"expected 86 active criteria, got {len(active)}")
    section508 = json.loads((DATA / "mappings" / "section508-fpc.json").read_text(encoding="utf-8"))
    section508["criteria"] = {
        item["id"]: item["standards_mappings"]["section508_fpc"]
        for item in active
        if item["standards_mappings"]["section508_fpc"].get("categories")
    }
    (DATA / "mappings" / "section508-fpc.json").write_text(json.dumps(section508, indent=2) + "\n", encoding="utf-8")
    (DATA / "wcag" / "2.2" / "criteria.json").write_text(json.dumps({"standard": "WCAG 2.2", "active_criteria": active}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (DATA / "wcag" / "2.2" / "historical.json").write_text(json.dumps({"standard": "WCAG", "historical_criteria": historical}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(active)} active and {len(historical)} historical records")


if __name__ == "__main__":
    main()
