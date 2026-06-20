from sqlalchemy.orm import Session
from models.db_models import Document, ParsedContext
from fastapi import HTTPException


def save_document_and_context(
    db: Session,
    doc_type: str,
    filename: str,
    file_path: str,
    size_mb: float,
    mime_type: str,
    extraction_method: str,
    char_count: int,
    raw_text: str,
    deterministic_fields: dict,
    parsed_data: dict
) -> dict:
    """
    Persists a single upload's full pipeline output across two tables —
    Document (file-level facts) and ParsedContext (interpreted output).
    Both are created in the same transaction so they either both succeed
    or both roll back together, never leaving an orphaned half-saved record.
    """

    # Step 1 — create the Document row
    document = Document(
        doc_type=doc_type,
        filename=filename,
        file_path=file_path,
        size_mb=size_mb,
        mime_type=mime_type,
        extraction_method=extraction_method,
        char_count=char_count,
        raw_text=raw_text
    )
    db.add(document)
    db.flush()  # flush (not commit) so document.id is generated and usable below,
                # without ending the transaction yet

    # Step 2 — create the ParsedContext row, linked via foreign key
    parsed_context = ParsedContext(
        document_id=document.id,
        deterministic_fields=deterministic_fields,
        parsed_data=parsed_data
    )
    db.add(parsed_context)

    # Step 3 — commit both inserts together
    db.commit()

    return {
        "document_id": str(document.id),
        "parsed_context_id": str(parsed_context.id)
    }


def get_document_with_context(db: Session, document_id) -> dict:
    """
    Fetches a document and its parsed context together, given a
    document_id. Used by the ATS scoring endpoint to retrieve
    already-processed resume/JD data without re-uploading or
    re-extracting anything.
    """

    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"No document found with id {document_id}"
        )

    # A document could theoretically have multiple parsed_context rows
    # over time (e.g. if extraction is re-run later with an improved
    # prompt) — grab the most recent one
    parsed_context = (
        db.query(ParsedContext)
        .filter(ParsedContext.document_id == document_id)
        .order_by(ParsedContext.parsed_at.desc())
        .first()
    )

    if not parsed_context:
        raise HTTPException(
            status_code=404,
            detail=f"No parsed data found for document {document_id}"
        )

    return {
        "doc_type": document.doc_type,
        "raw_text": document.raw_text,
        "deterministic_fields": parsed_context.deterministic_fields,
        "parsed_data": parsed_context.parsed_data
    }