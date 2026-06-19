from services.ats_skill_matching import match_skills
from services.ats_section_coverage import analyze_section_coverage
from services.ats_tfidf_similarity import analyze_content_similarity


# Layer weights — tunable. Reflects each layer's relative reliability,
# as established through testing: structured/exact signals (Layers 1, 2)
# carry the real weight; TF-IDF (Layer 3) is a low-weight independent
# sanity check, not a precision instrument.
LAYER_WEIGHTS = {
    "skill_match": 0.50,
    "section_coverage": 0.35,
    "content_similarity": 0.15
}


def compute_ats_score(
    resume_parsed_data: dict,
    resume_deterministic: dict,
    resume_raw_text: str,
    jd_parsed_data: dict,
    jd_deterministic: dict,
    jd_raw_text: str
) -> dict:
    """
    Runs all three ATS layers and combines them into one unified score
    plus a structured breakdown. This breakdown is the direct input
    for the tailoring agent — every gap identified here maps to a
    specific, actionable suggestion downstream.
    """

    # ── Layer 1: Deterministic skill matching ──
    layer1 = match_skills(
        resume_skills=resume_parsed_data.get("skills", []),
        required_skills=jd_parsed_data.get("required_skills", []),
        preferred_skills=jd_parsed_data.get("preferred_skills", [])
    )

    # ── Layer 2: Section/structural alignment ──
    layer2 = analyze_section_coverage(
        resume_parsed_data=resume_parsed_data,
        resume_deterministic=resume_deterministic,
        jd_parsed_data=jd_parsed_data,
        jd_raw_text=jd_raw_text
    )

    # ── Layer 3: TF-IDF content similarity ──
    layer3 = analyze_content_similarity(
        resume_sections=resume_deterministic.get("sections", {}),
        jd_sections=jd_deterministic.get("sections", {}),
        resume_raw_text=resume_raw_text,
        jd_raw_text=jd_raw_text
    )

    # ── Combine into final score ──
    # Layer 3's score is 0-1 (cosine similarity), Layers 1 and 2 are 0-100.
    # Normalize Layer 3 to the same 0-100 scale before combining.
    layer3_normalized = layer3["layer3_score"] * 100

    final_score = round(
        (layer1["layer1_score"] * LAYER_WEIGHTS["skill_match"]) +
        (layer2["layer2_score"] * LAYER_WEIGHTS["section_coverage"]) +
        (layer3_normalized * LAYER_WEIGHTS["content_similarity"])
    )

    # ── Build the actionable gap summary ──
    # This is what the tailoring agent actually consumes — every item
    # here should be specific enough to generate a concrete suggestion.
    gaps = []

    if layer1["required_skills"]["missing"]:
        gaps.append({
            "type": "missing_required_skill",
            "severity": "high",
            "items": layer1["required_skills"]["missing"],
            "suggestion": "Add these skills if you have relevant experience with them, "
                           "or consider a learning roadmap to acquire them."
        })

    if layer1["preferred_skills"]["missing"]:
        gaps.append({
            "type": "missing_preferred_skill",
            "severity": "low",
            "items": layer1["preferred_skills"]["missing"],
            "suggestion": "These are bonus skills the JD mentions — not essential, "
                           "but worth highlighting if you have any exposure to them."
        })

    for penalty in layer2["penalties"]:
        gaps.append({
            "type": f"structural_{penalty['area']}",
            "severity": penalty["severity"],
            "items": [penalty["issue"]],
            "suggestion": _suggestion_for_area(penalty["area"])
        })

    return {
        "final_score": final_score,
        "layer_breakdown": {
            "skill_match": {
                "score": layer1["layer1_score"],
                "weight": LAYER_WEIGHTS["skill_match"]
            },
            "section_coverage": {
                "score": layer2["layer2_score"],
                "weight": LAYER_WEIGHTS["section_coverage"]
            },
            "content_similarity": {
                "score": round(layer3_normalized, 1),
                "weight": LAYER_WEIGHTS["content_similarity"]
            }
        },
        "skill_analysis": {
            "matched_required": layer1["required_skills"]["matched"],
            "missing_required": layer1["required_skills"]["missing"],
            "matched_preferred": layer1["preferred_skills"]["matched"],
            "missing_preferred": layer1["preferred_skills"]["missing"],
            "bonus_skills": layer1["bonus_skills"]
        },
        "structural_analysis": layer2["checks"],
        "content_similarity_detail": layer3["breakdown"],
        "gaps": sorted(gaps, key=lambda g: {"high": 0, "medium": 1, "low": 2}[g["severity"]])
    }


def _suggestion_for_area(area: str) -> str:
    """
    Maps a structural gap area to a concrete, human-readable suggestion.
    Kept separate from the penalty detection logic so the wording can
    be refined independently of the detection rules.
    """
    suggestions = {
        "experience": "Consider expanding on relevant experience, or emphasize "
                      "transferable experience from projects if work history is limited.",
        "education": "Ensure your education section clearly states your degree "
                     "and institution if the JD specifies a degree requirement.",
        "certifications": "Consider pursuing a relevant certification, or highlight "
                          "any existing certifications more prominently.",
        "leadership": "Highlight any team coordination, mentoring, or ownership "
                      "experience from your projects or roles, even informal leadership.",
        "skills": "Add a dedicated, clearly labeled skills section if one doesn't exist."
    }
    return suggestions.get(area, "Review this area for alignment with the job description.")