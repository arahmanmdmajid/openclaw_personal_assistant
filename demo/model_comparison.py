"""
Model Comparison Script
-----------------------
Runs a set of benchmark prompts through both Claude and Ollama
and prints a formatted comparison table.

Usage: python demo/model_comparison.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from models import ModelManager

console = Console()

BENCHMARKS = [
    {
        "name": "Simple QA",
        "prompt": "What is a REST API? Answer in 2 sentences.",
        "expected": "accuracy",
    },
    {
        "name": "Code Generation",
        "prompt": "Write a Python function that checks if a string is a palindrome.",
        "expected": "code quality",
    },
    {
        "name": "Summarization",
        "prompt": (
            "Summarize this in 3 bullet points:\n"
            "Machine learning is a type of artificial intelligence that allows computers "
            "to learn from data without being explicitly programmed. It uses algorithms to "
            "find patterns, make decisions, and improve over time. Common applications include "
            "image recognition, natural language processing, and recommendation systems."
        ),
        "expected": "brevity + accuracy",
    },
    {
        "name": "Task Planning",
        "prompt": "List 5 steps to deploy a Python web app to a cloud server.",
        "expected": "completeness",
    },
    {
        "name": "Complex Reasoning",
        "prompt": (
            "A developer notices that their API is slow. "
            "List 3 likely causes and 3 solutions for each."
        ),
        "expected": "depth of reasoning",
    },
]


def run_comparison() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]Hermes Assistant — Model Comparison[/bold cyan]\n"
            "Claude (Anthropic API)  vs  Ollama (local)",
            border_style="cyan",
        )
    )

    manager = ModelManager()
    results: list[dict] = []

    for bench in BENCHMARKS:
        console.print(f"\n[bold yellow]Running:[/bold yellow] {bench['name']}")

        # Claude
        manager.switch_backend("claude")
        t0 = time.perf_counter()
        c_resp = manager.generate(bench["prompt"], max_tokens=512)
        c_time = time.perf_counter() - t0

        # Ollama
        manager.switch_backend("ollama")
        t0 = time.perf_counter()
        o_resp = manager.generate(bench["prompt"], max_tokens=512)
        o_time = time.perf_counter() - t0

        results.append(
            {
                "name": bench["name"],
                "claude_ok": c_resp.success,
                "claude_time": round(c_time, 2),
                "claude_tokens": c_resp.input_tokens + c_resp.output_tokens,
                "claude_snippet": c_resp.text[:120].replace("\n", " "),
                "ollama_ok": o_resp.success,
                "ollama_time": round(o_time, 2),
                "ollama_snippet": o_resp.text[:120].replace("\n", " "),
            }
        )

    # ── Summary table ────────────────────────────────────────────
    table = Table(
        title="Model Comparison Results",
        show_lines=True,
        header_style="bold magenta",
    )
    table.add_column("Benchmark", style="bold")
    table.add_column("Claude Time")
    table.add_column("Claude Tokens")
    table.add_column("Claude OK?")
    table.add_column("Ollama Time")
    table.add_column("Ollama OK?")

    for r in results:
        table.add_row(
            r["name"],
            f"{r['claude_time']}s",
            str(r["claude_tokens"]),
            "✅" if r["claude_ok"] else "❌",
            f"{r['ollama_time']}s",
            "✅" if r["ollama_ok"] else "❌",
        )

    console.print(table)

    # ── Snippet comparison ───────────────────────────────────────
    console.rule("[bold]Response Snippets[/bold]")
    for r in results:
        console.print(f"\n[bold cyan]{r['name']}[/bold cyan]")
        console.print(f"  [green]Claude:[/green]  {r['claude_snippet']}")
        console.print(f"  [yellow]Ollama:[/yellow]  {r['ollama_snippet']}")

    console.print("\n[bold green]Comparison complete![/bold green]")


if __name__ == "__main__":
    run_comparison()
