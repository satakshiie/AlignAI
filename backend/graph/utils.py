# graph/utils.py

def summarize_tailoring_outcome(gap_items: list, bullet_rewrites: list) -> str:
    """
    Generates a plain-language summary of what the tailoring pass
    actually accomplished, distinguishing "nothing to improve" from
    "no safe improvements found, but real gaps remain."

    Called after all three Tailoring calls have run, as part of
    building the final response — not a graph node itself, since
    it's pure formatting logic with no LLM call involved.
    """
    changed_bullets = [b for b in bullet_rewrites if b["changed"]]
    true_gaps = [g for g in gap_items if g["status"] == "true_gap"]
    implied_surfaced = [g for g in gap_items if g["status"] == "implied"]

    if not changed_bullets and not true_gaps:
        return "Your resume is already well-aligned with this job description — no changes needed."

    if not changed_bullets and true_gaps:
        return (
            f"We couldn't find safe ways to improve your existing bullets without "
            f"overstating your experience. However, {len(true_gaps)} genuine skill gap(s) "
            f"were identified — see your learning roadmap below for how to close them."
        )

    return (
        f"Updated {len(changed_bullets)} bullet(s) to better surface your existing experience. "
        f"{len(true_gaps)} genuine gap(s) remain — see your learning roadmap."
    )