import hashlib
import json
from sqlalchemy.orm import Session
from models.db_models import ResultCache


def compute_cache_key(resume_text: str, jd_text: str) -> str:
    """
    Builds a stable cache key from both documents' raw text. If either
    document changes even slightly (different resume version, different
    JD), the hash changes and we correctly treat it as a new request —
    no stale cache hits on genuinely different content.
    """
    combined = f"{resume_text.strip()}||{jd_text.strip()}"
    return hashlib.sha256(combined.encode()).hexdigest()


def get_cached_result(db: Session, cache_key: str) -> dict | None:
    """
    Looks up a cached result. Returns the parsed result dict if found,
    None if this exact resume+JD pair hasn't been processed before.
    """
    cached = db.query(ResultCache).filter(ResultCache.cache_key == cache_key).first()

    if cached:
        return json.loads(cached.result_data)

    return None


def save_result_to_cache(db: Session, cache_key: str, result: dict) -> None:
    """
    Saves a result to the cache, keyed by the resume+JD content hash.
    """
    cached_entry = ResultCache(
        cache_key=cache_key,
        result_data=json.dumps(result)
    )
    db.add(cached_entry)
    db.commit()