"""
doc_type_heuristic.py

Quick, free content-based heuristic to catch the most common mismatch:
a resume uploaded into the JD slot (or vice-versa).

This runs immediately after text extraction, before any LLM/deterministic
extraction, so it adds virtually zero cost. It is intentionally simple —
it scores keyword signals rather than doing NLP — and is designed to
fail in the right direction:

  SIGNAL DESIGN RULE: every term in RESUME_SIGNALS must be rare/absent in
  real JDs, and every term in JD_SIGNALS must be rare/absent in real resumes.
  Terms like "experience", "education", "skills", "summary" appear in BOTH
  document types and must NOT be in either list — they wash out the score
  and cause JDs uploaded as resumes to go UNDETECTED.

  - A resume with "gpa", "references", "internship", "publications" will score
    high on resume signals and near-zero on JD signals → caught correctly.
  - A JD with "responsibilities", "we are hiring", "you will", "apply now"
    will score high on JD signals and near-zero on resume signals → caught correctly.
  - A very sparse or unusual document might score 0/0 and be treated as
    UNDETECTED — we let those through rather than false-block valid uploads.
"""

from enum import Enum


class DocTypeGuess(str, Enum):
    RESUME = "resume"
    JD = "jd"
    UNDETECTED = "undetected"   # too few signals either way — don't block


# ── RESUME signals ────────────────────────────────────────────────────────────
# Only include terms that genuinely do NOT appear in job descriptions.
# Removed: "education", "experience", "skills", "summary", "employment",
#          "certifications", "achievements" — all appear in JDs too.
RESUME_SIGNALS = [
    "gpa",
    "references",
    "internship",
    "volunteer",
    "publications",
    "awards",
    "work history",
    "objective",
    "coursework",
    "extracurricular",
    "dean's list",
    "honor roll",
    "thesis",
    "dissertation",
    "cumulative gpa",
    "relevant coursework",
]

# ── JD signals ────────────────────────────────────────────────────────────────
# Only include terms that genuinely do NOT appear in resumes.
JD_SIGNALS = [
    "responsibilities",
    "qualifications",
    "we are looking for",
    "we are hiring",
    "requirements",
    "about the role",
    "about the company",
    "about us",
    "what you will do",
    "what you'll do",
    "you will",
    "who you are",
    "minimum qualifications",
    "preferred qualifications",
    "nice to have",
    "benefits",
    "compensation",
    "salary",
    "equal opportunity",
    "apply now",
    "how to apply",
    "job description",
    "job summary",
    "we offer",
    "the ideal candidate",
    "job type",
    "full-time",
    "part-time",
    "hybrid",
    "on-site",
    "remote",
]

# Minimum gap between winner and loser scores before we're confident enough
# to block. If scores are this close, we return UNDETECTED (safe fallback).
CONFIDENCE_THRESHOLD = 2


"""
doc_type_heuristic.py

Quick, free content-based heuristic to catch the most common mismatch:
a resume uploaded into the JD slot (or vice-versa).

This runs immediately after text extraction, before any LLM/deterministic
extraction, so it adds virtually zero cost. It is intentionally simple —
it scores keyword signals rather than doing NLP — and is designed to
fail in the right direction:

  SIGNAL DESIGN RULE: every term in RESUME_SIGNALS must be rare/absent in
  real JDs, and every term in JD_SIGNALS must be rare/absent in real resumes.
  Terms like "experience", "education", "skills", "summary" appear in BOTH
  document types and must NOT be in either list — they wash out the score
  and cause JDs uploaded as resumes to go UNDETECTED.

  - A resume with "gpa", "references", "internship", "publications" will score
    high on resume signals and near-zero on JD signals → caught correctly.
  - A JD with "responsibilities", "we are hiring", "you will", "apply now"
    will score high on JD signals and near-zero on resume signals → caught correctly.
  - A very sparse or unusual document might score 0/0 and be treated as
    UNDETECTED — we let those through rather than false-block valid uploads.
"""

from enum import Enum


class DocTypeGuess(str, Enum):
    RESUME = "resume"
    JD = "jd"
    UNDETECTED = "undetected"   # too few signals either way — don't block


# ── RESUME signals ────────────────────────────────────────────────────────────
# Only include terms that genuinely do NOT appear in job descriptions.
# Removed: "education", "experience", "skills", "summary", "employment",
#          "certifications", "achievements" — all appear in JDs too.
RESUME_SIGNALS = [
    "gpa",
    "references",
    "internship",
    "volunteer",
    "publications",
    "awards",
    "work history",
    "objective",
    "coursework",
    "extracurricular",
    "dean's list",
    "honor roll",
    "thesis",
    "dissertation",
    "cumulative gpa",
    "relevant coursework",
]

# ── JD signals ────────────────────────────────────────────────────────────────
# Only include terms that genuinely do NOT appear in resumes.
JD_SIGNALS = [
    "responsibilities",
    "qualifications",
    "we are looking for",
    "we are hiring",
    "requirements",
    "about the role",
    "about the company",
    "about us",
    "what you will do",
    "what you'll do",
    "you will",
    "who you are",
    "minimum qualifications",
    "preferred qualifications",
    "nice to have",
    "benefits",
    "compensation",
    "salary",
    "equal opportunity",
    "apply now",
    "how to apply",
    "job description",
    "job summary",
    "we offer",
    "the ideal candidate",
    "job type",
    "full-time",
    "part-time",
    "hybrid",
    "on-site",
    "remote",
]

# Minimum gap between winner and loser scores before we're confident enough
# to block. If scores are this close, we return UNDETECTED (safe fallback).
CONFIDENCE_THRESHOLD = 2


def guess_doc_type(text: str) -> DocTypeGuess:
    """
    Score the extracted text against resume and JD keyword lists and return
    the most likely document type.

    Returns DocTypeGuess.UNDETECTED when the signal gap is below
    CONFIDENCE_THRESHOLD — callers should treat that as "don't block".
    """
    text_lower = text.lower()

    resume_score = sum(1 for signal in RESUME_SIGNALS if signal in text_lower)
    jd_score = sum(1 for signal in JD_SIGNALS if signal in text_lower)

    gap = abs(resume_score - jd_score)

    if gap < CONFIDENCE_THRESHOLD:
        return DocTypeGuess.UNDETECTED

    if resume_score > jd_score:
        return DocTypeGuess.RESUME
    return DocTypeGuess.JD


def has_minimal_document_signal(text: str) -> bool:
    """
    Separate, lower-bar check: does this text contain ANY resume-like
    or JD-like signal at all, regardless of which type wins? This catches
    documents that are neither (receipts, invoices, random PDFs) — which
    guess_doc_type() alone can't distinguish from genuinely ambiguous
    resume/JD content, since both score 0/0 the same way.
    """
    text_lower = text.lower()
    resume_score = sum(1 for signal in RESUME_SIGNALS if signal in text_lower)
    jd_score = sum(1 for signal in JD_SIGNALS if signal in text_lower)
    return (resume_score + jd_score) > 0

def is_substantial_document(text: str, min_word_count: int = 100) -> bool:
    """
    A genuine resume or JD has substantial descriptive content — typically
    several hundred words at minimum. Certificates, receipts, and similar
    short formal documents rarely exceed a few dozen words of actual prose,
    even though they might coincidentally contain a stray keyword match.
    This catches what keyword scoring alone cannot.
    """
    word_count = len(text.split())
    return word_count >= min_word_count
