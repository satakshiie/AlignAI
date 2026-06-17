from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.schemas import UploadResponse, DocType
from services.file_services import validate_and_save
from services.extraction_service import extract_text

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: DocType = Form(...)
):
    # Step 1 — validate and save the file, get back raw bytes too
    result = await validate_and_save(file, doc_type.value)

    # Step 2 — extract text using those same bytes
    extraction_result = extract_text(result["content"])

    if not extraction_result["success"]:
        raise HTTPException(
            status_code=422,
            detail=extraction_result["error"]
        )

    # Step 3 — build the full response including extracted text
    return UploadResponse(
        success=True,
        doc_type=doc_type,
        filename=result["filename"],
        size_mb=result["size_mb"],
        mime_type=result["mime_type"],
        message=f"{doc_type.value} uploaded, validated, and text extracted successfully.",
        extraction_method=extraction_result["method"],
        char_count=extraction_result["char_count"],
        extracted_text=extraction_result["text"]
    )