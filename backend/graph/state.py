from typing import TypedDict, Literal, Optional


class GapItem(TypedDict):
    skill: str
    skill_type: str
    status: Literal["true_gap", "implied"]
    confidence: float
    grounding: list[str]
    suggested_action: Optional[str]
    critic_confidence: Optional[float]
    critic_notes: Optional[str]
    needs_human_review: bool
    human_decision: Optional[str]


class BulletRewrite(TypedDict):
    source: str
    original: str
    rewritten: str
    changed: bool
    grounding: str
    confidence: float
    critic_confidence: Optional[float]
    needs_human_review: bool
    human_decision: Optional[str]


class RoadmapItem(TypedDict):
    skill: str
    priority: str
    reasoning: str
    suggested_approach: str
    estimated_timeframe: str


class TailoringState(TypedDict):
    # Inputs — set once before the graph runs
    resume_parsed_data: dict
    jd_parsed_data: dict
    ats_gaps: list[dict]

    # Populated by nodes as the graph runs
    gap_items: list[GapItem]
    bullet_rewrites: list[BulletRewrite]
    learning_roadmap: list[RoadmapItem]

    # Populated by Critic (built next)
    needs_human_review: bool