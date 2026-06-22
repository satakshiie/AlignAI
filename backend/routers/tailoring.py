import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from langgraph.types import Command
from database import get_db
from models.schemas import (
    TailorStartRequest, TailorStartResponse,
    TailorResumeRequest, TailorResumeResponse
)
from services.storage_service import get_document_with_context
from services.ats_engine import compute_ats_score
from services.usage_service import get_identifier, check_and_increment_usage
from services.cache_service import compute_cache_key, get_cached_result, save_result_to_cache
from graph.tailoring_graph import build_tailoring_graph
from graph.utils import summarize_tailoring_outcome

router = APIRouter(prefix="/api", tags=["tailoring"])

graph = build_tailoring_graph()  # built once at import time, reused across requests


@router.post("/tailor/start", response_model=TailorStartResponse)
async def start_tailoring(
    request_body: TailorStartRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    resume = get_document_with_context(db, request_body.resume_document_id)
    jd = get_document_with_context(db, request_body.jd_document_id)

    if resume["doc_type"] != "resume":
        raise HTTPException(status_code=400, detail="resume_document_id does not point to a resume")
    if jd["doc_type"] != "jd":
        raise HTTPException(status_code=400, detail="jd_document_id does not point to a JD")

    # Step 1 — check cache first, before touching the daily usage limit
    cache_key = compute_cache_key(resume["raw_text"], jd["raw_text"])
    cached_result = get_cached_result(db, cache_key)

    if cached_result:
        return TailorStartResponse(
            success=True,
            thread_id="cached",
            status="completed",
            from_cache=True,
            **cached_result
        )

    # Step 2 — enforce daily usage limit, only for genuinely new requests
    identifier = get_identifier(request)
    check_and_increment_usage(db, identifier)  # raises 429 if limit reached

    # Step 3 — run the ATS engine to get gaps (reusing your existing Phase 3 work)
    ats_result = compute_ats_score(
        resume_parsed_data=resume["parsed_data"],
        resume_deterministic=resume["deterministic_fields"],
        resume_raw_text=resume["raw_text"],
        jd_parsed_data=jd["parsed_data"],
        jd_deterministic=jd["deterministic_fields"],
        jd_raw_text=jd["raw_text"]
    )

    # Step 4 — run the Tailoring graph
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "resume_parsed_data": resume["parsed_data"],
        "jd_parsed_data": jd["parsed_data"],
        "ats_gaps": ats_result["gaps"],
        "gap_items": [],
        "bullet_rewrites": [],
        "learning_roadmap": [],
        "needs_human_review": False
    }

    result = graph.invoke(initial_state, config=config)

    # Step 5 — branch based on whether the graph paused for human review
    if "__interrupt__" in result:
        interrupt_payload = result["__interrupt__"][0].value
        return TailorStartResponse(
            success=True,
            thread_id=thread_id,
            status="needs_review",
            flagged_gaps=interrupt_payload["flagged_gaps"],
            flagged_bullets=interrupt_payload["flagged_bullets"]
        )

    # Graph completed without needing human review — finalize and cache
    summary = summarize_tailoring_outcome(result["gap_items"], result["bullet_rewrites"])
    final_payload = {
        "gap_items": result["gap_items"],
        "bullet_rewrites": result["bullet_rewrites"],
        "learning_roadmap": result["learning_roadmap"],
        "summary": summary
    }
    save_result_to_cache(db, cache_key, final_payload)

    return TailorStartResponse(
        success=True,
        thread_id=thread_id,
        status="completed",
        **final_payload
    )


@router.post("/tailor/resume", response_model=TailorResumeResponse)
async def resume_tailoring(request_body: TailorResumeRequest):
    config = {"configurable": {"thread_id": request_body.thread_id}}

    result = graph.invoke(
        Command(resume={"decisions": request_body.decisions}),
        config=config
    )

    summary = summarize_tailoring_outcome(result["gap_items"], result["bullet_rewrites"])

    return TailorResumeResponse(
        success=True,
        gap_items=result["gap_items"],
        bullet_rewrites=result["bullet_rewrites"],
        learning_roadmap=result["learning_roadmap"],
        summary=summary
    )