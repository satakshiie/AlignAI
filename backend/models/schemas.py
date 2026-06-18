from pydantic import BaseModel
from enum import Enum
from typing import Any


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