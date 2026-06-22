from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import TailoringState
from graph.nodes.skill_gap_resolver import skill_gap_resolver_node
from graph.nodes.bullet_rewriter import bullet_rewriter_node
from graph.nodes.roadmap_generator import roadmap_generator_node
from graph.nodes.critic import critic_node
from graph.nodes.human_review import human_review_node



def route_after_critic(state: TailoringState) -> str:
    """
    Decides where to go after the Critic runs. This is the actual
    branching logic LangGraph is built for — a plain function chain
    would need to handle this pause/resume itself.
    """
    return "needs_review" if state["needs_human_review"] else "approved"


def build_tailoring_graph():
    """
    Builds the full Tailoring agent graph: Skill Gap Resolver → Bullet
    Rewriter → Roadmap Generator → Critic → (conditionally) Human Review.
    """
    graph = StateGraph(TailoringState)

    graph.add_node("skill_gap_resolver", skill_gap_resolver_node)
    graph.add_node("bullet_rewriter", bullet_rewriter_node)
    graph.add_node("roadmap_generator", roadmap_generator_node)
    graph.add_node("critic", critic_node)
    graph.add_node("human_review", human_review_node)

    graph.set_entry_point("skill_gap_resolver")
    graph.add_edge("skill_gap_resolver", "bullet_rewriter")
    graph.add_edge("bullet_rewriter", "roadmap_generator")
    graph.add_edge("roadmap_generator", "critic")

    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "needs_review": "human_review",
            "approved": END
        }
    )

    graph.add_edge("human_review", END)

    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)