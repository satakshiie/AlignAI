
import os
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
from schemas.contracts import ScraperOutput, TailoringDraft, TailoredExperience

load_dotenv()

# ── GROQ LLM SETUP ────────────────────────────────────────────────────────────

groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

# ── MOCK DATA ────

MOCK_SCRAPER_OUTPUT = ScraperOutput(
    job_title="Senior iOS Developer",
    company_name="Apple (Simulated)",
    required_skills=["Swift", "SwiftUI", "UIKit", "CoreML", "Git"],
    soft_skills=["communication", "cross-functional collaboration", "UI/UX eye"],
    core_responsibilities=[
        "Build performant native iOS applications",
        "Integrate on-device machine learning features",
        "Collaborate with design and backend teams",
        "Conduct code reviews and mentor junior developers"
    ]
)

MOCK_ORIGINAL_RESUME_BULLETS = [
    "Built and shipped 3 iOS apps using Swift and UIKit with 50k+ downloads.",
    "Integrated a real-time object detection feature using the Vision framework.",
    "Collaborated with designers and backend engineers to define API contracts.",
    "Mentored 2 junior developers and led weekly code review sessions.",
    "Managed feature branches and pull requests using Git and GitHub.",
]

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────

TAILORING_PROMPT = """
You are an expert resume writer. Your job is to rewrite resume bullet points 
to better match a specific job description.

STRICT RULES — you must follow these without exception:
1. You may ONLY rewrite bullets using information present in the original bullet.
2. You MUST NOT invent new skills, tools, metrics, or experiences.
3. You MUST NOT add technologies not mentioned in the original bullet.
4. Every rewritten bullet must start with a strong action verb.
5. Every rewritten bullet must be one line, concise and specific.
6. You MUST highlight JD keywords naturally — do not keyword-stuff.

You will receive:
- The job title and company name
- The required skills from the JD
- The core responsibilities from the JD
- The original resume bullets (these are ground truth — do not go beyond them)

Return a JSON object matching this exact structure:
{
  "professional_summary": "A 2-3 sentence summary tailored to the role.",
  "tailored_experience": [
    {
      "original_bullet": "the original bullet text",
      "rewritten_bullet": "the rewritten bullet text",
      "skills_highlighted": ["skill1", "skill2"],
      "source_section": "experience"
    }
  ]
}

Return valid JSON only. No markdown fences. No preamble.
"""

# ── AGENT DEFINITION ──────────────────────────────────────────────────────────

tailoring_agent = Agent(
    role="Expert Resume Writer",
    goal="Rewrite resume bullets to match a job description without inventing any new experience.",
    backstory="""You are a professional resume coach with 10 years of experience 
    helping engineers land jobs at top tech companies. You are known for your 
    ability to reframe existing experience powerfully — and your strict refusal 
    to ever fabricate credentials.""",
    llm=groq_llm,   
    verbose=True,
    allow_delegation=False,
)

# ── MAIN FUNCTION ─────

def run_tailoring_agent(
    scraper_output: ScraperOutput,
    original_bullets: list[str],
    critic_feedback: str = None,
    use_mock: bool = True
) -> TailoringDraft:
    """
    Takes the ScraperOutput and original resume bullets,
    returns a TailoringDraft with rewritten bullets.
    If critic_feedback is provided, it means this is a revision run.
    """

    if use_mock:
        print("🟡 MOCK MODE: Returning hardcoded TailoringDraft (0 API credits used)")
        return TailoringDraft(
            professional_summary=(
                f"Results-driven iOS Engineer with hands-on experience in Swift, UIKit, "
                f"and on-device ML using the Vision framework. Proven ability to ship "
                f"high-quality native apps and collaborate cross-functionally with design "
                f"and backend teams. Seeking to bring strong technical and mentorship skills "
                f"to {scraper_output.company_name}."
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
                    rewritten_bullet="Implemented real-time object detection leveraging Apple's Vision framework, directly applying CoreML principles.",
                    skills_highlighted=["CoreML", "Vision framework"],
                    source_section="experience"
                ),
                TailoredExperience(
                    original_bullet="Collaborated with designers and backend engineers to define API contracts.",
                    rewritten_bullet="Drove cross-functional collaboration with design and backend teams to define and ship API contracts on schedule.",
                    skills_highlighted=["cross-functional collaboration"],
                    source_section="experience"
                ),
                TailoredExperience(
                    original_bullet="Mentored 2 junior developers and led weekly code review sessions.",
                    rewritten_bullet="Mentored 2 junior iOS developers and facilitated weekly code reviews to uphold engineering standards.",
                    skills_highlighted=["mentorship", "code review"],
                    source_section="experience"
                ),
                TailoredExperience(
                    original_bullet="Managed feature branches and pull requests using Git and GitHub.",
                    rewritten_bullet="Maintained clean Git workflows by managing feature branches and pull requests across a collaborative team.",
                    skills_highlighted=["Git", "GitHub"],
                    source_section="experience"
                ),
            ]
        )

    # ── REAL MODE ──
    print(f"🟢 REAL MODE: Tailoring resume for {scraper_output.job_title} at {scraper_output.company_name}...")

    feedback_block = ""
    if critic_feedback:
        feedback_block = f"""
        
REVISION INSTRUCTIONS FROM CRITIC:
{critic_feedback}

Fix the issues above in your rewrite. Do not repeat the same mistakes.
"""

    task = Task(
        description=f"""
        {TAILORING_PROMPT}
        {feedback_block}

        JOB TITLE: {scraper_output.job_title}
        COMPANY: {scraper_output.company_name}

        REQUIRED SKILLS:
        {chr(10).join(f'- {s}' for s in scraper_output.required_skills)}

        CORE RESPONSIBILITIES:
        {chr(10).join(f'- {r}' for r in scraper_output.core_responsibilities)}

        ORIGINAL RESUME BULLETS (ground truth — do not go beyond these):
        {chr(10).join(f'{i+1}. {b}' for i, b in enumerate(original_bullets))}
        """,
        agent=tailoring_agent,
        expected_output="A JSON object matching the TailoringDraft schema."
    )

    crew = Crew(agents=[tailoring_agent], tasks=[task])
    result = crew.kickoff()

    # Strip markdown code fences if present (LLM sometimes ignores the "no markdown" instruction)
    raw_json = result.raw.strip()
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]  # Extract content between fences
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]  # Remove "json" language tag
        raw_json = raw_json.strip()
    
    return TailoringDraft.model_validate_json(raw_json)


# ── QUICK TEST ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    draft = run_tailoring_agent(
        scraper_output=MOCK_SCRAPER_OUTPUT,
        original_bullets=MOCK_ORIGINAL_RESUME_BULLETS,
        use_mock=True
    )

    print("\n--- TAILORING DRAFT ---\n")
    print(f"SUMMARY:\n{draft.professional_summary}\n")
    print("REWRITTEN BULLETS:")
    for item in draft.tailored_experience:
        print(f"\n  ORIGINAL : {item.original_bullet}")
        print(f"  REWRITTEN: {item.rewritten_bullet}")
        print(f"  SKILLS   : {item.skills_highlighted}")