"""
Local AI-like utilities for doctor workflows without external dependencies.
These functions use simple heuristics/templates to generate useful content while
keeping all processing offline and ensuring stable backend startup.
"""
from __future__ import annotations
from typing import List, Dict


def _fmt_lines(lines: List[str]) -> str:
    return "\n".join(f"- {ln}" for ln in lines if ln)


def analyze_symptoms_ai(symptoms: str, age: str | int = "", gender: str = "", medical_history: str = "") -> str:
    parts = [
        "Possible diagnoses:",
        _fmt_lines([
            "Refractive error (myopia/hyperopia/astigmatism) likely" if any(k in symptoms.lower() for k in ["blur", "blurry", "headache"]) else "",
            "Dry eye syndrome" if any(k in symptoms.lower() for k in ["dry", "itch", "burn"]) else "",
            "Allergic conjunctivitis" if any(k in symptoms.lower() for k in ["red", "itch", "allergy"]) else "",
        ]),
        "\nRecommended tests/examinations:",
        _fmt_lines([
            "Visual acuity and refraction",
            "Slit-lamp examination",
            "Schirmer test if dryness suspected",
        ]),
        "\nTreatment suggestions:",
        _fmt_lines([
            "Artificial tears QID for dryness",
            "Cool compress and antihistamine drops for allergy",
            "Advise regular breaks and proper lighting",
        ]),
        "\nWhen to seek immediate care:",
        _fmt_lines([
            "Sudden loss of vision",
            "Severe eye pain",
            "Trauma or chemical exposure",
        ]),
    ]
    return "\n".join(p for p in parts if p)


def suggest_medications_ai(diagnosis: str, age: str | int = "", allergies: str = "") -> str:
    diag = diagnosis.lower()
    lines: List[str] = []
    if "dry" in diag:
        lines += [
            "Carboxymethylcellulose 0.5%: 1 drop QID OU for 2-4 weeks",
            "Consider gel at night if symptoms persist",
        ]
    if "allerg" in diag:
        lines += [
            "Olopatadine 0.1%: 1 drop BID OU for 2 weeks",
            "Avoid rubbing eyes and use cool compress",
        ]
    if not lines:
        lines = [
            "Use lubricating drops QID",
            "Re-evaluate in 1-2 weeks or sooner if worse",
        ]
    return _fmt_lines(lines)


def analyze_prescription_interactions(medications: List[str]) -> str:
    meds = [m.strip().lower() for m in medications]
    warnings: List[str] = []
    # Simple duplicate/overlap check
    if len(set(meds)) != len(meds):
        warnings.append("Duplicate medication detected; verify dosing schedule.")
    # Example simplistic caution
    if any("steroid" in m for m in meds) and any("antibiotic" in m for m in meds):
        warnings.append("Steroid + antibiotic combo: ensure indication and monitor IOP.")
    if not warnings:
        warnings.append("No significant interactions detected based on provided list.")
    return _fmt_lines(warnings)


def generate_patient_education_ai(condition: str, treatment: str) -> str:
    return (
        f"About {condition}:\n"
        f"- This condition affects the surface or internal structures of the eye.\n"
        f"- Follow the prescribed treatment: {treatment}.\n\n"
        "How to use medications:\n"
        "- Wash hands before use.\n"
        "- Tilt head back and avoid touching the dropper tip.\n\n"
        "Do's and Don'ts:\n"
        "- Do rest your eyes and stay hydrated.\n"
        "- Don't rub your eyes.\n\n"
        "When to contact the doctor:\n"
        "- Worsening pain, redness, or vision changes.\n\n"
        "Expected recovery:\n"
        "- Many symptoms improve within 1-2 weeks; follow-up as advised."
    )


def smart_inventory_suggestions(current_inventory: Dict[str, int], patient_demographics: str) -> str:
    low_stock = [name for name, qty in current_inventory.items() if qty <= 2]
    lines = [
        "Reorder recommendations:",
        _fmt_lines([f"{name}: reorder to minimum 10" for name in low_stock]) or "- Stock levels are adequate.",
        "\nSeasonal considerations:",
        "- Allergy season: consider more lubricants and antihistamine drops.",
        "\nCost-effective alternatives:",
        "- Offer generic lubricants and frames with popular sizes.",
    ]
    return "\n".join(lines)
