"""
Planning Agent
--------------
Responsibility : Break down goals into actionable task plans, create weekly
                 schedules, and generate project roadmaps.
Skills used    : TaskExtractionSkill, SummarizationSkill
"""

import logging
from datetime import date

from models import ModelManager
from skills import TaskExtractionSkill, SummarizationSkill
from .base_agent import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a productivity and project planning expert. "
    "Create clear, structured, and achievable plans. "
    "Use numbered lists, time estimates where helpful, and prioritize tasks. "
    f"Today's date is {date.today().isoformat()}."
)


class PlanningAgent(BaseAgent):
    name = "planning_agent"
    description = (
        "Handles planning and productivity tasks: creating task lists, "
        "weekly plans, project roadmaps, and goal breakdowns. "
        "Triggered by 'plan', 'schedule', 'task list', 'roadmap', 'organize', "
        "'what should I do', 'next steps', 'priority'."
    )

    def __init__(self, model_manager: ModelManager):
        self.model = model_manager
        self.task_skill = TaskExtractionSkill(model_manager)
        self.summary_skill = SummarizationSkill(model_manager)

    def handle(self, message: str, **kwargs) -> AgentResponse:  # type: ignore[override]
        logger.info("PlanningAgent handling: %r", message[:80])
        skills_used: list[str] = []

        prompt = (
            f"User request: {message}\n\n"
            "Create a detailed, actionable plan to address this request. "
            "Include:\n"
            "1. Goal / Objective\n"
            "2. Prioritized task list (numbered, with action verbs)\n"
            "3. Suggested timeline or milestones\n"
            "4. Tips or resources if relevant\n\n"
            "Plan:"
        )

        response = self.model.generate(prompt=prompt, system=SYSTEM_PROMPT, max_tokens=1024)
        skills_used.append("task_extraction")

        if not response.success:
            return self._error_response(response.error or "Planning generation failed.")

        return AgentResponse(
            agent_name=self.name,
            success=True,
            message=response.text,
            skills_used=skills_used,
            tools_used=[],
            model_used=response.model,
            metadata={"elapsed": response.elapsed_seconds},
        )
