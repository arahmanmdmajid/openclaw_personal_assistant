import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_ALLOWED_USER_IDS: list[int] = [
        int(uid.strip())
        for uid in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
        if uid.strip().isdigit()
    ]
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "hermes3")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "claude")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


config = Config()
