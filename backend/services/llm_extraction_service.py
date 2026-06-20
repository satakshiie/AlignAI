import json
import os
from dotenv import load_dotenv

load_dotenv()
from groq import Groq

client = Groq()  # assumes GROQ_API_KEY is already set in your environment

MODEL = "llama-3.3-70b-versatile"


# ============================================================
# RESUME EXTRACTION
# ============================================================

def build_extraction_prompt(sections: dict, raw_text: str, extraction_method: str) -> str:
    """
    Builds the prompt for resume parsing. Sections from Phase 1 are passed
    as primary structured input. Raw text is fallback context for cases
    where a section came back empty due to PDF reading-order quirks.
    """

    ocr_note = ""
    if extraction_method == "tesseract_ocr":
        ocr_note = (
            "\nNote: this text was extracted via OCR and may contain minor "
            "character recognition errors (e.g. 'l' vs 'I', missing punctuation, "
            "bullet symbols misread as 'e' or '•'). Use context to infer the "
            "correct intended word or value when extracting fields.\n"
        )

    prompt = f"""You are a resume parsing assistant. Extract structured information from the resume below.

The resume has been pre-segmented into sections, but section boundaries may be imperfect —
some content (e.g. a project's sub-title, or content that appears before its own header due to
PDF layout) may be misplaced. Use the raw text as a fallback reference if a section seems
incomplete or empty.
{ocr_note}
PRE-SEGMENTED SECTIONS:
{json.dumps(sections, indent=2)}

RAW TEXT (fallback reference):
{raw_text}

Extract the following and return ONLY valid JSON, no preamble, no markdown formatting, no explanation:

{{
  "summary": "string or null",
  "skills": ["list of individual skill strings, deduplicated"],
  "experience": [
    {{
      "role": "string",
      "company": "string",
      "duration": "string, e.g. '03/2026 - 04/2026'",
      "bullets": ["list of responsibility/achievement strings"]
    }}
  ],
  "projects": [
    {{
      "title": "string",
      "role": "string or null",
      "tech_stack": ["list of technologies used"],
      "bullets": ["list of description strings"]
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "duration": "string or null",
      "gpa_or_grade": "string or null"
    }}
  ],
  "certifications": ["list of certification name strings"]
}}

Rules:
- If a field has no information available, use null (for strings) or an empty list (for arrays) — never omit the key.
- The "summary" field must be the candidate's own written summary/objective statement, copied or lightly cleaned from the resume text — never write one yourself. If no summary, objective, or "about me" section exists anywhere in the resume, set "summary" to null. Do not synthesize a summary by combining details from skills, experience, or projects — that counts as fabrication and is strictly forbidden.
- The "skills" list should include every technology, language, framework, or tool explicitly named anywhere in the resume — including inside experience bullets and project descriptions, not only the dedicated Skills section. Do not infer or add skills that are not directly named as text anywhere in the resume.
- Each distinct project under a "Projects" heading should be its own object in the projects array, even if they were grouped under one section in the pre-segmented input.
- A short proper-noun-like word or phrase immediately followed by "Role:" and a tech stack description is a PROJECT TITLE, not a certification. Certifications are formal credential names (e.g. "AWS Certified Developer", "Azure AI Fundamentals") — never a single standalone word followed by "Role: [job title] | Tech: [technologies]". If you see that pattern, the preceding word or phrase belongs in the project's "title" field, not in certifications.
- Do not fabricate company names, dates, or institutions that are not present in the text.
"""
    return prompt


def extract_resume_data(sections: dict, raw_text: str, extraction_method: str) -> dict:
    """
    Calls the LLM to extract structured resume data.
    """
    prompt = build_extraction_prompt(sections, raw_text, extraction_method)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        raw_output = response.choices[0].message.content
        parsed = json.loads(raw_output)

        return {"success": True, "data": parsed}

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"LLM returned invalid JSON: {str(e)}"}

    except Exception as e:
        return {"success": False, "error": f"LLM extraction failed: {str(e)}"}


