"""
Skill: Code Analysis
---------------------
What it does : Reviews code snippets for bugs, improvements, and best practices.
When to use  : When the user shares code and asks for review, debugging, or explanation.
Input        : code (str), language (str, default "python"), mode (review|explain|debug)
Output       : Structured code review as a string
"""

import logging

from models import ModelManager
from .base_skill import BaseSkill, SkillResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a senior software engineer performing a code review. "
    "Provide structured feedback covering: bugs, security issues, performance, "
    "readability, and improvement suggestions. Be concise and actionable."
)

EXPLAIN_SYSTEM = (
    "You are an expert programmer and technical teacher. "
    "Explain the provided code clearly, covering what it does, how it works, "
    "and any noteworthy patterns or concerns."
)

DEBUG_SYSTEM = (
    "You are an expert debugger. Identify the root cause of the bug described, "
    "explain why it happens, and provide a corrected version of the code."
)


class CodeAnalysisSkill(BaseSkill):
    name = "code_analysis"
    description = (
        "Analyze, review, explain, or debug code. "
        "Use when the user shares a code snippet and mentions review, bug, error, or explanation."
    )
    input_schema = {
        "code": "str",
        "language": "str (default 'python')",
        "mode": "str: review | explain | debug (default 'review')",
        "context": "str (optional: error message or description)",
    }
    output_schema = {"analysis": "str (structured code feedback)"}

    def __init__(self, model_manager: ModelManager):
        self.model = model_manager

    def run(  # type: ignore[override]
        self,
        code: str,
        language: str = "python",
        mode: str = "review",
        context: str = "",
    ) -> SkillResult:
        logger.info("CodeAnalysisSkill: mode=%s lang=%s", mode, language)

        system = {
            "review": SYSTEM_PROMPT,
            "explain": EXPLAIN_SYSTEM,
            "debug": DEBUG_SYSTEM,
        }.get(mode, SYSTEM_PROMPT)

        context_block = f"\nAdditional context: {context}" if context else ""
        prompt = (
            f"Language: {language}\n"
            f"Mode: {mode}\n"
            f"{context_block}\n\n"
            f"Code:\n```{language}\n{code}\n```\n\n"
            f"{'Review' if mode == 'review' else 'Explanation' if mode == 'explain' else 'Debug analysis'}:"
        )

        response = self.model.generate(prompt=prompt, system=system, max_tokens=1024)
        if response.success:
            return SkillResult(
                skill_name=self.name,
                success=True,
                output=response.text,
                metadata={"model": response.model, "mode": mode, "language": language},
            )
        return SkillResult(
            skill_name=self.name, success=False, output="", error=response.error
        )
