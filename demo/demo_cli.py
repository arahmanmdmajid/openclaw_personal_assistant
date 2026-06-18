"""
CLI Demo — runs without a Telegram token.
Shows the full workflow: message → routing → agent → skills → response.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from orchestrator import HermesOrchestrator

console = Console()

DEMO_MESSAGES = [
    {
        "label": "Research Task",
        "message": "Search for the latest advancements in large language models and summarize the key findings.",
    },
    {
        "label": "Planning Task",
        "message": "I want to build a personal portfolio website. Create a detailed project plan with tasks and timeline.",
    },
    {
        "label": "Code Review Task",
        "message": (
            "Review this Python code:\n```python\n"
            "def calculate_average(numbers):\n"
            "    total = 0\n"
            "    for n in numbers:\n"
            "        total = total + n\n"
            "    return total / len(numbers)\n```"
        ),
    },
    {
        "label": "Full Workflow: Weekly Summary + Tasks",
        "message": "Summarize recent news about AI agents and create a task list of three things I should learn this week.",
    },
]


def run_demo_session(backend: str = "claude") -> None:
    console.print(
        Panel.fit(
            "[bold cyan]Hermes Personal Assistant — CLI Demo[/bold cyan]\n"
            f"Backend: [yellow]{backend}[/yellow]",
            border_style="cyan",
        )
    )

    orchestrator = HermesOrchestrator(model_backend=backend)

    for i, demo in enumerate(DEMO_MESSAGES, 1):
        console.rule(f"[bold green]Demo {i}: {demo['label']}[/bold green]")
        console.print(f"\n[bold]User message:[/bold]\n{demo['message']}\n")

        start = time.perf_counter()
        response = orchestrator.handle(demo["message"], user_id="demo_user")
        elapsed = time.perf_counter() - start

        # Show metadata
        table = Table(show_header=False, box=None)
        table.add_row("[dim]Agent[/dim]", f"[cyan]{response.agent_name}[/cyan]")
        table.add_row("[dim]Skills used[/dim]", ", ".join(response.skills_used) or "none")
        table.add_row("[dim]Tools used[/dim]", ", ".join(response.tools_used) or "none")
        table.add_row("[dim]Model[/dim]", response.model_used or backend)
        table.add_row("[dim]Wall time[/dim]", f"{elapsed:.2f}s")
        console.print(table)

        console.print("\n[bold]Assistant response:[/bold]")
        console.print(Panel(Markdown(response.message[:1500]), border_style="blue"))
        console.print()

    # Conversation log
    console.rule("[bold]Conversation Log (Observability)[/bold]")
    log = orchestrator.get_log()
    log_table = Table(
        "Time", "Agent", "Skills", "Tools", "Model", "OK?",
        show_lines=True,
        border_style="dim",
    )
    for entry in log:
        log_table.add_row(
            entry["timestamp"][11:19],
            entry["agent"],
            ", ".join(entry["skills"]) or "—",
            ", ".join(entry["tools"]) or "—",
            entry["model"][-20:] if entry["model"] else "—",
            "✅" if entry["success"] else "❌",
        )
    console.print(log_table)
    console.print("\n[bold green]Demo complete![/bold green]")


if __name__ == "__main__":
    backend = sys.argv[1] if len(sys.argv) > 1 else "claude"
    run_demo_session(backend=backend)
