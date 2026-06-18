"""
Skill: Web Search
-----------------
What it does : Searches the web using DuckDuckGo and returns top results.
When to use  : When the user asks about current events, topics, or unknown facts.
Input        : query (str), max_results (int, default 5)
Output       : List of {title, url, snippet} dicts
"""

import logging
from typing import Optional

from duckduckgo_search import DDGS

from .base_skill import BaseSkill, SkillResult

logger = logging.getLogger(__name__)


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = (
        "Search the web for current information, news, or factual data. "
        "Use when the user mentions 'search', 'find', 'look up', or needs recent info."
    )
    input_schema = {"query": "str", "max_results": "int (default 5)"}
    output_schema = {"results": "list[{title, url, snippet}]"}

    def run(self, query: str, max_results: int = 5) -> SkillResult:  # type: ignore[override]
        logger.info("WebSearchSkill: query=%r max=%d", query, max_results)
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(
                        {
                            "title": r.get("title", ""),
                            "url": r.get("href", ""),
                            "snippet": r.get("body", ""),
                        }
                    )
            return SkillResult(
                skill_name=self.name,
                success=True,
                output=results,
                metadata={"query": query, "result_count": len(results)},
            )
        except Exception as exc:
            logger.error("WebSearchSkill error: %s", exc)
            return SkillResult(
                skill_name=self.name, success=False, output=[], error=str(exc)
            )
