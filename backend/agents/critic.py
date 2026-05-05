# agents/critic.py

import os
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
from schemas.contracts import ScraperOutput, TailoringDraft, CriticReport

load_dotenv()

# ── GROQ LLM SETUP ────────────────────────────────────────────────────────────

groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────

CRITIC_PROMPT = """
You are a brutal but fair ATS (Applicant Tracking System) expert and resume auditor.
Your job is to review a tailored resume draft against the original job description
and the candidate's original resume bullets.

You have TWO jobs:

JOB 1 — HALLUCINATION DETECTION:
Compare every rewritten bullet against its original bullet.
Flag any skill, tool, metric, title, or claim in the rewrite that does NOT exist
in the original bullet. These are hallucinations and must be rejected.

JOB 2 — KEYWORD COVERAGE:
Check that the required JD skills appear naturally in the draft.
Flag any required skill that is completely missing from the rewritten bullets
and the professional summary combined.

APPROVAL CRITERIA (ALL must be true to approve):
- Zero hallucinations detected
- At least 80% of required skills appear in the draft
- Every rewritten bullet starts with an action verb
- Professional summary mentions the job title or role

Return a JSON object matching this exact structure:
{
  "is_approved": true or false,
  "hallucinations_detected": ["list of invented claims, empty if none"],
  "missing_keywords": ["list of required JD skills not found in draft, empty if none"],
  "feedback": "Specific fix instructions for the writer. Empty string if approved.",
  "revision_count": 0
}

Return valid JSON only. No markdown fences. No preamble.
"""

# ── MOCK DATA ─────────────────────────────────────────────────────────────────

MOCK_APPROVED_DRAFT = TailoringDraft(
    professional_summary=(
        "Results-driven iOS Engineer with hands-on experience in Swift, UIKit, "
        "and on-device ML using the Vision framework. Proven ability to ship "
        "high-quality native apps and collaborate cross-functionally."
    ),
    tailored_experience=[
        __import__('schemas.contracts', fromlist=['TailoredExperience']).TailoredExperience(
            original_bullet="Built and shipped 3 iOS apps using Swift and UIKit with 50k+ downloads.",
            rewritten_bullet="Engineered and launched 3 production iOS applications using Swift and UIKit, achieving 50k+ downloads.",
            skills_highlighted=["Swift", "UIKit"],
            source_section="experience"
        ),
        __import__('schemas.contracts', fromlist=['TailoredExperience']).TailoredExperience(
            original_bullet="Integrated a real-time object detection feature using the Vision framework.",
            rewritten_bullet="Implemented real-time object detection leveraging Apple's Vision framework and CoreML.",
            skills_highlighted=["CoreML", "Vision framework"],
            source_section="experience"
        ),
    ]
)

MOCK_SCRAPER_OUTPUT = ScraperOutput(
    job_title="Senior iOS Developer",
    company_name="Apple (Simulated)",
    required_skills=["Swift", "SwiftUI", "UIKit", "CoreML", "Git"],
    soft_skills=["communication", "collaboration"],
    core_responsibilities=[
        "Build performant native iOS applications",
        "Integrate on-device machine learning features",
    ]
)

MOCK_ORIGINAL_BULLETS = [
    "Built and shipped 3 iOS apps using Swift and UIKit with 50k+ downloads.",
    "Integrated a real-time object detection feature using the Vision framework.",
]

# ── AGENT DEFINITION ──────────────────────────────────────────────────────────

critic_agent = Agent(
    role="ATS Critic and Resume Auditor",
    goal="Detect hallucinations and missing keywords in a tailored resume draft.",
    backstory="""You are a senior technical recruiter with deep knowledge of ATS 
    systems. You have reviewed thousands of resumes and have a sharp eye for 
    exaggerated or fabricated claims. You are the last line of defense before 
    a resume reaches a hiring manager.""",
    llm=groq_llm,
    verbose=True,
    allow_delegation=False,
)

# ── MAIN FUNCTION ─────────────────────────────────────────────────────────────

