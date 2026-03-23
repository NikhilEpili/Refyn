"""Abstract base agent for LLM interactions."""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from app.config import settings
import structlog
from typing import Any
from agents.schemas import ReviewComment

logger = structlog.get_logger()

class ReviewCommentList(BaseModel):
    comments: list[ReviewComment]

class BaseAgent:
    """Base class for all specific review agents."""
    
    def __init__(self, role: str, focus_area: str, agent_type: str):
        self.role = role
        self.focus_area = focus_area
        self.agent_type = agent_type
        
        api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else ""
        self.llm = ChatOpenAI(
            model="gpt-4o" if getattr(settings, "llm_provider", "openai") == "openai" else "mistral-large-latest",
            api_key=api_key,
            temperature=0.1
        )
        self.parser = PydanticOutputParser(pydantic_object=ReviewCommentList)
        
    async def run(self, pr_diff: str, context_chunks: list[str], strictness: float) -> list[ReviewComment]:
        """Execute the agent review on a PR diff with RAG context."""
        from agents.prompts import SYSTEM_PROMPT_TEMPLATE
        
        system_instructions = SYSTEM_PROMPT_TEMPLATE.format(
            role=self.role,
            focus_area=self.focus_area,
            strictness=strictness
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_instructions),
            ("user", "Context Chunks:\n{context}\n\nPR Diff:\n{diff}\n\nFormat Instructions:\n{format_instructions}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        context_str = "\n\n".join(context_chunks) if context_chunks else "No relevant context found."
        
        try:
            result = await chain.ainvoke({
                "context": context_str,
                "diff": pr_diff,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Ensure agent_type is strictly set to self.agent_type to prevent hallucination
            for comment in result.comments:
                comment.agent_type = self.agent_type
                
            return result.comments
        except Exception as e:
            await logger.aerror(f"{self.agent_type} agent failed", error=str(e))
            return []
