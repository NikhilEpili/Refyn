"""Performance Agent."""

from agents.base_agent import BaseAgent
from agents.prompts import PERFORMANCE_PROMPT, PERFORMANCE_FOCUS

class PerformanceAgent(BaseAgent):
    """Agent focused on identifying performance bottlenecks."""
    def __init__(self):
        super().__init__(
            role=PERFORMANCE_PROMPT,
            focus_area=PERFORMANCE_FOCUS,
            agent_type="performance"
        )
