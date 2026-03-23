"""Reaction webhook handler."""

import structlog
from feedback.store import insert_feedback

logger = structlog.get_logger()

async def handle_reaction_event(payload: dict) -> None:
    """Parse and handle pull_request_review_comment reaction events."""
    action = payload.get("action")
    if action != "created":
        return
        
    comment = payload.get("comment", {})
    reaction_data = payload.get("reaction", {})
    repo_full_name = payload.get("repository", {}).get("full_name")
    
    emoji = reaction_data.get("content")
    if emoji == "+1":
        reaction_val = 1
    elif emoji == "-1":
        reaction_val = -1
    else:
        return
        
    body = comment.get("body", "")
    
    agent_type = "style" # default
    if "Security" in body: agent_type = "security"
    elif "Performance" in body: agent_type = "performance"
    
    comment_id = comment.get("id")
    
    await logger.ainfo("Caught reaction", repo=repo_full_name, agent=agent_type, reaction=reaction_val)
    
    confidence = 0.8
    await insert_feedback(repo_full_name, comment_id, agent_type, reaction_val, confidence)
