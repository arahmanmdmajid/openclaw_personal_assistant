"""
External Tool: GitHub API
--------------------------
Fetches repository info, open issues, and recent commits via PyGithub.
Requires GITHUB_TOKEN environment variable.
"""

import logging
from typing import Optional

from github import Github, GithubException

from config import config

logger = logging.getLogger(__name__)


class GitHubTool:
    """Wraps the GitHub API for repo/issue/commit operations."""

    def __init__(self):
        token = config.GITHUB_TOKEN
        self._gh = Github(token) if token else Github()
        self._authenticated = bool(token)

    # ── Repository info ─────────────────────────────────────────

    def get_repo_summary(self, repo_full_name: str) -> dict:
        """Return basic info about a repository."""
        try:
            repo = self._gh.get_repo(repo_full_name)
            return {
                "name": repo.full_name,
                "description": repo.description or "",
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "open_issues": repo.open_issues_count,
                "language": repo.language or "unknown",
                "url": repo.html_url,
                "last_updated": repo.updated_at.isoformat() if repo.updated_at else "",
            }
        except GithubException as exc:
            logger.error("GitHubTool.get_repo_summary error: %s", exc)
            return {"error": str(exc)}

    # ── Issues ──────────────────────────────────────────────────

    def get_open_issues(self, repo_full_name: str, limit: int = 10) -> list[dict]:
        """Return the most recent open issues."""
        try:
            repo = self._gh.get_repo(repo_full_name)
            issues = []
            for issue in repo.get_issues(state="open")[:limit]:
                issues.append(
                    {
                        "number": issue.number,
                        "title": issue.title,
                        "labels": [lb.name for lb in issue.labels],
                        "comments": issue.comments,
                        "url": issue.html_url,
                        "created_at": issue.created_at.isoformat(),
                    }
                )
            return issues
        except GithubException as exc:
            logger.error("GitHubTool.get_open_issues error: %s", exc)
            return [{"error": str(exc)}]

    # ── Commits ─────────────────────────────────────────────────

    def get_recent_commits(self, repo_full_name: str, limit: int = 5) -> list[dict]:
        """Return the most recent commits on the default branch."""
        try:
            repo = self._gh.get_repo(repo_full_name)
            commits = []
            for commit in repo.get_commits()[:limit]:
                commits.append(
                    {
                        "sha": commit.sha[:7],
                        "message": commit.commit.message.split("\n")[0],
                        "author": commit.commit.author.name,
                        "date": commit.commit.author.date.isoformat(),
                        "url": commit.html_url,
                    }
                )
            return commits
        except GithubException as exc:
            logger.error("GitHubTool.get_recent_commits error: %s", exc)
            return [{"error": str(exc)}]

    # ── Formatting ──────────────────────────────────────────────

    def format_issues(self, issues: list[dict]) -> str:
        if not issues:
            return "No open issues."
        lines = []
        for issue in issues:
            if "error" in issue:
                return f"Error: {issue['error']}"
            labels = ", ".join(issue["labels"]) if issue["labels"] else "no labels"
            lines.append(f"#{issue['number']}: {issue['title']} [{labels}]")
        return "\n".join(lines)

    def format_commits(self, commits: list[dict]) -> str:
        if not commits:
            return "No commits found."
        lines = []
        for c in commits:
            if "error" in c:
                return f"Error: {c['error']}"
            lines.append(f"{c['sha']} — {c['message']} ({c['author']}, {c['date'][:10]})")
        return "\n".join(lines)
