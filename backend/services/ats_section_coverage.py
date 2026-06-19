import re

# ---------- CONFIGURATION ----------

# Which JD fields signal emphasis on each structural area.
# Used to check whether the JD actually cares about a given section
# before penalizing the resume for not having/matching it.

SECTION_SIGNALS = {
    "experience": {
        "jd_fields": ["responsibilities", "qualifications", "required_skills"],
        "resume_section": "experience",
        "weight": 0.35
    },
    "education": {
        "jd_fields": ["qualifications"],
        "resume_section": "education",
        "weight": 0.20
    },
    "certifications": {
        "jd_fields": ["required_skills", "preferred_skills", "qualifications"],
        "resume_section": "certification",
        "weight": 0.15
    },
    "projects": {
        "jd_fields": ["responsibilities", "required_skills"],
        "resume_section": "projects",
        "weight": 0.15
    },
    "skills": {
        "jd_fields": ["required_skills", "preferred_skills"],
        "resume_section": "technical skills",
        "weight": 0.15
    }
}

# Keywords that signal the JD requires leadership/management
LEADERSHIP_SIGNALS = [
    "lead", "leads", "leading", "manager", "manage", "manages",
    "managing", "head of", "director", "principal", "mentor",
    "mentoring", "team lead", "tech lead"
]

# Keywords that signal the JD requires a specific degree
DEGREE_SIGNALS = [
    "bachelor", "b.tech", "b.e", "master", "m.tech", "phd",
    "degree in", "graduate", "undergraduate", "bs ", "ms ",
    "computer science", "engineering degree"
]

# Keywords that signal the JD requires certifications
CERTIFICATION_SIGNALS = [
    "certified", "certification", "certificate", "aws certified",
    "azure", "gcp certified", "pmp", "cissp", "comptia"
]

# Patterns to extract years of experience from JD text
YEARS_EXPERIENCE_PATTERNS = [
    re.compile(r"(\d+)\+?\s*years?\s+(?:of\s+)?experience", re.IGNORECASE),
    re.compile(r"(\d+)\+?\s*yrs?\s+(?:of\s+)?experience", re.IGNORECASE),
    re.compile(r"minimum\s+(?:of\s+)?(\d+)\s+years?", re.IGNORECASE),
    re.compile(r"at\s+least\s+(\d+)\s+years?", re.IGNORECASE),
]

# Patterns to extract years from resume date ranges
RESUME_DATE_PATTERNS = [
    re.compile(r"(\d{4})\s*[-–—]\s*(\d{4})", re.IGNORECASE),
    re.compile(r"(\d{2}/\d{4})\s*[-–—]\s*(\d{2}/\d{4})", re.IGNORECASE),
    re.compile(r"(\d{4})\s*[-–—]\s*(present|current)", re.IGNORECASE),
    re.compile(r"(\d{2}/\d{4})\s*[-–—]?\s*(present|current)", re.IGNORECASE),
]


# ---------- HELPER FUNCTIONS ----------

def extract_years_required(jd_raw_text: str) -> float | None:
    """
    Pulls the minimum years of experience requirement from JD text.
    Returns the highest number found (in case multiple are mentioned
    for different requirements) as a float, or None if not specified.
    """
    years_found = []
    for pattern in YEARS_EXPERIENCE_PATTERNS:
        for match in pattern.finditer(jd_raw_text):
            try:
                years_found.append(float(match.group(1)))
            except ValueError:
                continue

    return max(years_found) if years_found else None


def estimate_resume_years(resume_dates: list[str], resume_raw_text: str) -> float:
    """
    Estimates total years of professional experience from resume date ranges.
    Uses the dates extracted by Phase 1's deterministic extraction.

    This is an approximation — overlapping roles or gaps aren't handled
    perfectly, but it's directionally accurate for scoring purposes.
    """
    from datetime import datetime

    total_months = 0
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Try to find date ranges in the raw experience text
    experience_text = resume_raw_text

    for pattern in RESUME_DATE_PATTERNS:
        for match in pattern.finditer(experience_text):
            try:
                start_str = match.group(1)
                end_str = match.group(2)

                # Parse start date
                if "/" in start_str:
                    parts = start_str.split("/")
                    start_month, start_year = int(parts[0]), int(parts[1])
                else:
                    start_month, start_year = 1, int(start_str)

                # Parse end date — handle "present/current"
                if end_str.lower() in ("present", "current"):
                    end_month, end_year = current_month, current_year
                elif "/" in end_str:
                    parts = end_str.split("/")
                    end_month, end_year = int(parts[0]), int(parts[1])
                else:
                    end_month, end_year = 12, int(end_str)

                months = (end_year - start_year) * 12 + (end_month - start_month)
                if months > 0:
                    total_months += months

            except (ValueError, IndexError):
                continue

    return round(total_months / 12, 1)


def jd_requires_certifications(jd_parsed_data: dict) -> bool:
    """
    Checks whether the JD explicitly mentions certifications
    in its required skills, preferred skills, or qualifications.
    """
    fields_to_check = (
        jd_parsed_data.get("required_skills", []) +
        jd_parsed_data.get("preferred_skills", []) +
        jd_parsed_data.get("qualifications", [])
    )
    combined = " ".join(fields_to_check).lower()
    return any(signal in combined for signal in CERTIFICATION_SIGNALS)


