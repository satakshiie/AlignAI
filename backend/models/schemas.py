from pydantic import BaseModel
from enum import Enum
from typing import Any
from uuid import UUID



class TailorStartRequest(BaseModel):
    resume_document_id: UUID
    jd_document_id: UUID


class TailorStartResponse(BaseModel):
    success: bool
    thread_id: str
    status: str  # "completed" or "needs_review"
    from_cache: bool = False
    # Populated if status == "completed"
    gap_items: list[dict[str, Any]] | None = None
    bullet_rewrites: list[dict[str, Any]] | None = None
    learning_roadmap: list[dict[str, Any]] | None = None
    summary: str | None = None
    # Populated if status == "needs_review"
    flagged_gaps: list[dict[str, Any]] | None = None
    flagged_bullets: list[dict[str, Any]] | None = None


class TailorResumeRequest(BaseModel):
    thread_id: str
    decisions: dict[str, str]  # maps skill/bullet identifier -> "approved"/"rejected"/"edited"


class TailorResumeResponse(BaseModel):
    success: bool
    gap_items: list[dict[str, Any]]
    bullet_rewrites: list[dict[str, Any]]
    learning_roadmap: list[dict[str, Any]]
    summary: str


class DocType(str, Enum):
    resume = "resume"
    jd = "jd"


class UploadResponse(BaseModel):
    success: bool
    doc_type: DocType
    filename: str
    size_mb: float
    mime_type: str
    document_id: UUID
    message: str
    extraction_method: str
    char_count: int
    extracted_text: str
    deterministic_fields: dict[str, Any]   # name, email, phone, dates, sections, links
    parsed_data: dict[str, Any]            # the LLM-structured output (resume or JD shape)



class ATSScoreRequest(BaseModel):
    resume_document_id: UUID
    jd_document_id: UUID


class ATSScoreResponse(BaseModel):
    success: bool
    final_score: int
    layer_breakdown: dict[str, Any]
    skill_analysis: dict[str, Any]
    structural_analysis: dict[str, Any]
    content_similarity_detail: dict[str, Any]
    gaps: list[dict[str, Any]]