from pydantic import BaseModel, Field
from typing import List, Optional

class ScraperOutput(BaseModel):
    """Contract for the data extracted from a Job Description URL."""
    job_title: str = Field(..., description="The official title of the position.")
    company_name: str = Field(..., description="The name of the hiring company.")
    required_skills: List[str] = Field(..., description="Mandatory technical and hard skills required.")
    soft_skills: List[str] = Field(..., description="Required soft skills or cultural fit attributes.")
    core_responsibilities: List[str] = Field(..., description="The main day-to-day duties of the role.")

class TailoredExperience(BaseModel):
    """A sub-model to map an old resume bullet to a new tailored one."""
    original_bullet: str = Field(..., description="The user's original resume bullet point.")
    rewritten_bullet: str = Field(..., description="The newly rewritten, tailored bullet point.")
    skills_highlighted: List[str] = Field(..., description="The specific JD skills targeted in this rewrite.")
    source_section: Optional[str] = Field(None, description="Section of resume this bullet came from e.g. 'experience', 'projects'.")

class TailoringDraft(BaseModel):
    """Contract for the Writer Agent's proposed resume rewrite."""
    professional_summary: str = Field(..., description="A newly crafted summary aligning with the role.")
    tailored_experience: List[TailoredExperience] = Field(..., description="List of rewritten bullet points.")

class CriticReport(BaseModel):
    """Contract for the QA Agent's final review."""
    is_approved: bool = Field(..., description="True if the draft is ready, False if it needs revision.")
    hallucinations_detected: List[str] = Field(default=[], description="List of skills the writer invented that were not in the original resume.")
    missing_keywords: List[str] = Field(default=[], description="Crucial JD keywords that the writer failed to include.")
    feedback: str = Field(..., description="Specific instructions for the writer to fix the draft, if not approved.")
    revision_count: int = Field(default=0, description="Tracks how many times the draft has been revised. Cap at 3.")