"""
Code Agent
----------
Responsibility : Review, explain, and debug code snippets. Fetch GitHub
                 issues/commits and create development task plans.
Skills used    : CodeAnalysisSkill, TaskExtractionSkill
Tools used     : GitHubTool
"""

import logging
import re

from models import ModelManager
from skills import CodeAnalysisSkill, TaskExtractionSkill
from tools import GitHubTool
from .base_agent import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a senior software engineer. Help with code review, debugging, "
    "explanation, and developer productivity. Be precise and concise."
)

GITHUB_RE = re.compile(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", re.I)


class CodeAgent(BaseAgent):
    name = "code_agent"
    description = (
        "Handles developer tasks: code review, bug fixing, code explanation, "
        "GitHub issue tracking, and dev planning. "
        "Triggered by 'code', 'bug', 'error', 'review', 'debug', 'github', "
        "'commit', 'issue', 'pull request', '```', 'function', 'class'."
    )

    def __init__(self, model_manager: ModelManager):
        self.model = model_manager
        self.code_skill = CodeAnalysisSkill(model_manager)
        self.task_skill = TaskExtractionSkill(model_manager)
        self.github_tool = GitHubTool()

    def handle(self, message: str, **kwargs) -> AgentResponse:  # type: ignore[override]
        logger.info("CodeAgent handling: %r", message[:80])
        skills_used: list[str] = []
        tools_used: list[str] = []

        # Branch 1: GitHub repo URL detected
        gh_match = GITHUB_RE.search(message)
        if gh_match:
            return self._handle_github(message, gh_match.group(1), skills_used, tools_used)

        # Branch 2: Code snippet detected
        if "```" in message or any(kw in message.lower() for kw in ["def ", "class ", "function", "import "]):
            return self._handle_code_snippet(message, skills_used, tools_used)

        # Branch 3: General dev question
        return self._handle_general(message, skills_used, tools_used)

    def _handle_github(
        self, message: str, repo: str, skills_used: list, tools_used: list
    ) -> AgentResponse:
        tools_used.append("GitHubTool")

        repo_info = self.github_tool.get_repo_summary(repo)
        if "error" in repo_info:
            return self._error_response(f"GitHub error: {repo_info['error']}")

        issues = self.github_tool.get_open_issues(repo, limit=5)
        commits = self.github_tool.get_recent_commits(repo, limit=3)

        context = (
            f"Repository: {repo_info['name']}\n"
            f"Description: {repo_info['description']}\n"
            f"Stars: {repo_info['stars']} | Forks: {repo_info['forks']} | Language: {repo_info['language']}\n\n"
            f"Open Issues:\n{self.github_tool.format_issues(issues)}\n\n"
            f"Recent Commits:\n{self.github_tool.format_commits(commits)}"
        )

        prompt = f"User request: {message}\n\nGitHub context:\n{context}\n\nSummary and recommendations:"
        response = self.model.generate(prompt=prompt, system=SYSTEM_PROMPT, max_tokens=1024)
        skills_used.append("code_analysis")

        if not response.success:
            return self._error_response(response.error or "Model failed.")

        return AgentResponse(
            agent_name=self.name,
            success=True,
            message=f"**GitHub Report: {repo}**\n\n{response.text}",
            skills_used=skills_used,
            tools_used=tools_used,
            model_used=response.model,
        )

    def _handle_code_snippet(
        self, message: str, skills_used: list, tools_used: list
    ) -> AgentResponse:
        mode = "debug" if any(w in message.lower() for w in ["bug", "error", "fix", "broken"]) else "review"
        if "explain" in message.lower() or "what does" in message.lower():
            mode = "explain"

        result = self.code_skill.run(code=message, mode=mode)
        skills_used.append("code_analysis")

        if not result.success:
            return self._error_response(result.error or "Code analysis failed.")

        return AgentResponse(
            agent_name=self.name,
            success=True,
            message=result.output,
            skills_used=skills_used,
            tools_used=tools_used,
            model_used=result.metadata.get("model", ""),
        )

    def _handle_general(
        self, message: str, skills_used: list, tools_used: list
    ) -> AgentResponse:
        response = self.model.generate(
            prompt=message,
            system=SYSTEM_PROMPT,
            max_tokens=1024,
        )
        if not response.success:
            return self._error_response(response.error or "Model failed.")

        return AgentResponse(
            agent_name=self.name,
            success=True,
            message=response.text,
            skills_used=skills_used,
            tools_used=tools_used,
            model_used=response.model,
        )
