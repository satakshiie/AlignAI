import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()
MODEL = "llama-3.3-70b-versatile"


def build_bullet_rewrite_prompt(
    experience: list[dict],
    projects: list[dict],
    implied_skills: list[dict],
    jd_responsibilities: list[str]
) -> str:
    """
    Builds the prompt for rewriting resume bullets. The model's job is
    to REPHRASE existing content to surface skills more explicitly and
    align vocabulary with the JD where genuinely applicable — never to
    invent new accomplishments, metrics, or responsibilities that aren't
    already present in the original bullet.
    """

    implied_summary = "\n".join(
        f"- '{item['skill']}' is implied by: {', '.join(item['grounding'])}"
        for item in implied_skills
        if item["status"] == "implied"
    )

    prompt = f"""You are a resume editing assistant. Your job is to rewrite resume bullets to be
clearer and more aligned with a target job description — WITHOUT changing what actually happened
or inventing any new claims.

CRITICAL RULES:
- You may rephrase, reorganize, and clarify existing bullets.
- You may make an implied skill more explicit if it's already supported by the bullet's own content
  (see "skills to surface" below) — e.g. if a bullet describes iOS work but never says the word "iOS",
  you may add the word "iOS" since it's already true of what's described.
- You must NEVER add new metrics, outcomes, technologies, or responsibilities that are not present
  in the original bullet. If the original bullet doesn't mention a number, don't invent one.
- You must NEVER change the fundamental claim of what the candidate did.
- Every rewrite must come with a "grounding" explanation — what in the ORIGINAL bullet justifies
  the change you made.
- If a bullet is already clear and well-aligned, you may leave it unchanged — don't force changes
  for the sake of it.
  - Be especially careful with words like "collaboration," "team," "cross-functional" —
  these describe HUMAN INTERACTION claims, which are a different and stronger claim than
  a technical/architectural detail. A bullet mentioning "cross-module workflows" (a software
  architecture detail) does NOT automatically justify adding language about "collaborating
  with cross-functional teams" (a claim about working with other people) unless the original
  bullet explicitly describes working with other people, not just other systems or modules.
- Do not pull specific phrases or near-exact wording from the JD responsibilities into the
  rewritten bullet. Vocabulary alignment means using similar terminology where genuinely
  accurate, not inserting JD phrasing wholesale.

SKILLS TO SURFACE (already implied by existing content, safe to make explicit):
{implied_summary if implied_summary else "None"}

TARGET JD RESPONSIBILITIES (for vocabulary alignment only — do not copy claims from here):
{json.dumps(jd_responsibilities)}

EXPERIENCE BULLETS TO REVIEW:
{json.dumps([{"role": e.get("role"), "company": e.get("company"), "bullets": e.get("bullets", [])} for e in experience], indent=2)}

PROJECT BULLETS TO REVIEW:
{json.dumps([{"title": p.get("title"), "bullets": p.get("bullets", [])} for p in projects], indent=2)}

Return ONLY valid JSON, no preamble, no markdown formatting:

{{
  "bullet_rewrites": [
    {{
      "source": "string — which role or project this bullet belongs to",
      "original": "the exact original bullet text",
      "rewritten": "the rewritten version, or identical to original if no change needed",
      "changed": true or false,
      "grounding": "string — what in the original bullet justifies this specific change, or 'no change needed' if unchanged",
      "confidence": "float 0-1 — how confident you are this rewrite is fully grounded in the original"
    }}
  ]
}}

Rules:
- Include EVERY bullet from both experience and projects above, even ones you didn't change.
- "changed" must be false if rewritten is identical to original.
- Never set confidence to exactly 1.0.
"""
    return prompt


def bullet_rewriter_node(state: dict) -> dict:
    """
    LangGraph node — Call 1 of the Tailoring agent.
    Reads resume experience/projects and the Skill Gap Resolver's
    gap_items from state, returns rewritten bullets with grounding.
    """

    resume_data = state["resume_parsed_data"]
    jd_data = state["jd_parsed_data"]
    gap_items = state.get("gap_items", [])

    experience = resume_data.get("experience", [])
    projects = resume_data.get("projects", [])

    # If there's no experience or project content at all, nothing to rewrite
    if not experience and not projects:
        return {"bullet_rewrites": []}

    prompt = build_bullet_rewrite_prompt(
        experience=experience,
        projects=projects,
        implied_skills=gap_items,
        jd_responsibilities=jd_data.get("responsibilities", [])
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

        bullet_rewrites = []
        for item in parsed.get("bullet_rewrites", []):
            bullet_rewrites.append({
                **item,
                "critic_confidence": None,
                "needs_human_review": False,
                "human_decision": None
            })

        return {"bullet_rewrites": bullet_rewrites}

    except json.JSONDecodeError as e:
        # Fail safe — if rewriting fails, return the original bullets
        # unchanged rather than losing them or crashing the graph
        fallback = []
        for role in experience:
            for bullet in role.get("bullets", []):
                fallback.append({
                    "source": role.get("role", "experience"),
                    "original": bullet,
                    "rewritten": bullet,
                    "changed": False,
                    "grounding": "Rewrite failed — original preserved unchanged",
                    "confidence": None,
                    "critic_confidence": None,
                    "needs_human_review": True,
                    "human_decision": None
                })
        return {"bullet_rewrites": fallback}