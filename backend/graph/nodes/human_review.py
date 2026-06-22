# graph/nodes/human_review.py
from langgraph.types import interrupt


def human_review_node(state: dict) -> dict:
    """
    LangGraph node — pauses execution and surfaces flagged items for
    human review. Uses LangGraph's interrupt() to genuinely halt the
    graph here, rather than just returning a "please review" flag and
    hoping the calling code handles pausing/resuming itself.
    """

    gap_items = state.get("gap_items", [])
    bullet_rewrites = state.get("bullet_rewrites", [])

    flagged_gaps = [item for item in gap_items if item["needs_human_review"]]
    flagged_bullets = [b for b in bullet_rewrites if b["needs_human_review"]]

    # interrupt() halts execution HERE and returns this payload to
    # whatever called graph.invoke() or graph.stream(). The graph
    # state is checkpointed — execution doesn't resume until the
    # caller invokes the graph again with a human's decision.
    human_input = interrupt({
        "flagged_gaps": flagged_gaps,
        "flagged_bullets": flagged_bullets,
        "message": "These items need your review before finalizing."
    })

    # Once resumed, human_input contains whatever the caller passed
    # back in — expected shape: a dict mapping each flagged item's
    # identifier to a decision ("approved", "rejected", "edited")
    decisions = human_input.get("decisions", {})

    updated_gaps = []
    for item in gap_items:
        if item["needs_human_review"]:
            decision = decisions.get(item["skill"], "approved")  # default to approved if unspecified
            updated_gaps.append({**item, "human_decision": decision})
        else:
            updated_gaps.append(item)

    updated_bullets = []
    for bullet in bullet_rewrites:
        if bullet["needs_human_review"]:
            decision = decisions.get(bullet["original"], "approved")
            updated_bullets.append({**bullet, "human_decision": decision})
        else:
            updated_bullets.append(bullet)

    return {
        "gap_items": updated_gaps,
        "bullet_rewrites": updated_bullets
    }