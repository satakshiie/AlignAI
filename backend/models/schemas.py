from pydantic import BaseModel
from enum import Enum
from typing import Any
from uuid import UUID


class DocType(str, Enum):
    resume = "resume"
    jd = "jd"


class UploadResponse(BaseModel):
    success: bool
    doc_type: DocType
    filename: str
    size_mb: float
    mime_type: str
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