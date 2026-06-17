from pydantic import BaseModel
from pydantic import BaseModel
from enum import Enum


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