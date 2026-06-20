from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.schemas import ATSScoreRequest, ATSScoreResponse
from services.storage_service import get_document_with_context
from services.ats_engine import compute_ats_score

router = APIRouter(prefix="/api", tags=["ats"])


@router.post("/ats-score", response_model=ATSScoreResponse)
async def get_ats_score(
    request: ATSScoreRequest,
    db: Session = Depends(get_db)
):
    # Fetch both documents' stored data
    resume = get_document_with_context(db, request.resume_document_id)
    jd = get_document_with_context(db, request.jd_document_id)

    # Sanity check — make sure the IDs actually correspond to the
    # expected document types, since nothing stops a caller from
    # accidentally swapping resume_document_id and jd_document_id
    if resume["doc_type"] != "resume":
        raise HTTPException(
            status_code=400,
            detail=f"Document {request.resume_document_id} is not a resume (found: {resume['doc_type']})"
        )

    if jd["doc_type"] != "jd":
        raise HTTPException(
            status_code=400,
            detail=f"Document {request.jd_document_id} is not a JD (found: {jd['doc_type']})"
        )

    result = compute_ats_score(
        resume_parsed_data=resume["parsed_data"],
        resume_deterministic=resume["deterministic_fields"],
        resume_raw_text=resume["raw_text"],
        jd_parsed_data=jd["parsed_data"],
        jd_deterministic=jd["deterministic_fields"],
        jd_raw_text=jd["raw_text"]
    )

    return ATSScoreResponse(
        success=True,
        **result
    )