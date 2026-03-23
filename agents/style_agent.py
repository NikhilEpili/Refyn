"""Style Agent."""

from agents.base_agent import BaseAgent
from agents.prompts import STYLE_PROMPT, STYLE_FOCUS

class StyleAgent(BaseAgent):
    """Agent focused on code style, readability, and conventions."""
    def __init__(self):
        super().__init__(
            role=STYLE_PROMPT,
            focus_area=STYLE_FOCUS,
            agent_type="style"
        )
