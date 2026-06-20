import uuid
import hashlib
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB


class UsageLog(Base):
    """
    Tracks daily usage per identifier (IP address for now, swappable
    for a real user_id once auth exists). One row per identifier per day —
    incremented, not appended, to keep this table small and fast to query.
    """
    __tablename__ = "usage_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(String, nullable=False)   # IP address hash, or future user_id
    usage_date = Column(Date, nullable=False, server_default=func.current_date())
    full_runs_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResultCache(Base):
    """
    Caches the full ATS/tailoring output for a given resume+JD pair,
    keyed by a hash of both documents' content. If the same pair is
    scored again with no changes, we return the cached result instead
    of re-calling the LLM at all.
    """
    __tablename__ = "result_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String, nullable=False, unique=True, index=True)
    result_data = Column(Text, nullable=False)  # JSON-serialized result
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    """
    One row per uploaded file — resume or JD. Stores file metadata
    and a pointer to where the actual PDF lives on disk, not the
    binary content itself (binary blobs don't belong in relational rows).
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_type = Column(String(10), nullable=False)  # "resume" or "jd"
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)      # where it lives on disk/S3
    size_mb = Column(Float, nullable=False)
    mime_type = Column(String, nullable=False)
    extraction_method = Column(String, nullable=False)  # "pymupdf" or "tesseract_ocr"
    char_count = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=False)          # full extracted text
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class ParsedContext(Base):
    """
    The structured output for a document — both the deterministic
    (regex/spaCy) fields and the LLM-parsed fields, stored as JSONB
    so the differing resume/JD shapes don't need separate tables.
    """
    __tablename__ = "parsed_context"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    deterministic_fields = Column(JSONB, nullable=False)
    parsed_data = Column(JSONB, nullable=False)

    parsed_at = Column(DateTime(timezone=True), server_default=func.now())