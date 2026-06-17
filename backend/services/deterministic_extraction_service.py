import re
import spacy
import phonenumbers

# Load once at module level — loading spaCy's model is expensive,
# you don't want this running on every request
nlp = spacy.load("en_core_web_sm")


# ---------- SECTION HEADER DEFINITIONS ----------
# doc_type-aware — resume and JD have different vocabularies for sections

RESUME_HEADERS = [
    "summary", "objective", "experience", "work experience",
    "education", "skills", "technical skills", "projects",
    "certification", "certifications", "achievements", "publications"
]

JD_HEADERS = [
    "responsibilities", "requirements", "qualifications",
    "about the role", "about us", "benefits", "what you'll do",
    "what we're looking for", "nice to have", "preferred qualifications"
]


# ---------- REGEX PATTERNS ----------

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

LINKEDIN_PATTERN = re.compile(r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9-]+/?", re.IGNORECASE)

GITHUB_PATTERN = re.compile(r"(https?://)?(www\.)?github\.com/[a-zA-Z0-9-]+/?", re.IGNORECASE)


DATE_RANGE_PATTERN = re.compile(
    r"(\b\d{1,2}/\d{4}\b|\b[A-Za-z]{3,9}\s\d{4}\b|\b\d{4}\b)"
    r"\s*(?:[-–—]\s*)?"
    r"(\b\d{1,2}/\d{4}\b|\b[A-Za-z]{3,9}\s\d{4}\b|\b\d{4}\b|present|current)",
    re.IGNORECASE
)


SINGLE_DATE_PATTERN = re.compile(
    r"\b\d{1,2}/\d{4}\b|\b[A-Za-z]{3,9}\s\d{4}\b",
    re.IGNORECASE
)
def categorize_links(hyperlinks: list[str]) -> dict:
    """
    Splits hyperlinks into identity links (LinkedIn, portfolio, GitHub
    profile) vs reference links (project repos, demos, app store, drive).
    Most resumes only contain reference links for projects — a GitHub
    PROFILE link is actually fairly rare unless explicitly added near
    the contact info.
    """
    linkedin = None
    portfolio = None
    github_profile = None
    project_links = []

    for link in hyperlinks:
        lower = link.lower()

        if "linkedin.com" in lower:
            linkedin = link

        elif "github.com" in lower:
            path_parts = link.split("github.com/")[-1].strip("/").split("/")
            if len(path_parts) == 1:
                # github.com/username — no repo name after it = profile
                github_profile = link
            else:
                # github.com/username/repo-name = project reference
                project_links.append(link)

        elif any(domain in lower for domain in ["vercel.app", "netlify.app", "github.io"]):
            portfolio = link

        else:
            # drive.google.com, apps.apple.com, etc. — project evidence
            project_links.append(link)

    return {
        "linkedin": linkedin,
        "portfolio": portfolio,
        "github_profile": github_profile,
        "project_links": list(set(project_links))  # dedupe repeated links
    }

def extract_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None

def extract_phone(text: str) -> str | None:
    """
    Restricts phone search to the first 400 characters — the contact
    info header — rather than the full document. Scanning the entire
    resume risks false positives where digit sequences inside dates
    or other numeric fields (e.g. "03/2026-04/2026") get misread as
    valid-shaped phone numbers purely by coincidence.
    """
    header_text = text[:400]

    for match in phonenumbers.PhoneNumberMatcher(header_text, "IN"):
        number = match.number
        if phonenumbers.is_valid_number(number):
            return phonenumbers.format_number(
                number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
    return None

def extract_linkedin(text: str, hyperlinks: list[str] = None) -> str | None:
    match = LINKEDIN_PATTERN.search(text)
    if match:
        return match.group(0)

    # Fall back to checking actual hyperlink targets — catches cases
    # where the resume shows "LinkedIn" as a clickable label only
    if hyperlinks:
        for link in hyperlinks:
            if "linkedin.com" in link.lower():
                return link

    return None


def extract_github(text: str, hyperlinks: list[str] = None) -> str | None:
    match = GITHUB_PATTERN.search(text)
    if match:
        return match.group(0)

    if hyperlinks:
        github_links = [link for link in hyperlinks if "github.com" in link.lower()]

        for link in github_links:
            path_parts = link.split("github.com/")[-1].strip("/").split("/")
            if len(path_parts) == 1:  # just "username", no repo name after it
                return link

        # No profile-shaped link found — fall back to the first repo link
        if github_links:
            return github_links[0]

    return None


def extract_name(text: str) -> str | None:
    """
    Uses spaCy NER to find PERSON entities.
    Heuristic: the candidate's name is almost always the first
    PERSON entity found near the top of the resume.
    """
    # Only run NER on the first 300 characters — name appears at the top,
    # running spaCy on the entire document wastes compute
    doc = nlp(text[:300])

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    return None


def extract_dates(text: str) -> list[str]:
    """
    Returns all date ranges and standalone dates found in the document.
    Range matches are extracted first; their text spans are excluded
    from standalone date matching so we don't double-count dates that
    are already part of a range (e.g. "03/2026" inside "03/2026-04/2026").
    """
    range_matches = list(DATE_RANGE_PATTERN.finditer(text))

    # Track character positions already covered by a range match
    claimed_spans = [match.span() for match in range_matches]

    def is_claimed(pos: int) -> bool:
        return any(start <= pos < end for start, end in claimed_spans)

    range_results = [match.group(0) for match in range_matches]

    # Only keep single-date matches that fall OUTSIDE any range span
    single_results = [
        match.group(0)
        for match in SINGLE_DATE_PATTERN.finditer(text)
        if not is_claimed(match.start())
    ]

    doc = nlp(text)
    spacy_dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]

    all_dates = range_results + single_results + spacy_dates
    seen = set()
    unique_dates = []
    for d in all_dates:
        if d not in seen:
            seen.add(d)
            unique_dates.append(d)

    return unique_dates

def extract_sections(text: str, doc_type: str) -> dict:
    headers = RESUME_HEADERS if doc_type == "resume" else JD_HEADERS

    lines = text.split("\n")
    sections = {}
    current_header = "header"
    current_content = []

    for line in lines:
        stripped = line.strip().lower()

        is_header = (
            len(stripped) > 0
            and len(stripped.split()) <= 4
            and any(stripped == h or stripped.startswith(h) for h in headers)
        )

        if is_header:
            sections[current_header] = "\n".join(current_content).strip()
            current_header = stripped
            current_content = []
        else:
            current_content.append(line)

    sections[current_header] = "\n".join(current_content).strip()

    if doc_type == "resume" and not sections.get("summary"):
        header_lines = sections.get("header", "").split("\n")
        if len(header_lines) > 1:
            # First line is almost always the name — keep it separate,
            # merge the rest into summary
            sections["header"] = header_lines[0]
            sections["summary"] = "\n".join(header_lines[1:]).strip()

    return sections


def extract_deterministic_fields(text: str, doc_type: str, hyperlinks: list[str] = None) -> dict:
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text, hyperlinks),
        "github": extract_github(text, hyperlinks),
        "dates": extract_dates(text),
        "sections": extract_sections(text, doc_type)
    }