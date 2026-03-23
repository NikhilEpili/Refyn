"""Security Agent."""

from agents.base_agent import BaseAgent
from agents.prompts import SECURITY_PROMPT, SECURITY_FOCUS

class SecurityAgent(BaseAgent):
    """Agent focused on identifying security vulnerabilities."""
    def __init__(self):
        super().__init__(
            role=SECURITY_PROMPT,
            focus_area=SECURITY_FOCUS,
            agent_type="security"
        )
