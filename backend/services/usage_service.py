import hashlib
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, Request
from models.db_models import UsageLog

MAX_FULL_RUNS_PER_DAY = 1


def hash_identifier(raw_identifier: str) -> str:
    """
    Hashes the IP address before storing it. We don't need the raw IP
    for anything — just need to recognize 'this is the same source
    asking again today' — so storing a hash instead avoids holding
    onto raw IP addresses longer than necessary.
    """
    return hashlib.sha256(raw_identifier.encode()).hexdigest()


def get_identifier(request: Request) -> str:
    """
    Extracts a usage identifier from the request. Uses IP address as
    a placeholder until real user auth exists — isolated here so
    swapping to request.state.user_id later only requires changing
    this one function, nothing else in the usage-checking logic.
    """
    client_ip = request.client.host if request.client else "unknown"
    return hash_identifier(client_ip)


def check_and_increment_usage(db: Session, identifier: str) -> None:
    """
    Checks whether this identifier has used up today's free run.
    Raises HTTPException if the limit is already reached.
    If under the limit, increments the count — this happens BEFORE
    the actual pipeline runs, so a user can't fire off multiple
    concurrent requests to slip past the check (see note below on
    why this isn't fully race-proof yet).
    """
    today = date.today()

    usage_row = (
        db.query(UsageLog)
        .filter(and_(UsageLog.identifier == identifier, UsageLog.usage_date == today))
        .first()
    )

    if usage_row is None:
        # First use today for this identifier
        usage_row = UsageLog(identifier=identifier, usage_date=today, full_runs_count=0)
        db.add(usage_row)
        db.flush()

    if usage_row.full_runs_count >= MAX_FULL_RUNS_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit reached ({MAX_FULL_RUNS_PER_DAY} per day). Please try again tomorrow."
        )

    usage_row.full_runs_count += 1
    db.commit()


def get_remaining_usage(db: Session, identifier: str) -> dict:
    """
    Returns how many runs this identifier has left today —
    useful for the frontend to show 'you have 1 run remaining today'
    before the user even attempts an action.
    """
    today = date.today()

    usage_row = (
        db.query(UsageLog)
        .filter(and_(UsageLog.identifier == identifier, UsageLog.usage_date == today))
        .first()
    )

    used = usage_row.full_runs_count if usage_row else 0
    remaining = max(0, MAX_FULL_RUNS_PER_DAY - used)

    return {"used_today": used, "remaining_today": remaining, "limit": MAX_FULL_RUNS_PER_DAY}