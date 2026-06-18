from rapidfuzz import fuzz

# ---------- NORMALIZATION ----------

# Canonical alias map — maps known variants to one standard form.
# Key = variant (lowercase), value = canonical form (lowercase).
# Extend this as you encounter new variations in real resumes/JDs.

SKILL_ALIASES = {
    # JavaScript ecosystem
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",
    "node.js": "node",
    "nodejs": "node",
    "node js": "node",
    "next.js": "nextjs",
    "vue.js": "vue",
    "vuejs": "vue",
    "express.js": "express",
    "expressjs": "express",

    # Python ecosystem
    "ml": "machine learning",
    "ai/ml": "machine learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "dl": "deep learning",
    "scikit-learn": "sklearn",
    "scikit learn": "sklearn",

    # Databases
    "postgresql": "postgres",
    "mongo": "mongodb",
    "mongo db": "mongodb",

    # DevOps / Cloud
    "amazon web services": "aws",
    "google cloud platform": "gcp",
    "google cloud": "gcp",
    "microsoft azure": "azure",
    "k8s": "kubernetes",
    "docker compose": "docker",

    # Mobile
    "swiftui": "swift",
    "swift ui": "swift",

    # General
    "c plus plus": "c++",
    "cplusplus": "c++",
    "golang": "go",
    "js": "javascript",
    "ts": "typescript",
    "llm": "large language models",
    "llms": "large language models",
    "rest api": "rest",
    "restful api": "rest",
    "restful": "rest",
    "ui/ux": "ux design",
    "ui ux": "ux design",
    "rest apis": "rest",
    "rest api": "rest",
    "restful apis": "rest",
    "restful api": "rest",
    "restful": "rest",
}


def normalize_skill(skill: str) -> str:
    """
    Lowercases and resolves known aliases to their canonical form.
    "React.js" → "react", "ML" → "machine learning", etc.
    Skills not in the alias map are just lowercased and stripped.
    """
    cleaned = skill.lower().strip()
    return SKILL_ALIASES.get(cleaned, cleaned)


def normalize_skill_list(skills: list[str]) -> list[str]:
    """
    Normalizes a full list and deduplicates — so if a resume lists
    both "React" and "React.js", they collapse to one canonical "react"
    rather than appearing to be two separate skills.
    """
    seen = set()
    result = []
    for skill in skills:
        normalized = normalize_skill(skill)
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


# ---------- FUZZY MATCHING ----------

FUZZY_MATCH_THRESHOLD = 85  # 0-100 — below this score we don't count it as a match

def fuzzy_match(skill: str, candidates: list[str]) -> tuple[str | None, int]:
    """
    Finds the best fuzzy match for a skill in a list of candidates.
    Returns (best_match, score) or (None, 0) if nothing clears the threshold.

    Why fuzzy matching on top of alias normalization?
    The alias map catches known variants. Fuzzy matching catches
    everything else — typos, slight rephrasing, things no alias
    map could anticipate. Together they cover the full spectrum
    of real-world skill naming inconsistency.
    """
    best_match = None
    best_score = 0

    for candidate in candidates:
        # token_sort_ratio handles word-order differences:
        # "python data analysis" vs "data analysis python" → 100
        score = fuzz.token_sort_ratio(skill, candidate)
        if score > best_score:
            best_score = score
            best_match = candidate

    if best_score >= FUZZY_MATCH_THRESHOLD:
        return best_match, best_score

    return None, 0


# ---------- CORE MATCHING LOGIC ----------

def match_skills(
    resume_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str]
) -> dict:
    """
    Main Layer 1 function. Compares resume skills against JD required
    and preferred skills using normalized exact matching + fuzzy fallback.

    Returns a structured breakdown — not just a score, but named lists
    of matched/missing skills that the tailoring agent can act on directly.
    """

    # Normalize all three lists before any comparison
    norm_resume    = normalize_skill_list(resume_skills)
    norm_required  = normalize_skill_list(required_skills)
    norm_preferred = normalize_skill_list(preferred_skills)

    matched_required  = []
    missing_required  = []
    matched_preferred = []
    missing_preferred = []
    fuzzy_matches     = []  # skills matched via fuzzy, not exact — worth tracking separately

    # --- Required skills ---
    for req_skill in norm_required:
        if req_skill in norm_resume:
            # Exact match after normalization
            matched_required.append(req_skill)
        else:
            # Try fuzzy match as fallback
            fuzzy_result, score = fuzzy_match(req_skill, norm_resume)
            if fuzzy_result:
                matched_required.append(req_skill)
                fuzzy_matches.append({
                    "jd_skill": req_skill,
                    "resume_skill": fuzzy_result,
                    "score": score
                })
            else:
                missing_required.append(req_skill)

    # --- Preferred skills ---
    for pref_skill in norm_preferred:
        if pref_skill in norm_resume:
            matched_preferred.append(pref_skill)
        else:
            fuzzy_result, score = fuzzy_match(pref_skill, norm_resume)
            if fuzzy_result:
                matched_preferred.append(pref_skill)
                fuzzy_matches.append({
                    "jd_skill": pref_skill,
                    "resume_skill": fuzzy_result,
                    "score": score
                })
            else:
                missing_preferred.append(pref_skill)

    # --- Bonus skills ---
    # Skills the candidate has that aren't in the JD at all —
    # useful context for the tailoring agent ("you have Swift experience
    # but this JD doesn't mention it — probably not worth emphasizing")
    all_jd_skills = set(norm_required + norm_preferred)
    bonus_skills = [s for s in norm_resume if s not in all_jd_skills]

    # --- Score calculation ---
    # Required skills weighted at 70%, preferred at 30%
    # Fuzzy matches count as full matches for scoring — they represent
    # real skills, just with inconsistent naming
    required_score = (
        len(matched_required) / len(norm_required) * 100
        if norm_required else 100  # no required skills = full score by default
    )

    preferred_score = (
        len(matched_preferred) / len(norm_preferred) * 100
        if norm_preferred else 100
    )

    layer1_score = round(
        (required_score * 0.70) + (preferred_score * 0.30)
    )

    return {
        "layer1_score": layer1_score,
        "required_skills": {
            "matched": matched_required,
            "missing": missing_required,
            "total": len(norm_required),
            "match_rate": round(required_score, 1)
        },
        "preferred_skills": {
            "matched": matched_preferred,
            "missing": missing_preferred,
            "total": len(norm_preferred),
            "match_rate": round(preferred_score, 1)
        },
        "bonus_skills": bonus_skills,
        "fuzzy_matches": fuzzy_matches  # transparency — show which matches were fuzzy
    }