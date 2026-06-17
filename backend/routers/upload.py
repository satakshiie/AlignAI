from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.schemas import UploadResponse, DocType
from services.file_service import validate_and_save

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: DocType = Form(...)
):
    # doc_type comes from the form — either "resume" or "jd"
    # FastAPI validates the enum automatically before this function runs

    result = await validate_and_save(file, doc_type.value)

    return UploadResponse(
        success=True,
        doc_type=doc_type,
        filename=result["filename"],
        size_mb=result["size_mb"],
        mime_type=result["mime_type"],
        message=f"{doc_type.value} uploaded and validated successfully."
    )