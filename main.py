"""
Hermes Personal Assistant — Entry Point
Run:  python main.py
      python main.py --backend ollama
      python main.py --demo          (CLI demo, no Telegram token needed)
"""

import argparse
import logging
import sys

from config import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Hermes Personal Assistant")
    p.add_argument(
        "--backend",
        choices=["claude", "ollama"],
        default=config.DEFAULT_MODEL,
        help="LLM backend to use (default: %(default)s)",
    )
    p.add_argument(
        "--demo",
        action="store_true",
        help="Run CLI demo instead of Telegram bot",
    )
    return p.parse_args()


def run_telegram(backend: str) -> None:
    from orchestrator import HermesOrchestrator
    from channels import TelegramChannel

    logger.info("Starting Hermes Assistant (Telegram, backend=%s)", backend)
    orchestrator = HermesOrchestrator(model_backend=backend)
    bot = TelegramChannel(orchestrator)
    bot.run()


def run_demo(backend: str) -> None:
    from demo.demo_cli import run_demo_session
    run_demo_session(backend=backend)


if __name__ == "__main__":
    args = parse_args()
    if args.demo:
        run_demo(args.backend)
    else:
        run_telegram(args.backend)