# ============================================================
# JOB DESCRIPTION EXTRACTION
# ============================================================

def build_jd_extraction_prompt(sections: dict, raw_text: str, extraction_method: str) -> str:
    """
    Builds the prompt for job description parsing. Structurally different
    from resume extraction — a JD describes role requirements, not a
    person's history, so the schema separates required vs preferred
    skills rather than using one flat skills list.
    """

    ocr_note = ""
    if extraction_method == "tesseract_ocr":
        ocr_note = (
            "\nNote: this text was extracted via OCR and may contain minor "
            "character recognition errors. Use context to infer the correct "
            "intended word or value when extracting fields.\n"
        )

    prompt = f"""You are a job description parsing assistant. Extract structured information from the job description below.

The JD has been pre-segmented into sections, but section boundaries may be imperfect.
Use the raw text as a fallback reference if a section seems incomplete or empty.
{ocr_note}
PRE-SEGMENTED SECTIONS:
{json.dumps(sections, indent=2)}

RAW TEXT (fallback reference):
{raw_text}

Extract the following and return ONLY valid JSON, no preamble, no markdown formatting, no explanation:

{{
  "job_title": "string or null",
  "company": "string or null",
  "seniority_level": "one of: entry, mid, senior, lead, not specified",
  "employment_type": "one of: full-time, part-time, internship, contract, not specified",
  "required_skills": ["list of skills explicitly marked as required/must-have"],
  "preferred_skills": ["list of skills explicitly marked as preferred/nice-to-have/bonus"],
  "responsibilities": ["list of distinct responsibility/duty strings"],
  "qualifications": ["list of distinct qualification requirements, e.g. degree, years of experience"],
  "ats_keywords": ["list of important domain-specific terms and tools mentioned, useful for ATS keyword matching"]
}}

Rules:
- If a field has no information available, use null (for strings) or an empty list (for arrays) — never omit the key.
- Only include a skill in "required_skills" if the text explicitly signals it as mandatory (e.g. listed under "Requirements", "Must have", or stated directly as required). Do not guess.
- Only include a skill in "preferred_skills" if the text explicitly signals it as optional/bonus (e.g. listed under "Nice to have", "Preferred", "Bonus points").
- If a skill's required/preferred status is genuinely ambiguous from context, default to "required_skills" rather than omitting it, but never duplicate the same skill in both lists.
- "ats_keywords" should include skills, tools, certifications, and domain terms mentioned anywhere in the JD — this list may overlap with required/preferred skills, that's expected.
- Do not fabricate a company name, job title, or seniority level that isn't stated or strongly implied by the text. If seniority isn't mentioned or implied by job title (e.g. "Senior Engineer"), use "not specified".
- "required_skills" and "preferred_skills" must each be SHORT, ATOMIC skill or competency names (1-4 words each, e.g. "communication skills", "Python", "team management") — never full sentences or requirement descriptions. If a requirement is phrased as a full sentence in the JD (e.g. "must have at least 2 years of experience managing a team"), extract just the core skill/competency from it (e.g. "team management experience") rather than copying the full sentence.
- Do not invent responsibilities or qualifications not present in the text.
"""
    return prompt


def extract_jd_data(sections: dict, raw_text: str, extraction_method: str) -> dict:
    """
    Calls the LLM to extract structured JD data. Mirrors extract_resume_data()
    but uses the JD-specific prompt and schema.
    """
    prompt = build_jd_extraction_prompt(sections, raw_text, extraction_method)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        raw_output = response.choices[0].message.content
        parsed = json.loads(raw_output)

        return {"success": True, "data": parsed}

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"LLM returned invalid JSON: {str(e)}"}

    except Exception as e:
        return {"success": False, "error": f"LLM extraction failed: {str(e)}"}