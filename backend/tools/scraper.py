import os
from firecrawl import Firecrawl
from dotenv import load_dotenv

load_dotenv()

MOCK_JOB_DESCRIPTION = """
# Senior iOS Developer
**Company:** Apple (Simulated)

## About the Role
We are looking for a highly motivated iOS Developer to join our core experiences team.
You will be responsible for building highly performant, accessible, and beautiful native applications.

## Required Skills
* 3+ years of professional iOS development experience.
* Deep mastery of **Swift**, **SwiftUI**, and **UIKit**.
* Experience with on-device machine learning (CoreML, Vision framework).
* Strong understanding of Git and collaborative GitHub workflows.

## Soft Skills
* Strong communication skills and cross-functional collaboration.
* A keen eye for UI/UX design and aesthetics.
"""

def scrape_job_description(url: str, use_mock: bool = True) -> str:
    """
    Takes a job board URL and returns the Markdown text.
    If use_mock is True, returns fake data to save API credits.
    """
    if use_mock:
        print(f"🟡 MOCK MODE: Returning fake data for {url} (0 credits used)")
        return MOCK_JOB_DESCRIPTION

    print(f"🟢 REAL SCRAPE: Fetching URL: {url}...")
    app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

    try:
        scraped_data = app.scrape_url(
            url,
            params={'formats': ['markdown']}
        )

        if hasattr(scraped_data, 'markdown'):
            markdown_text = scraped_data.markdown or ''
        elif isinstance(scraped_data, dict):
            markdown_text = scraped_data.get('markdown', '')
        else:
            markdown_text = str(scraped_data)

        if not markdown_text:
            return "Error: Could not extract markdown from the page."

        print("Scrape successful!")
        return markdown_text

    except Exception as e:
        return f"An error occurred while scraping: {str(e)}"


if __name__ == "__main__":
    test_url = "https://jobs.apple.com/en-us/details/200547076/ios-engineer"
    result = scrape_job_description(test_url, use_mock=True)
    print("\n--- Scraped Job Description ---\n")
    print(result)