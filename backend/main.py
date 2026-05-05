# main.py

from dotenv import load_dotenv
from schemas.contracts import ScraperOutput, TailoringDraft, CriticReport
from tools.scraper import scrape_job_description
from agents.tailoring import run_tailoring_agent, MOCK_SCRAPER_OUTPUT, MOCK_ORIGINAL_RESUME_BULLETS
from agents.critic import run_critic_agent
from tools.pdf_parser import parse_resume_pdf

load_dotenv()


MAX_RETRIES = 3
USE_MOCK = False



def run_pipeline(
    jd_url: str,
    original_bullets: list[str],
    scraper_output: ScraperOutput = None,
) -> dict:
    """
    Full pipeline:
    1. Scraper Agent   → extracts JD requirements
    2. Tailoring Agent → rewrites resume bullets
    3. Critic Agent    → reviews draft, rejects if hallucinations found
    4. Retry loop      → sends critic feedback back to writer (max 3 times)
    """

    print("\n" + "="*60)
    print("         ALIGNAI — RESUME TAILORING PIPELINE")
    print("="*60)


    print("\n📋 STEP 1: Scraping job description...")

    if USE_MOCK:

        scraper_output = MOCK_SCRAPER_OUTPUT
        print(f"🟡 MOCK: Using hardcoded JD for '{scraper_output.job_title}' at {scraper_output.company_name}")
    else:
        raw_jd = scrape_job_description(jd_url, use_mock=False)
    
        scraper_output = MOCK_SCRAPER_OUTPUT
        print(f"🟢 REAL: Scraped JD from {jd_url}")

    print(f"✅ JD extracted: {len(scraper_output.required_skills)} required skills found")


    print("\n✍️  STEP 2: Tailoring resume...")

    critic_feedback = None
    final_draft = None
    final_report = None

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n🔄 Attempt {attempt} of {MAX_RETRIES}")


        draft: TailoringDraft = run_tailoring_agent(
            scraper_output=scraper_output,
            original_bullets=original_bullets,
            critic_feedback=critic_feedback,
            use_mock=USE_MOCK
        )
        print("✅ Draft generated")

        print(f"\n🔍 STEP 3: Critic reviewing draft (attempt {attempt})...")
        report: CriticReport = run_critic_agent(
            scraper_output=scraper_output,
            tailoring_draft=draft,
            original_bullets=original_bullets,
            revision_count=attempt,
            use_mock=USE_MOCK
        )

        # ── APPROVED ──
        if report.is_approved:
            print(f"\n✅ CRITIC APPROVED the draft on attempt {attempt}!")
            final_draft = draft
            final_report = report
            break

        # ── REJECTED ──
        print(f"\n❌ CRITIC REJECTED the draft on attempt {attempt}")
        if report.hallucinations_detected:
            print(f"   Hallucinations : {report.hallucinations_detected}")
        if report.missing_keywords:
            print(f"   Missing keywords: {report.missing_keywords}")
        print(f"   Feedback: {report.feedback}")

        critic_feedback = report.feedback

        if attempt == MAX_RETRIES:
            print(f"\n⚠️  MAX RETRIES ({MAX_RETRIES}) reached. Flagging for human review.")
            final_draft = draft
            final_report = report

    # ── STEP 4: RESULTS ───────────
    print("\n" + "="*60)
    print("                      FINAL OUTPUT")
    print("="*60)

    print(f"\n📄 ROLE    : {scraper_output.job_title} @ {scraper_output.company_name}")
    print(f"✅ APPROVED : {final_report.is_approved}")
    print(f"🔄 ATTEMPTS : {final_report.revision_count}")

    if final_report.missing_keywords:
        print(f"⚠️  MISSING  : {final_report.missing_keywords} (not in original resume — cannot add)")

    print(f"\n📝 PROFESSIONAL SUMMARY:\n{final_draft.professional_summary}")

    print("\n📌 TAILORED BULLETS:")
    for i, item in enumerate(final_draft.tailored_experience, 1):
        print(f"\n  [{i}] ORIGINAL : {item.original_bullet}")
        print(f"      REWRITTEN: {item.rewritten_bullet}")
        print(f"      SKILLS   : {item.skills_highlighted}")

    print("\n" + "="*60)

    return {
        "approved": final_report.is_approved,
        "attempts": final_report.revision_count,
        "missing_keywords": final_report.missing_keywords,
        "hallucinations": final_report.hallucinations_detected,
        "draft": final_draft,
        "report": final_report
    }




if __name__ == "__main__":
    # 1. Define your inputs
    test_pdf_path = "/Users/satakshi/Downloads/Resume-Sample-2.pdf"
    test_job_url = "https://jobs.apple.com/en-us/details/200547076/ios-engineer"

    # 2. Extract the real bullets from the PDF!
    # (Make sure use_mock=False so it actually reads your file)
    print("\n📄 Extracting Original Resume...")
    extracted_bullets = parse_resume_pdf(test_pdf_path, use_mock=False)

    # 3. Pass the REAL bullets into the pipeline
    result = run_pipeline(
        jd_url=test_job_url,
        original_bullets=extracted_bullets,
    )