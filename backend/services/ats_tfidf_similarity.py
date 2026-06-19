from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def clean_text_for_tfidf(text: str) -> str:

    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)   # strip punctuation/symbols
    text = re.sub(r"\s+", " ", text)        # collapse multiple spaces
    return text.strip()

def get_section_text(sections: dict, possible_keys: list[str]) -> str:
    """
    Looks up section content by trying multiple possible header names,
    since Phase 1's section splitting isn't always perfectly consistent
    (e.g. a JD's responsibilities content might land under a slightly
    different or fragmented key). Returns the longest matching section
    found, since longer content is more likely to be the real section
    rather than a stray fragment.
    """
    best_match = ""
    for key, content in sections.items():
        # Check if any possible key is a substring of this section's key name
        if any(possible_key in key for possible_key in possible_keys):
            if len(content) > len(best_match):
                best_match = content
    return best_match

def compute_similarity(text_a: str, text_b: str) -> float:
   
    text_a_clean = clean_text_for_tfidf(text_a)
    text_b_clean = clean_text_for_tfidf(text_b)

    if not text_a_clean or not text_b_clean:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")

    try:
        tfidf_matrix = vectorizer.fit_transform([text_a_clean, text_b_clean])
    except ValueError:
        # Happens if both texts are empty after cleaning, or contain
        # only stopwords — nothing meaningful to vectorize
        return 0.0

    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(float(similarity_matrix[0][0]), 3)


def analyze_content_similarity(
    resume_sections: dict,
    jd_sections: dict,
    resume_raw_text: str,
    jd_raw_text: str
) -> dict:

    resume_experience = get_section_text(resume_sections, ["experience"])
    jd_responsibilities = get_section_text(jd_sections, ["responsibilities", "duties", "role purpose"])

    experience_similarity = compute_similarity(resume_experience, jd_responsibilities)

    resume_projects = get_section_text(resume_sections, ["projects"])
    projects_similarity = compute_similarity(resume_projects, jd_responsibilities)

    overall_similarity = compute_similarity(resume_raw_text, jd_raw_text)

    best_section_similarity = max(experience_similarity, projects_similarity)

    layer3_score = round(
        (best_section_similarity * 0.75) + (overall_similarity * 0.25),
        3
    )

    return {
        "layer3_score": layer3_score,
        "breakdown": {
            "experience_vs_responsibilities": experience_similarity,
            "projects_vs_responsibilities": projects_similarity,
            "overall_document_similarity": overall_similarity
        }
    }