"""Shared data models for the review engine."""

from typing import TypedDict, Literal
from pydantic import BaseModel, Field

class ReviewComment(BaseModel):
    """Structured output for a single review comment."""
    file_path: str = Field(description="File path where the issue was found")
    line_number: int = Field(description="Line number of the issue")
    body: str = Field(description="Human-readable comment, including RAG reference if available")
    severity: Literal["blocking", "suggestion", "nit"] = Field(description="Severity of the issue")
    agent_type: Literal["security", "performance", "style"] = Field(description="Agent that generated the comment")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")

class ReviewState(TypedDict):
    """State graph for the LangGraph orchestrator."""
    pr_diff: str
    context_chunks: list[str]
    repo_id: str
    pr_number: int
    strictness: dict[str, float]
    
    security_comments: list[ReviewComment]
    performance_comments: list[ReviewComment]
    style_comments: list[ReviewComment]
    final_comments: list[ReviewComment]
