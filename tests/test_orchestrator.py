"""
Unit tests for routing logic (no API calls required).
Run: pytest tests/
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch
from orchestrator import HermesOrchestrator


def _make_orchestrator():
    """Create orchestrator with mocked model backend."""
    with patch("orchestrator.ModelManager") as MockMM:
        mock_mm = MockMM.return_value
        orc = HermesOrchestrator.__new__(HermesOrchestrator)
        orc.model = mock_mm
        orc._log = []

        # Patch individual agents
        orc.research_agent = MagicMock()
        orc.research_agent.name = "research_agent"
        orc.planning_agent = MagicMock()
        orc.planning_agent.name = "planning_agent"
        orc.code_agent = MagicMock()
        orc.code_agent.name = "code_agent"
        return orc


class TestRouting:
    def test_research_routing(self):
        orc = _make_orchestrator()
        agent = orc._route("search for the latest news on Python")
        assert agent.name == "research_agent"

    def test_planning_routing(self):
        orc = _make_orchestrator()
        agent = orc._route("create a weekly plan for my project tasks")
        assert agent.name == "planning_agent"

    def test_code_routing_via_backticks(self):
        orc = _make_orchestrator()
        agent = orc._route("Review this ```python\nprint('hello')```")
        assert agent.name == "code_agent"

    def test_code_routing_via_github_url(self):
        orc = _make_orchestrator()
        agent = orc._route("Check issues at github.com/user/repo")
        assert agent.name == "code_agent"

    def test_default_fallback_to_research(self):
        orc = _make_orchestrator()
        agent = orc._route("hello there")
        assert agent.name == "research_agent"

    def test_planning_keywords(self):
        for msg in ["make a roadmap", "what should I do next", "set schedule"]:
            orc = _make_orchestrator()
            agent = orc._route(msg)
            assert agent.name == "planning_agent", f"Expected planning for: {msg!r}"

    def test_code_keywords(self):
        for msg in ["debug this error", "review my function", "fix this bug"]:
            orc = _make_orchestrator()
            agent = orc._route(msg)
            assert agent.name == "code_agent", f"Expected code for: {msg!r}"
