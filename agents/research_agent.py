"""
Research Agent
--------------
Responsibility : Search the web for information, summarize content,
                 and return structured research findings.
Skills used    : WebSearchSkill, SummarizationSkill
Tools used     : SearchTool
"""

import logging

from models import ModelManager
from skills import WebSearchSkill, SummarizationSkill
from tools import SearchTool
from .base_agent import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a research assistant. Given a topic and web search results, "
    "synthesize a clear, well-structured research summary. "
    "Cite sources by title. Be objective and factual."
)


class ResearchAgent(BaseAgent):
    name = "research_agent"
    description = (
        "Handles research tasks: searching for information, summarizing articles, "
        "and generating research briefs. Triggered by keywords like 'research', "
        "'search', 'find information', 'summarize', 'what is', 'latest news'."
    )

    def __init__(self, model_manager: ModelManager):
        self.model = model_manager
        self.search_skill = WebSearchSkill()
        self.summarization_skill = SummarizationSkill(model_manager)
        self.search_tool = SearchTool()

    def handle(self, message: str, **kwargs) -> AgentResponse:  # type: ignore[override]
        logger.info("ResearchAgent handling: %r", message[:80])
        skills_used: list[str] = []
        tools_used: list[str] = ["SearchTool"]

        # 1. Search the web
        search_result = self.search_skill.run(query=message, max_results=6)
        skills_used.append("web_search")

        if not search_result.success or not search_result.output:
            return self._error_response("Web search returned no results.")

        results: list[dict] = search_result.output
        formatted_results = self.search_tool.format_results(results)

        # 2. Synthesize with the LLM
        synthesis_prompt = (
            f"User query: {message}\n\n"
            f"Web search results:\n{formatted_results}\n\n"
            "Write a comprehensive research summary based on these results. "
            "Structure it with: Overview, Key Findings (bullet points), and Sources."
        )
        response = self.model.generate(
            prompt=synthesis_prompt,
            system=SYSTEM_PROMPT,
            max_tokens=1024,
        )

        if not response.success:
            return self._error_response(response.error or "Model generation failed.")

        skills_used.append("summarization")
        return AgentResponse(
            agent_name=self.name,
            success=True,
            message=response.text,
            skills_used=skills_used,
            tools_used=tools_used,
            model_used=response.model,
            metadata={"result_count": len(results), "elapsed": response.elapsed_seconds},
        )
