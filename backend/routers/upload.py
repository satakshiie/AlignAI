from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.schemas import UploadResponse, DocType
from services.file_services import validate_and_save
from services.extraction_service import extract_text
from services.deterministic_extraction_service import extract_deterministic_fields, categorize_links
from services.llm_extraction_service import extract_resume_data, extract_jd_data
from services.storage_service import save_document_and_context

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: DocType = Form(...),
    db: Session = Depends(get_db)
):
    result = await validate_and_save(file, doc_type.value)

    extraction_result = extract_text(result["content"])
    if not extraction_result["success"]:
        raise HTTPException(status_code=422, detail=extraction_result["error"])

    deterministic = extract_deterministic_fields(
        extraction_result["text"], doc_type.value, extraction_result["hyperlinks"]
    )
    links = categorize_links(extraction_result["hyperlinks"])
    deterministic["categorized_links"] = links

    if doc_type == DocType.resume:
        llm_result = extract_resume_data(
            deterministic["sections"], extraction_result["text"], extraction_result["method"]
        )
    else:
        llm_result = extract_jd_data(
            deterministic["sections"], extraction_result["text"], extraction_result["method"]
        )

    if not llm_result["success"]:
        raise HTTPException(status_code=422, detail=llm_result["error"])

    # Persist everything to PostgreSQL
    save_result = save_document_and_context(
        db=db,
        doc_type=doc_type.value,
        filename=result["filename"],
        file_path=result["saved_path"],
        size_mb=result["size_mb"],
        mime_type=result["mime_type"],
        extraction_method=extraction_result["method"],
        char_count=extraction_result["char_count"],
        raw_text=extraction_result["text"],
        deterministic_fields=deterministic,
        parsed_data=llm_result["data"]
    )

    return UploadResponse(
        success=True,
        doc_type=doc_type,
        filename=result["filename"],
        size_mb=result["size_mb"],
        mime_type=result["mime_type"],
        message=f"{doc_type.value} uploaded, validated, parsed, and saved successfully.",
        extraction_method=extraction_result["method"],
        char_count=extraction_result["char_count"],
        extracted_text=extraction_result["text"],
        deterministic_fields=deterministic,
        parsed_data=llm_result["data"]
    )