def run_critic_agent(
    scraper_output: ScraperOutput,
    tailoring_draft: TailoringDraft,
    original_bullets: list[str],
    revision_count: int = 0,
    use_mock: bool = True
) -> CriticReport:
    """
    Reviews the TailoringDraft against the ScraperOutput and original bullets.
    Returns a CriticReport with approval status and feedback.
    """

    if use_mock:
        print("🟡 MOCK MODE: Returning hardcoded CriticReport (0 API credits used)")

        # Simulate a passing review
        return CriticReport(
            is_approved=True,
            hallucinations_detected=[],
            missing_keywords=["SwiftUI"],  # SwiftUI not in original bullets — correctly flagged
            feedback="",
            revision_count=revision_count
        )

    # ── REAL MODE ──
    print(f"🔴 CRITIC REVIEWING draft (revision #{revision_count})...")

    # Format the draft for the prompt
    bullets_block = ""
    for item in tailoring_draft.tailored_experience:
        bullets_block += f"""
  ORIGINAL : {item.original_bullet}
  REWRITTEN: {item.rewritten_bullet}
  SKILLS   : {item.skills_highlighted}
"""

    task = Task(
        description=f"""
        {CRITIC_PROMPT}

        JOB TITLE: {scraper_output.job_title}

        REQUIRED SKILLS FROM JD:
        {chr(10).join(f'- {s}' for s in scraper_output.required_skills)}

        PROFESSIONAL SUMMARY (check for role alignment):
        {tailoring_draft.professional_summary}

        BULLET POINT REVIEW (original vs rewritten):
        {bullets_block}

        ORIGINAL RESUME BULLETS (ground truth):
        {chr(10).join(f'{i+1}. {b}' for i, b in enumerate(original_bullets))}

        CURRENT REVISION COUNT: {revision_count}
        """,
        agent=critic_agent,
        expected_output="A JSON object matching the CriticReport schema."
    )

    crew = Crew(agents=[critic_agent], tasks=[task])
    result = crew.kickoff()

    # Strip markdown code fences if present (LLM sometimes ignores the "no markdown" instruction)
    raw_json = result.raw.strip()
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]  # Extract content between fences
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]  # Remove "json" language tag
        raw_json = raw_json.strip()
    
    report = CriticReport.model_validate_json(raw_json)
    report.revision_count = revision_count
    return report


# ── QUICK TEST ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from schemas.contracts import TailoredExperience

    draft = TailoringDraft(
        professional_summary=(
            "Results-driven iOS Engineer with hands-on experience in Swift, UIKit, "
            "and on-device ML using the Vision framework."
        ),
        tailored_experience=[
            TailoredExperience(
                original_bullet="Built and shipped 3 iOS apps using Swift and UIKit with 50k+ downloads.",
                rewritten_bullet="Engineered and launched 3 production iOS applications using Swift and UIKit, achieving 50k+ downloads.",
                skills_highlighted=["Swift", "UIKit"],
                source_section="experience"
            ),
            TailoredExperience(
                original_bullet="Integrated a real-time object detection feature using the Vision framework.",
                rewritten_bullet="Implemented real-time object detection leveraging Apple's Vision framework and CoreML.",
                skills_highlighted=["CoreML", "Vision framework"],
                source_section="experience"
            ),
        ]
    )

    report = run_critic_agent(
        scraper_output=MOCK_SCRAPER_OUTPUT,
        tailoring_draft=draft,
        original_bullets=MOCK_ORIGINAL_BULLETS,
        revision_count=0,
        use_mock=True
    )

    print("\n--- CRITIC REPORT ---\n")
    print(f"APPROVED       : {report.is_approved}")
    print(f"HALLUCINATIONS : {report.hallucinations_detected}")
    print(f"MISSING KWS    : {report.missing_keywords}")
    print(f"FEEDBACK       : {report.feedback or 'None — draft approved!'}")
    print(f"REVISION COUNT : {report.revision_count}")