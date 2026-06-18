import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq()  # assumes GROQ_API_KEY is already set in your environment, same as Kamalam

MODEL = "llama-3.3-70b-versatile"


def build_extraction_prompt(sections: dict, raw_text: str, extraction_method: str) -> str:
    """
    Builds the prompt for resume parsing. Sections from Phase 1 are passed
    as the primary structured input. Raw text is included as fallback
    context — useful when a section came back empty (e.g. "education")
    due to PDF reading-order quirks, since the LLM can still find that
    content in the raw text even if Phase 1's splitter missed it.
    """

    # Only mention OCR caveats if this document actually went through OCR —
    # no need to prime the model to expect noise in a clean text extraction
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
    Returns a dict with success status and either the parsed data or an error.
    """

    prompt = build_extraction_prompt(sections, raw_text, extraction_method)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # low temperature — we want consistent, literal extraction, not creativity
            response_format={"type": "json_object"}  # forces valid JSON output from Groq
        )

        raw_output = response.choices[0].message.content
        parsed = json.loads(raw_output)

        return {
            "success": True,
            "data": parsed
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"LLM returned invalid JSON: {str(e)}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"LLM extraction failed: {str(e)}"
        }