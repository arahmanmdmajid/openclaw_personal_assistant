"""
Hermes Agent Orchestrator
--------------------------
Routes incoming messages to the appropriate agent based on keyword analysis.
Maintains a simple conversation log for observability.
"""

import logging
import re
from datetime import datetime
from typing import Optional

from models import ModelManager
from agents import ResearchAgent, PlanningAgent, CodeAgent, AgentResponse

logger = logging.getLogger(__name__)

# ── Routing keyword maps ────────────────────────────────────────

RESEARCH_KEYWORDS = {
    "research", "search", "find", "look up", "latest", "news",
    "what is", "tell me about", "summarize", "article", "paper",
    "information about", "learn about",
}

PLANNING_KEYWORDS = {
    "plan", "schedule", "task", "roadmap", "organize", "priority",
    "what should i do", "next steps", "weekly", "daily", "project",
    "goal", "milestone", "breakdown", "how do i approach",
}

CODE_KEYWORDS = {
    "code", "bug", "error", "debug", "review", "github", "commit",
    "issue", "pull request", "function", "class", "script", "fix",
    "exception", "traceback", "import", "```",
}


class HermesOrchestrator:
    """Central router that dispatches messages to the right agent."""

    def __init__(self, model_backend: str = "claude"):
        self.model = ModelManager(backend=model_backend)
        self.research_agent = ResearchAgent(self.model)
        self.planning_agent = PlanningAgent(self.model)
        self.code_agent = CodeAgent(self.model)
        self._log: list[dict] = []

    # ── Public ──────────────────────────────────────────────────

    def handle(self, message: str, user_id: Optional[str] = None) -> AgentResponse:
        """Route message and return agent response."""
        agent = self._route(message)
        logger.info("Routing to %s (user=%s)", agent.name, user_id)

        response = agent.handle(message)
        self._record(message, response, user_id)
        return response

    def switch_model(self, backend: str) -> None:
        self.model.switch_backend(backend)
        logger.info("Orchestrator switched to backend: %s", backend)

    def get_log(self) -> list[dict]:
        return list(self._log)

    def benchmark(self, prompt: str) -> dict:
        """Run a prompt through both models for comparison."""
        return self.model.benchmark(prompt)

    # ── Routing logic ────────────────────────────────────────────

    def _route(self, message: str):
        lower = message.lower()

        # Code agent wins if there's a code block or GitHub URL
        if "```" in message or "github.com/" in lower:
            return self.code_agent

        scores = {
            "research": self._score(lower, RESEARCH_KEYWORDS),
            "planning": self._score(lower, PLANNING_KEYWORDS),
            "code": self._score(lower, CODE_KEYWORDS),
        }

        best = max(scores, key=lambda k: scores[k])

        if scores[best] == 0:
            # Default: research agent handles unknown queries
            return self.research_agent

        return {
            "research": self.research_agent,
            "planning": self.planning_agent,
            "code": self.code_agent,
        }[best]

    @staticmethod
    def _score(text: str, keywords: set[str]) -> int:
        return sum(1 for kw in keywords if kw in text)

    # ── Logging ─────────────────────────────────────────────────

    def _record(self, message: str, response: AgentResponse, user_id: Optional[str]) -> None:
        self._log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "message": message[:200],
                "agent": response.agent_name,
                "skills": response.skills_used,
                "tools": response.tools_used,
                "model": response.model_used,
                "success": response.success,
            }
        )