def jd_requires_leadership(jd_parsed_data: dict) -> bool:
    """
    Checks whether the JD signals a leadership/management expectation
    in its responsibilities or qualifications.
    """
    fields_to_check = (
        jd_parsed_data.get("responsibilities", []) +
        jd_parsed_data.get("qualifications", [])
    )
    combined = " ".join(fields_to_check).lower()
    return any(signal in combined for signal in LEADERSHIP_SIGNALS)


def jd_requires_degree(jd_parsed_data: dict) -> bool:
    """
    Checks whether the JD specifies a degree requirement.
    """
    qualifications = jd_parsed_data.get("qualifications", [])
    combined = " ".join(qualifications).lower()
    return any(signal in combined for signal in DEGREE_SIGNALS)


def resume_has_leadership_evidence(resume_parsed_data: dict) -> bool:
    """
    Checks whether the resume's experience bullets contain
    leadership signals — managing people, leading teams etc.
    """
    experience = resume_parsed_data.get("experience", [])
    all_bullets = []
    for role in experience:
        all_bullets.extend(role.get("bullets", []))

    combined = " ".join(all_bullets).lower()
    return any(signal in combined for signal in LEADERSHIP_SIGNALS)


# ---------- MAIN LAYER 2 FUNCTION ----------

def analyze_section_coverage(
    resume_parsed_data: dict,
    resume_deterministic: dict,
    jd_parsed_data: dict,
    jd_raw_text: str
) -> dict:
    """
    Layer 2 — structural alignment check.
    Evaluates whether the resume's sections align with what the JD
    emphasizes, rather than just checking if sections exist.
    """

    sections = resume_deterministic.get("sections", {})
    resume_dates = resume_deterministic.get("dates", [])
    resume_raw_text = " ".join(sections.values())

    checks = {}
    penalties = []

    # ── CHECK 1: Experience section exists and has content ──
    experience_content = sections.get("experience", "").strip()
    has_experience = len(experience_content) > 50  # more than a stub

    checks["has_experience_section"] = has_experience
    if not has_experience:
        penalties.append({
            "area": "experience",
            "issue": "No experience section found or section is empty.",
            "severity": "high"
        })

    # ── CHECK 2: Years of experience vs JD requirement ──
    years_required = extract_years_required(jd_raw_text)
    years_detected = estimate_resume_years(resume_dates, resume_raw_text)

    checks["years_required"] = years_required
    checks["years_detected"] = years_detected

    years_gap = False
    if years_required and years_detected < years_required:
        years_gap = True
        penalties.append({
            "area": "experience",
            "issue": f"JD requires {years_required}+ years, resume shows approximately {years_detected} years.",
            "severity": "high"
        })

    checks["years_gap"] = years_gap

    # ── CHECK 3: Education section ──
    education_content = resume_parsed_data.get("education", [])
    has_education = len(education_content) > 0
    jd_needs_degree = jd_requires_degree(jd_parsed_data)

    checks["has_education"] = has_education
    checks["jd_requires_degree"] = jd_needs_degree

    if jd_needs_degree and not has_education:
        penalties.append({
            "area": "education",
            "issue": "JD specifies a degree requirement but no education section found.",
            "severity": "high"
        })

    # ── CHECK 4: Certifications ──
    resume_certs = resume_parsed_data.get("certifications", [])
    has_certifications = len(resume_certs) > 0
    jd_needs_certs = jd_requires_certifications(jd_parsed_data)

    checks["has_certifications"] = has_certifications
    checks["jd_emphasizes_certifications"] = jd_needs_certs

    if jd_needs_certs and not has_certifications:
        penalties.append({
            "area": "certifications",
            "issue": "JD emphasizes certifications but none found in resume.",
            "severity": "medium"
        })

    # ── CHECK 5: Projects section ──
    projects = resume_parsed_data.get("projects", [])
    has_projects = len(projects) > 0

    checks["has_projects"] = has_projects

    # ── CHECK 6: Skills section ──
    skills_content = sections.get("technical skills", "").strip()
    has_skills_section = len(skills_content) > 20

    checks["has_skills_section"] = has_skills_section
    if not has_skills_section:
        penalties.append({
            "area": "skills",
            "issue": "No dedicated skills section found.",
            "severity": "low"
        })

    # ── CHECK 7: Leadership signals ──
    jd_needs_leadership = jd_requires_leadership(jd_parsed_data)
    resume_has_leadership = resume_has_leadership_evidence(resume_parsed_data)

    checks["jd_requires_leadership"] = jd_needs_leadership
    checks["resume_shows_leadership"] = resume_has_leadership

    if jd_needs_leadership and not resume_has_leadership:
        penalties.append({
            "area": "leadership",
            "issue": "JD expects leadership/management experience but no evidence found in resume.",
            "severity": "medium"
        })

    # ── SCORE CALCULATION ──
    # Start at 100, deduct for penalties by severity
    severity_weights = {"high": 20, "medium": 10, "low": 5}
    raw_score = 100

    for penalty in penalties:
        raw_score -= severity_weights[penalty["severity"]]

    layer2_score = max(0, raw_score)  # floor at 0

    return {
        "layer2_score": layer2_score,
        "checks": checks,
        "penalties": penalties,
        "summary": {
            "total_penalties": len(penalties),
            "high_severity": sum(1 for p in penalties if p["severity"] == "high"),
            "medium_severity": sum(1 for p in penalties if p["severity"] == "medium"),
            "low_severity": sum(1 for p in penalties if p["severity"] == "low")
        }
    }