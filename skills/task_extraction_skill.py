"""
Skill: Task Extraction
-----------------------
What it does : Parses a block of text and extracts actionable to-do items.
When to use  : When the user asks for a task list, action items, or next steps from text.
Input        : text (str), max_tasks (int, default 10)
Output       : Numbered list of tasks as a string
"""

import logging

from models import ModelManager
from .base_skill import BaseSkill, SkillResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a productivity expert. Read the provided text and extract clear, "
    "actionable tasks. Each task should start with a strong action verb. "
    "Number each task. If no tasks can be extracted, say 'No actionable tasks found.'"
)


class TaskExtractionSkill(BaseSkill):
    name = "task_extraction"
    description = (
        "Extract actionable tasks or to-do items from text. "
        "Use when the user wants a task list, action items, or next steps."
    )
    input_schema = {"text": "str", "max_tasks": "int (default 10)"}
    output_schema = {"tasks": "str (numbered list)"}

    def __init__(self, model_manager: ModelManager):
        self.model = model_manager

    def run(self, text: str, max_tasks: int = 10) -> SkillResult:  # type: ignore[override]
        logger.info("TaskExtractionSkill: text length=%d", len(text))
        prompt = (
            f"Extract up to {max_tasks} actionable tasks from the text below. "
            "Each task must start with an action verb (e.g., Read, Write, Review, Schedule).\n\n"
            f"Text:\n{text[:5000]}\n\nNumbered task list:"
        )
        response = self.model.generate(prompt=prompt, system=SYSTEM_PROMPT, max_tokens=512)
        if response.success:
            return SkillResult(
                skill_name=self.name,
                success=True,
                output=response.text,
                metadata={"model": response.model},
            )
        return SkillResult(
            skill_name=self.name, success=False, output="", error=response.error
        )
