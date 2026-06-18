from sqlalchemy.orm import Session
from models.db_models import Document, ParsedContext


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