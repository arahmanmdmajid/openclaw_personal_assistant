"""
Mock Demo — runs without any API keys.
Shows the full architecture and routing logic using canned responses.
Run: python demo/demo_mock.py
"""

import sys
import os
import time
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()

MOCK_RESPONSES = {
    "research": """\
## AI Agent Advancements — Research Brief

**Overview**
Recent months have seen rapid progress in autonomous AI agent systems, with major labs
releasing frameworks for multi-step task completion.

**Key Findings**
- Multi-agent architectures now outperform single-agent setups on complex benchmarks
- Tool use accuracy has improved from ~60% to ~90% with structured prompting
- OpenAI, Anthropic, and Google all released agent SDKs in 2024–2025
- Local models (Hermes-3, Llama-3) are approaching API-model quality on reasoning tasks

**Sources**
1. "LLM Agents: A Survey" — arXiv 2024
2. Anthropic Blog — Claude's tool use improvements
3. HuggingFace Blog — Open-source agent benchmarks
""",
    "planning": """\
## Portfolio Website — Project Plan

**Objective:** Build and deploy a personal developer portfolio within 4 weeks.

**Prioritized Task List:**
1. Define content: bio, projects, skills, contact info
2. Choose tech stack (React + Tailwind recommended)
3. Design wireframes (Figma or pen/paper)
4. Build homepage and about section
5. Add projects section with GitHub links
6. Integrate contact form (EmailJS or Formspree)
7. Optimize for mobile and SEO
8. Deploy to Vercel or Netlify

**Timeline:**
- Week 1: Design + content
- Week 2: Core pages built
- Week 3: Polish + integrations
- Week 4: Testing + deploy

**Resources:**
- vitejs.dev (fast build tool)
- tailwindcss.com (styling)
- vercel.com (free deployment)
""",
    "code": """\
## Code Review — `calculate_average`

**Issues Found:**

🔴 **Bug (Critical):** Division by zero when `numbers` is empty — raises `ZeroDivisionError`.

🟡 **Performance:** Manual summation loop is redundant; Python's built-in `sum()` is faster.

🟢 **Readability:** Acceptable, but type hints would help.

**Corrected version:**
```python
def calculate_average(numbers: list[float]) -> float:
    if not numbers:
        raise ValueError("Cannot average an empty list")
    return sum(numbers) / len(numbers)
```

**Recommendations:**
- Add a unit test with an empty list
- Consider returning `None` or `0.0` instead of raising, depending on use case
""",
}


def simulate_workflow():
    console.print(
        Panel.fit(
            "[bold cyan]Hermes Personal Assistant[/bold cyan]\n"
            "[dim]Mock Demo — No API keys required[/dim]",
            border_style="cyan",
        )
    )

    demos = [
        {
            "label": "Research Task",
            "message": "Search for the latest advancements in AI agents and summarize key findings.",
            "agent": "research_agent",
            "skills": ["web_search", "summarization"],
            "tools": ["SearchTool (DuckDuckGo)"],
            "model": "claude-sonnet-4-6",
            "response_key": "research",
            "elapsed": 2.8,
        },
        {
            "label": "Planning Task",
            "message": "I want to build a personal portfolio website. Create a project plan with tasks and timeline.",
            "agent": "planning_agent",
            "skills": ["task_extraction"],
            "tools": [],
            "model": "claude-sonnet-4-6",
            "response_key": "planning",
            "elapsed": 1.9,
        },
        {
            "label": "Code Review Task",
            "message": "Review this Python code:\n```python\ndef calculate_average(numbers):\n    total = 0\n    for n in numbers:\n        total = total + n\n    return total / len(numbers)\n```",
            "agent": "code_agent",
            "skills": ["code_analysis"],
            "tools": [],
            "model": "claude-sonnet-4-6",
            "response_key": "code",
            "elapsed": 2.2,
        },
    ]

    log_rows = []

    for i, demo in enumerate(demos, 1):
        console.rule(f"[bold green]Demo {i}: {demo['label']}[/bold green]")
        console.print(f"\n[bold]User → Telegram:[/bold]\n[italic]{demo['message'][:120]}[/italic]\n")

        # Simulate processing delay
        with console.status(f"[yellow]Orchestrator routing → {demo['agent']}…[/yellow]"):
            time.sleep(0.5)

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_row("[dim]Agent[/dim]", f"[cyan]{demo['agent']}[/cyan]")
        table.add_row("[dim]Skills[/dim]", ", ".join(demo["skills"]))
        table.add_row("[dim]Tools[/dim]", ", ".join(demo["tools"]) if demo["tools"] else "—")
        table.add_row("[dim]Model[/dim]", demo["model"])
        table.add_row("[dim]Elapsed[/dim]", f"{demo['elapsed']}s")
        console.print(table)

        console.print("\n[bold]Assistant → Telegram:[/bold]")
        console.print(Panel(Markdown(MOCK_RESPONSES[demo["response_key"]]), border_style="blue"))

        log_rows.append(
            (
                f"12:{15 + i:02d}:00",
                demo["agent"],
                ", ".join(demo["skills"]),
                ", ".join(demo["tools"]) if demo["tools"] else "—",
                demo["model"][-16:],
                "✅",
            )
        )
        console.print()

    # ── Conversation log ────────────────────────────────────────
    console.rule("[bold]Observability Log[/bold]")
    log_table = Table(
        "Time", "Agent", "Skills", "Tools", "Model", "OK?",
        show_lines=True, border_style="dim",
    )
    for row in log_rows:
        log_table.add_row(*row)
    console.print(log_table)

    # ── Model comparison summary ─────────────────────────────────
    console.rule("[bold]Model Comparison Summary[/bold]")
    cmp_table = Table(
        "Model", "Setup", "Speed", "Quality", "Tool Use", "Cost", "Notes",
        show_lines=True, header_style="bold magenta",
    )
    cmp_table.add_row(
        "Claude Sonnet 4.6", "API", "Fast (2–4s)", "Excellent", "Excellent",
        "$3/M tokens", "Best for structured tasks, code review",
    )
    cmp_table.add_row(
        "Ollama Hermes-3", "Local", "Medium (5–15s)", "Good", "Good",
        "Free", "No API costs; weaker on multi-step tool use",
    )
    console.print(cmp_table)

    console.print("\n[bold green]✅ Demo complete! See README.md for full setup instructions.[/bold green]")


if __name__ == "__main__":
    simulate_workflow()
