"""
Skill: Text Summarization
--------------------------
What it does : Summarizes long text into bullet-point key findings.
When to use  : When the user provides a URL, pasted article, or paper abstract to digest.
Input        : text (str), max_bullets (int, default 5)
Output       : Bulleted summary string
"""

import logging

from models import ModelManager
from .base_skill import BaseSkill, SkillResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert summarizer. Extract the most important points from the text "
    "and present them as concise bullet points. Be factual and accurate."
)


class SummarizationSkill(BaseSkill):
    name = "summarization"
    description = (
        "Summarize long text, articles, papers, or documents into key bullet points. "
        "Use when the user asks to summarize, digest, or explain content."
    )
    input_schema = {"text": "str", "max_bullets": "int (default 5)"}
    output_schema = {"summary": "str (bulleted list)"}

    def __init__(self, model_manager: ModelManager):
        self.model = model_manager

    def run(self, text: str, max_bullets: int = 5) -> SkillResult:  # type: ignore[override]
        logger.info("SummarizationSkill: text length=%d", len(text))
        prompt = (
            f"Summarize the following text into exactly {max_bullets} key bullet points.\n\n"
            f"Text:\n{text[:6000]}\n\nBullet-point summary:"
        )
        response = self.model.generate(prompt=prompt, system=SYSTEM_PROMPT, max_tokens=512)
        if response.success:
            return SkillResult(
                skill_name=self.name,
                success=True,
                output=response.text,
                metadata={"model": response.model, "elapsed": response.elapsed_seconds},
            )
        return SkillResult(
            skill_name=self.name, success=False, output="", error=response.error
        )
