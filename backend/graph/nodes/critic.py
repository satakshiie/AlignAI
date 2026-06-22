import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()
MODEL = "llama-3.3-70b-versatile"

# Below this confidence, an item gets routed to human review rather
# than auto-approved. Tunable — start conservative, loosen later once
# you have real data on how often the Critic's skepticism is warranted.
CRITIC_CONFIDENCE_THRESHOLD = 0.7


def build_critic_prompt(gap_items: list[dict], bullet_rewrites: list[dict]) -> str:
    """
    Builds the prompt for the Critic's independent review. Deliberately
    framed as a skeptical audit, not a confirmation pass — the model is
    explicitly asked to find reasons a claim might be wrong, not to agree
    with the prior reasoning.
    """

    implied_skills = [item for item in gap_items if item["status"] == "implied"]
    changed_bullets = [b for b in bullet_rewrites if b["changed"]]

    prompt = f"""You are a skeptical auditor reviewing claims made by another AI system about a
candidate's resume. Your job is NOT to confirm these claims are reasonable — your job is to
actively look for weaknesses, overreach, or insufficient evidence in each claim, and assign
a genuinely independent confidence score.

For each "implied skill" claim below, ask yourself:
- Is the grounding cited actually specific and direct, or is it vague/circumstantial?
- Could this grounding just as easily NOT imply the skill in question?
- Is the connection a single weak inference, or multiple independent pieces of evidence?

For each "bullet rewrite" claim below, ask yourself:
- Does the rewritten version state anything beyond what the original bullet actually said?
- Could the added language be interpreted as a stronger claim than the original (e.g. turning
  a technical detail into a claim about people/collaboration, or adding implied scale/impact)?
- Is the grounding given for the change specific, or generic-sounding?

IMPLIED SKILL CLAIMS TO AUDIT:
{json.dumps(implied_skills, indent=2)}

BULLET REWRITE CLAIMS TO AUDIT:
{json.dumps(changed_bullets, indent=2)}

Return ONLY valid JSON, no preamble, no markdown formatting:

{{
  "skill_reviews": [
    {{
      "skill": "string — matching the skill name above",
      "critic_confidence": "float 0-1 — your INDEPENDENT confidence this claim is well-grounded",
      "critic_notes": "string — specific concern if confidence is lowered, or brief confirmation if high"
    }}
  ],
  "bullet_reviews": [
    {{
      "source": "string — matching the source above",
      "original": "string — matching the original bullet above, used to identify which review applies",
      "critic_confidence": "float 0-1 — your INDEPENDENT confidence this rewrite is fully grounded",
      "critic_notes": "string — specific concern if confidence is lowered, or brief confirmation if high"
    }}
  ]
}}

Rules:
- Be genuinely critical. If you would have made the same claim with the same confidence, say so —
  but don't default to high confidence just because the original reasoning sounds plausible.
- A confidence score above 0.85 should be reserved for claims with multiple independent, specific
  pieces of grounding — not single, generic-sounding justifications.
- Never use exactly 1.0.
"""
    return prompt


def critic_node(state: dict) -> dict:
    """
    LangGraph node — independently audits the Tailoring agent's output.
    Sets critic_confidence and needs_human_review on each gap_item and
    bullet_rewrite, and sets the graph-level needs_human_review flag
    that the conditional edge will route on.
    """

    gap_items = state.get("gap_items", [])
    bullet_rewrites = state.get("bullet_rewrites", [])

    implied_skills = [item for item in gap_items if item["status"] == "implied"]
    changed_bullets = [b for b in bullet_rewrites if b["changed"]]

    # Nothing to audit — true gaps and unchanged bullets don't carry
    # claims that need critique, only "implied" classifications and
    # actual bullet changes do
    if not implied_skills and not changed_bullets:
        return {
            "gap_items": gap_items,
            "bullet_rewrites": bullet_rewrites,
            "needs_human_review": False
        }

    prompt = build_critic_prompt(gap_items, bullet_rewrites)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        raw_output = response.choices[0].message.content
        parsed = json.loads(raw_output)

        skill_reviews = {r["skill"]: r for r in parsed.get("skill_reviews", [])}
        bullet_reviews = {r["original"]: r for r in parsed.get("bullet_reviews", [])}

        any_needs_review = False

        # Apply critic review back onto gap_items
        updated_gap_items = []
        for item in gap_items:
            review = skill_reviews.get(item["skill"])
            if review:
                needs_review = review["critic_confidence"] < CRITIC_CONFIDENCE_THRESHOLD
                any_needs_review = any_needs_review or needs_review
                updated_gap_items.append({
                    **item,
                    "critic_confidence": review["critic_confidence"],
                    "critic_notes": review["critic_notes"],
                    "needs_human_review": needs_review
                })
            else:
                updated_gap_items.append(item)

        # Apply critic review back onto bullet_rewrites
        updated_bullets = []
        for bullet in bullet_rewrites:
            review = bullet_reviews.get(bullet["original"])
            if review:
                needs_review = review["critic_confidence"] < CRITIC_CONFIDENCE_THRESHOLD
                any_needs_review = any_needs_review or needs_review
                updated_bullets.append({
                    **bullet,
                    "critic_confidence": review["critic_confidence"],
                    "needs_human_review": needs_review
                })
            else:
                updated_bullets.append(bullet)

        return {
            "gap_items": updated_gap_items,
            "bullet_rewrites": updated_bullets,
            "needs_human_review": any_needs_review
        }

    except json.JSONDecodeError:
        # Fail safe — if the Critic itself fails, don't silently auto-approve
        # everything. Default to flagging implied skills and changed bullets
        # for human review, since we couldn't independently verify them.
        flagged_gaps = [
            {**item, "needs_human_review": True, "critic_notes": "Critic review failed — flagged by default"}
            if item["status"] == "implied" else item
            for item in gap_items
        ]
        flagged_bullets = [
            {**b, "needs_human_review": True}
            if b["changed"] else b
            for b in bullet_rewrites
        ]
        return {
            "gap_items": flagged_gaps,
            "bullet_rewrites": flagged_bullets,
            "needs_human_review": True
        }