"""LangGraph orchestrator for the review engine."""

from langgraph.graph import StateGraph, START, END
from agents.schemas import ReviewState, ReviewComment
from agents.security_agent import SecurityAgent
from agents.performance_agent import PerformanceAgent
from agents.style_agent import StyleAgent
from app.config import settings

def _get_strictness(state: ReviewState, agent_type: str) -> float:
    return state.get("strictness", {}).get(agent_type, 3.0)

async def run_security_agent(state: ReviewState) -> dict[str, list[ReviewComment]]:
    agent = SecurityAgent()
    strictness = _get_strictness(state, "security")
    comments = await agent.run(state["pr_diff"], state["context_chunks"], strictness)
    return {"security_comments": comments}

async def run_performance_agent(state: ReviewState) -> dict[str, list[ReviewComment]]:
    agent = PerformanceAgent()
    strictness = _get_strictness(state, "performance")
    comments = await agent.run(state["pr_diff"], state["context_chunks"], strictness)
    return {"performance_comments": comments}

async def run_style_agent(state: ReviewState) -> dict[str, list[ReviewComment]]:
    agent = StyleAgent()
    strictness = _get_strictness(state, "style")
    comments = await agent.run(state["pr_diff"], state["context_chunks"], strictness)
    return {"style_comments": comments}

def retrieve_strictness_weights(state: ReviewState) -> dict[str, dict[str, float]]:
    # Simulated Redis fetch for MVP
    # Ideally retrieved from feedback service
    weights = state.get("strictness", {})
    if not weights:
        weights = {"security": 3.0, "performance": 3.0, "style": 3.0}
    return {"strictness": weights}

def aggregate_and_deduplicate(state: ReviewState) -> dict[str, list[ReviewComment]]:
    """Filter comments by confidence and deduplicate."""
    all_comments = []
    all_comments.extend(state.get("security_comments", []))
    all_comments.extend(state.get("performance_comments", []))
    all_comments.extend(state.get("style_comments", []))
    
    # 1. Confidence filter
    threshold = settings.confidence_threshold
    high_confidence = [c for c in all_comments if c.confidence >= threshold]
    
    # 2. Deduplication by file and line (keep highest confidence)
    deduped = {}
    for comment in high_confidence:
        key = f"{comment.file_path}:{comment.line_number}"
        if key not in deduped or comment.confidence > deduped[key].confidence:
            deduped[key] = comment
            
    return {"final_comments": list(deduped.values())}

def build_review_graph() -> Any:
    """Build the LangGraph state machine."""
    graph = StateGraph(ReviewState)
    
    graph.add_node("retrieve_weights", retrieve_strictness_weights)
    graph.add_node("security", run_security_agent)
    graph.add_node("performance", run_performance_agent)
    graph.add_node("style", run_style_agent)
    graph.add_node("aggregate", aggregate_and_deduplicate)
    
    graph.add_edge(START, "retrieve_weights")
    graph.add_edge("retrieve_weights", "security")
    graph.add_edge("retrieve_weights", "performance")
    graph.add_edge("retrieve_weights", "style")
    graph.add_edge("security", "aggregate")
    graph.add_edge("performance", "aggregate")
    graph.add_edge("style", "aggregate")
    graph.add_edge("aggregate", END)
    
    return graph.compile()

async def run_review(pr_diff: str, context_chunks: list[str], repo_id: str, pr_number: int) -> list[ReviewComment]:
    """Entry point to run the full review pipeline."""
    graph = build_review_graph()
    initial_state = {
        "pr_diff": pr_diff,
        "context_chunks": context_chunks,
        "repo_id": repo_id,
        "pr_number": pr_number,
        "strictness": {},
        "security_comments": [],
        "performance_comments": [],
        "style_comments": [],
        "final_comments": []
    }
    
    result = await graph.ainvoke(initial_state)
    return result.get("final_comments", [])
