"""
Communication Channel: Telegram
---------------------------------
Connects the Hermes Orchestrator to a Telegram bot.
Users send messages → bot routes to agents → response sent back.

Commands:
  /start        – Welcome message
  /help         – Usage instructions
  /model claude – Switch to Claude backend
  /model ollama – Switch to Ollama backend
  /log          – Show last 5 conversation entries
  /benchmark    – Compare Claude vs Ollama on a test prompt
"""

import logging
import html

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import config
from orchestrator import HermesOrchestrator

logger = logging.getLogger(__name__)

WELCOME = (
    "👋 *Hermes Personal Assistant* is online!\n\n"
    "I can help you with:\n"
    "🔍 *Research* — search & summarize information\n"
    "📋 *Planning* — create task lists & project plans\n"
    "💻 *Code* — review, debug, or analyze code\n\n"
    "Just send me a message to get started.\n"
    "Type /help for available commands."
)

HELP_TEXT = (
    "*Available Commands:*\n"
    "/start — Welcome message\n"
    "/help — This help text\n"
    "/model claude — Use Claude (Anthropic API)\n"
    "/model ollama — Use Ollama (local model)\n"
    "/log — Recent conversation log\n"
    "/benchmark — Compare both models\n\n"
    "*Tip:* Paste code in ``` blocks for automatic code review."
)


class TelegramChannel:
    """Telegram bot interface for the Hermes assistant."""

    def __init__(self, orchestrator: HermesOrchestrator):
        self.orchestrator = orchestrator

    def _is_allowed(self, user_id: int) -> bool:
        if not config.TELEGRAM_ALLOWED_USER_IDS:
            return True
        return user_id in config.TELEGRAM_ALLOWED_USER_IDS

    async def _check_access(self, update: Update) -> bool:
        if not self._is_allowed(update.effective_user.id):
            await update.message.reply_text("Sorry, you are not authorized to use this bot.")
            return False
        return True

    # ── Command handlers ─────────────────────────────────────────

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._check_access(update):
            return
        await update.message.reply_text(WELCOME, parse_mode="Markdown")

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._check_access(update):
            return
        await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")

    async def cmd_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._check_access(update):
            return
        args = context.args
        if not args or args[0] not in ("claude", "ollama"):
            await update.message.reply_text("Usage: /model claude  or  /model ollama")
            return
        self.orchestrator.switch_model(args[0])
        await update.message.reply_text(f"✅ Switched to *{args[0]}* backend.", parse_mode="Markdown")

    async def cmd_log(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._check_access(update):
            return
        entries = self.orchestrator.get_log()[-5:]
        if not entries:
            await update.message.reply_text("No conversation history yet.")
            return
        lines = ["*Recent activity:*"]
        for e in entries:
            lines.append(
                f"• `{e['timestamp'][11:19]}` → {e['agent']} | "
                f"skills: {', '.join(e['skills']) or 'none'} | "
                f"model: {e['model']}"
            )
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    async def cmd_benchmark(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._check_access(update):
            return
        await update.message.reply_text("⏳ Running benchmark on both models, please wait…")
        test_prompt = "Explain what a REST API is in 3 bullet points."
        results = self.orchestrator.benchmark(test_prompt)

        c = results["claude"]
        o = results["ollama"]
        text = (
            f"*Benchmark: \"{test_prompt}\"*\n\n"
            f"*Claude ({c['model']})*\n"
            f"  Status: {'✅' if c['success'] else '❌'}\n"
            f"  Time: {c['elapsed']}s | Tokens: {c['tokens']}\n"
            f"  Response: _{html.escape(c['response'][:200])}_\n\n"
            f"*Ollama ({o['model']})*\n"
            f"  Status: {'✅' if o['success'] else '❌'}\n"
            f"  Time: {o['elapsed']}s\n"
            f"  Response: _{html.escape(o['response'][:200])}_"
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    # ── Message handler ──────────────────────────────────────────

    async def on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._check_access(update):
            return

        user_message = update.message.text
        user_id = str(update.effective_user.id)

        await update.message.chat.send_action("typing")

        response = self.orchestrator.handle(user_message, user_id=user_id)

        header = f"*[{response.agent_name.replace('_', ' ').title()}]*\n"
        footer = (
            f"\n\n_Skills: {', '.join(response.skills_used) or 'none'} | "
            f"Tools: {', '.join(response.tools_used) or 'none'} | "
            f"Model: {response.model_used}_"
        )

        full_text = header + response.message + footer

        # Telegram message limit is 4096 chars
        for chunk in self._split(full_text, 4000):
            await update.message.reply_text(chunk, parse_mode="Markdown")

    @staticmethod
    def _split(text: str, size: int) -> list[str]:
        return [text[i : i + size] for i in range(0, len(text), size)]

    # ── Run ──────────────────────────────────────────────────────

    def run(self) -> None:
        if not config.TELEGRAM_BOT_TOKEN:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in .env")

        app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("help", self.cmd_help))
        app.add_handler(CommandHandler("model", self.cmd_model))
        app.add_handler(CommandHandler("log", self.cmd_log))
        app.add_handler(CommandHandler("benchmark", self.cmd_benchmark))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_message))

        logger.info("Telegram bot starting (polling)…")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
