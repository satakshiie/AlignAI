import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()
MODEL = "llama-3.3-70b-versatile"


def build_roadmap_prompt(
    true_gaps: list[dict],
    resume_skills: list[str],
    candidate_domain_hint: str
) -> str:
    """
    Builds the prompt for generating a learning roadmap for confirmed
    skill gaps. This is explicitly advice for the FUTURE, not a resume
    edit — the model must never suggest claiming these skills now.
    """

    gap_skill_names = [item["skill"] for item in true_gaps]

    prompt = f"""You are a career development assistant. The candidate has confirmed gaps between
their current skills and a target job's requirements. Generate a practical, prioritized
learning roadmap to help them close these gaps over time.

CRITICAL RULES:
- This roadmap is advice for what to LEARN — it is NOT resume content. Never phrase suggestions
  as something the candidate should claim on their resume now.
- Prioritize gaps that are foundational or commonly required across similar roles first.
- Be realistic about time investment — don't suggest "become an expert in X" with no timeframe context.
- Suggest concrete next steps (a type of resource, a project idea, a certification path) rather
  than vague advice like "learn more about X".
- Take into account the candidate's EXISTING skills — suggest learning paths that build on what
  they already know, not from zero, where reasonable.

CANDIDATE'S EXISTING SKILLS:
{json.dumps(resume_skills)}

CANDIDATE'S APPARENT DOMAIN:
{candidate_domain_hint}

CONFIRMED SKILL GAPS TO ADDRESS:
{json.dumps(gap_skill_names)}

Return ONLY valid JSON, no preamble, no markdown formatting:

{{
  "roadmap": [
    {{
      "skill": "string — the skill being addressed",
      "priority": "high, medium, or low",
      "reasoning": "string — why this priority, and how it connects to candidate's existing skills",
      "suggested_approach": "string — a concrete next step: project idea, resource type, or practice approach",
      "estimated_timeframe": "string — realistic rough estimate, e.g. '2-4 weeks of focused practice'"
    }}
  ]
}}

Rules:
- Include every skill from the confirmed gaps list above.
- "priority" should reflect how foundational/commonly-required the skill is, not just how hard it is.
"""
    return prompt


def infer_domain_hint(resume_skills: list[str], experience: list[dict]) -> str:
    """
    Builds a short domain description from the resume's own data —
    used to give the roadmap generator context without a separate
    LLM call. Simple heuristic based on what's already extracted,
    not a new inference step that needs its own grounding rules.
    """
    roles = [e.get("role", "") for e in experience]
    return f"Skills include: {', '.join(resume_skills[:10])}. Roles held: {', '.join(roles)}."


def roadmap_generator_node(state: dict) -> dict:
    """
    LangGraph node — Call 3 of the Tailoring agent.
    Only processes confirmed true_gap items from the Skill Gap Resolver —
    implied skills are handled by the Bullet Rewriter instead, since
    those don't need a learning roadmap, just clearer resume phrasing.
    """

    gap_items = state.get("gap_items", [])
    resume_data = state["resume_parsed_data"]

    true_gaps = [item for item in gap_items if item["status"] == "true_gap"]

    # No genuine gaps means no roadmap needed — skip the LLM call
    if not true_gaps:
        return {"learning_roadmap": []}

    domain_hint = infer_domain_hint(
        resume_data.get("skills", []),
        resume_data.get("experience", [])
    )

    prompt = build_roadmap_prompt(
        true_gaps=true_gaps,
        resume_skills=resume_data.get("skills", []),
        candidate_domain_hint=domain_hint
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # slightly higher than extraction calls —
                               # roadmap suggestions benefit from a little
                               # more natural variation than strict extraction
            response_format={"type": "json_object"}
        )

        raw_output = response.choices[0].message.content
        parsed = json.loads(raw_output)

        return {"learning_roadmap": parsed.get("roadmap", [])}

    except json.JSONDecodeError:
        # Fail safe — return a minimal roadmap rather than nothing,
        # so the user still sees their gaps even if generation failed
        return {
            "learning_roadmap": [
                {
                    "skill": item["skill"],
                    "priority": "medium",
                    "reasoning": "Roadmap generation failed — listing as a known gap.",
                    "suggested_approach": "Research standard learning resources for this skill.",
                    "estimated_timeframe": "Unknown"
                }
                for item in true_gaps
            ]
        }