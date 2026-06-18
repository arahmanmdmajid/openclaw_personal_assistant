"""
Multi-model backend for the Hermes Personal Assistant.

Supports:
  - Claude (Anthropic API)
  - Ollama (local models: hermes3, mistral, llama3, …)
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Optional

import anthropic
import requests

from config import config

logger = logging.getLogger(__name__)


@dataclass
class ModelResponse:
    text: str
    model: str
    elapsed_seconds: float
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.error is None


class ModelManager:
    """Routes inference to Claude or a local Ollama model."""

    SUPPORTED_BACKENDS = ("claude", "ollama")

    def __init__(self, backend: Optional[str] = None):
        self.backend = backend or config.DEFAULT_MODEL
        if self.backend not in self.SUPPORTED_BACKENDS:
            raise ValueError(f"Backend must be one of {self.SUPPORTED_BACKENDS}")
        self._claude_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # ── Public ──────────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> ModelResponse:
        if self.backend == "claude":
            return self._claude_generate(prompt, system, max_tokens, temperature)
        return self._ollama_generate(prompt, system, max_tokens, temperature)

    def switch_backend(self, backend: str) -> None:
        if backend not in self.SUPPORTED_BACKENDS:
            raise ValueError(f"Backend must be one of {self.SUPPORTED_BACKENDS}")
        self.backend = backend
        logger.info("Switched model backend to: %s", backend)

    # ── Claude ──────────────────────────────────────────────────

    def _claude_generate(
        self, prompt: str, system: str, max_tokens: int, temperature: float
    ) -> ModelResponse:
        start = time.perf_counter()
        try:
            messages_payload = [{"role": "user", "content": prompt}]
            kwargs = dict(
                model=config.CLAUDE_MODEL,
                max_tokens=max_tokens,
                messages=messages_payload,
            )
            if system:
                kwargs["system"] = system

            response = self._claude_client.messages.create(**kwargs)
            elapsed = time.perf_counter() - start
            text = response.content[0].text
            return ModelResponse(
                text=text,
                model=config.CLAUDE_MODEL,
                elapsed_seconds=round(elapsed, 2),
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            )
        except Exception as exc:
            elapsed = time.perf_counter() - start
            logger.error("Claude generation error: %s", exc)
            return ModelResponse(
                text="",
                model=config.CLAUDE_MODEL,
                elapsed_seconds=round(elapsed, 2),
                error=str(exc),
            )

    # ── Ollama ──────────────────────────────────────────────────

    def _ollama_generate(
        self, prompt: str, system: str, max_tokens: int, temperature: float
    ) -> ModelResponse:
        start = time.perf_counter()
        model_name = config.OLLAMA_MODEL
        try:
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            payload = {
                "model": model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }
            resp = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            elapsed = time.perf_counter() - start
            return ModelResponse(
                text=data.get("response", ""),
                model=model_name,
                elapsed_seconds=round(elapsed, 2),
                metadata={"eval_count": data.get("eval_count", 0)},
            )
        except Exception as exc:
            elapsed = time.perf_counter() - start
            logger.error("Ollama generation error: %s", exc)
            return ModelResponse(
                text="",
                model=model_name,
                elapsed_seconds=round(elapsed, 2),
                error=str(exc),
            )

    # ── Benchmark helper ────────────────────────────────────────

    def benchmark(self, prompt: str, system: str = "") -> dict:
        """Run the same prompt on both backends and return comparison data."""
        original = self.backend

        self.switch_backend("claude")
        claude_resp = self.generate(prompt, system)

        self.switch_backend("ollama")
        ollama_resp = self.generate(prompt, system)

        self.switch_backend(original)

        return {
            "claude": {
                "model": claude_resp.model,
                "success": claude_resp.success,
                "elapsed": claude_resp.elapsed_seconds,
                "tokens": claude_resp.input_tokens + claude_resp.output_tokens,
                "response": claude_resp.text[:300],
                "error": claude_resp.error,
            },
            "ollama": {
                "model": ollama_resp.model,
                "success": ollama_resp.success,
                "elapsed": ollama_resp.elapsed_seconds,
                "response": ollama_resp.text[:300],
                "error": ollama_resp.error,
            },
        }
