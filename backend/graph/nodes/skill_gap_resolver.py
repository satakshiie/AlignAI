import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq()
MODEL = "llama-3.3-70b-versatile"


def build_skill_gap_prompt(
    missing_required: list[str],
    missing_preferred: list[str],
    resume_skills: list[str],
    resume_experience: list[dict],
    resume_projects: list[dict]
) -> str:
    """
    Builds the prompt for re-examining Layer 1's flagged skill gaps.
    The model's job is NOT to invent new claims — it's to check whether
    each 'missing' skill is actually implied by content the candidate
    already provided (e.g. 'iOS' implied by Swift + SwiftUI + Xcode +
    iOS job titles), or whether it's a genuine gap with no grounding.
    """

    # Flatten experience/project bullets into plain text the model can scan
    experience_text = "\n".join(
        f"{role.get('role', '')} at {role.get('company', '')}: " +
        " ".join(role.get("bullets", []))
        for role in resume_experience
    )

    projects_text = "\n".join(
        f"{proj.get('title', '')}: " +
        " ".join(proj.get("tech_stack", [])) + " — " +
        " ".join(proj.get("bullets", []))
        for proj in resume_projects
    )

    prompt = f"""You are reviewing a list of "missing skills" flagged by an exact-match comparison
between a resume and a job description. Your job is to determine, for EACH missing skill,
whether it is:

1. "implied" — the candidate's existing skills, job titles, or project descriptions strongly
   suggest they actually have this skill, even though it wasn't listed as its own explicit skill.
2. "true_gap" — there is no reasonable evidence anywhere in the resume that the candidate has
   this skill or experience.

CRITICAL RULES:
- You must NEVER invent or assume information that isn't grounded in the resume content below.
- For every skill you classify as "implied", you MUST cite the SPECIFIC resume content
  (exact skill names, job titles, or project details) that supports this conclusion.
- If you cannot point to specific grounding, classify it as "true_gap" — do not guess.
- A skill being "related" to other skills is not enough — there must be a clear, specific,
  defensible connection (e.g. "iOS" is implied by "Swift" + "SwiftUI" + "Xcode" + an "iOS Developer"
  job title — that's a strong, specific connection, not a vague one).

CANDIDATE'S LISTED SKILLS:
{json.dumps(resume_skills)}

CANDIDATE'S EXPERIENCE:
{experience_text}

CANDIDATE'S PROJECTS:
{projects_text}

MISSING REQUIRED SKILLS TO EVALUATE:
{json.dumps(missing_required)}

MISSING PREFERRED SKILLS TO EVALUATE:
{json.dumps(missing_preferred)}

Return ONLY valid JSON, no preamble, no markdown formatting:

{{
  "gap_items": [
    {{
      "skill": "string — the exact skill name being evaluated",
      "skill_type": "required or preferred",
      "status": "implied or true_gap",
      "confidence": "float between 0 and 1 — how confident you are in this classification",
      "grounding": ["list of specific resume content that supports this classification — empty list if true_gap"],
      "suggested_action": "string — for 'implied': what to add/change; for 'true_gap': null"
    }}
  ]
}}

Rules:
- Include EVERY skill from both missing lists above — do not skip any.
- "confidence" should be lower (0.5-0.7) for plausible-but-uncertain connections, higher (0.8-0.95) for strong, specific connections like the iOS example. Never use exactly 1.0 — there's always some uncertainty in inference.
- "grounding" must quote or closely paraphrase actual resume content, not generic statements like "candidate has technical skills".
"""
    return prompt


def skill_gap_resolver_node(state: dict) -> dict:
    """
    LangGraph node — Call 2 of the Tailoring agent.
    Reads ats_gaps and resume_parsed_data from state, returns gap_items
    with grounded classifications for the rest of the graph to use.
    """

    ats_gaps = state["ats_gaps"]
    resume_data = state["resume_parsed_data"]

    # Extract missing skills from the ATS gap report structure
    missing_required = []
    missing_preferred = []
    for gap in ats_gaps:
        if gap["type"] == "missing_required_skill":
            missing_required.extend(gap["items"])
        elif gap["type"] == "missing_preferred_skill":
            missing_preferred.extend(gap["items"])

    # If there are no skill gaps at all, skip the LLM call entirely —
    # no point spending a Groq request to confirm an empty list
    if not missing_required and not missing_preferred:
        return {"gap_items": []}

    prompt = build_skill_gap_prompt(
        missing_required=missing_required,
        missing_preferred=missing_preferred,
        resume_skills=resume_data.get("skills", []),
        resume_experience=resume_data.get("experience", []),
        resume_projects=resume_data.get("projects", [])
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        raw_output = response.choices[0].message.content
        parsed = json.loads(raw_output)

        # Add the fields the Critic and human-review steps will need later —
        # not filled in by this node, but must exist in the shape so
        # downstream nodes don't break on a missing key
        gap_items = []
        for item in parsed.get("gap_items", []):
            gap_items.append({
                **item,
                "critic_confidence": None,
                "critic_notes": None,
                "needs_human_review": False,
                "human_decision": None
            })

        return {"gap_items": gap_items}

    except json.JSONDecodeError as e:
        # If this node fails, we don't want to silently lose the gap
        # report — fall back to treating everything as a true_gap with
        # zero grounding, rather than crashing the whole graph
        return {
            "gap_items": [
                {
                    "skill": skill,
                    "skill_type": "required",
                    "status": "true_gap",
                    "confidence": 0.5,
                    "grounding": [],
                    "suggested_action": None,
                    "critic_confidence": None,
                    "critic_notes": None,
                    "needs_human_review": True,  # flag for review since this is a fallback, not a real classification
                    "human_decision": None
                }
                for skill in missing_required + missing_preferred
            ]
        }