"""
External Tool: DuckDuckGo Web Search
--------------------------------------
Wraps DuckDuckGo search to provide real-time web results to agents.
No API key required.
"""

import logging
from typing import Optional

from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class SearchTool:
    """Thin wrapper around DuckDuckGo search."""

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        logger.info("SearchTool: %r", query)
        results = []
        try:
            with DDGS() as ddgs:
                for item in ddgs.text(query, max_results=max_results):
                    results.append(
                        {
                            "title": item.get("title", ""),
                            "url": item.get("href", ""),
                            "snippet": item.get("body", ""),
                        }
                    )
        except Exception as exc:
            logger.error("SearchTool error: %s", exc)
        return results

    def search_news(self, query: str, max_results: int = 5) -> list[dict]:
        results = []
        try:
            with DDGS() as ddgs:
                for item in ddgs.news(query, max_results=max_results):
                    results.append(
                        {
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("body", ""),
                            "date": item.get("date", ""),
                            "source": item.get("source", ""),
                        }
                    )
        except Exception as exc:
            logger.error("SearchTool.news error: %s", exc)
        return results

    def format_results(self, results: list[dict]) -> str:
        if not results:
            return "No results found."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. **{r['title']}**")
            lines.append(f"   {r['snippet']}")
            lines.append(f"   {r['url']}")
        return "\n".join(lines)
