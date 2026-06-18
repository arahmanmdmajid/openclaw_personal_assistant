"""Base class for all Hermes agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentResponse:
    agent_name: str
    success: bool
    message: str
    skills_used: list[str] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    model_used: str = ""
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __str__(self) -> str:
        return self.message


class BaseAgent(ABC):
    """
    Every Hermes agent has:
      - name        : unique identifier shown in responses
      - description : what kinds of requests it handles
      - handle()    : process a user message and return AgentResponse
    """

    name: str = "base_agent"
    description: str = "Base agent — override this."

    @abstractmethod
    def handle(self, message: str, **kwargs) -> AgentResponse:
        ...

    def _error_response(self, reason: str) -> AgentResponse:
        return AgentResponse(
            agent_name=self.name,
            success=False,
            message=f"Sorry, I encountered an error: {reason}",
            error=reason,
        )

    def __repr__(self) -> str:
        return f"<Agent:{self.name}>"
