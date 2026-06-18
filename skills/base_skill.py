"""Base class for all Hermes Agent skills."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SkillResult:
    skill_name: str
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __str__(self) -> str:
        if not self.success:
            return f"[{self.skill_name}] ERROR: {self.error}"
        return f"[{self.skill_name}] {str(self.output)[:200]}"


class BaseSkill(ABC):
    """
    Every Hermes skill must implement:
      - name        : unique identifier
      - description : when the orchestrator should invoke this skill
      - run(input)  : execute and return a SkillResult
    """

    name: str = "base_skill"
    description: str = "Base skill — override this."
    input_schema: dict = {}
    output_schema: dict = {}

    @abstractmethod
    def run(self, **kwargs) -> SkillResult:
        ...

    def __repr__(self) -> str:
        return f"<Skill:{self.name}>"
