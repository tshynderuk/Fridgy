"""Централізована конфігурація: єдине місце, де читаються змінні середовища."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# .../backend/fridgy/core/config.py -> .../backend
BACKEND_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    provider: str = "gemini"  # "gemini" або "mock"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    ai_timeout_s: float = 180.0


def load_settings() -> Settings:
    """Читає backend/.env та змінні середовища. Секрети не логуються."""
    load_dotenv(dotenv_path=BACKEND_DIR / ".env", override=True)
    return Settings(
        provider=os.getenv("AI_PROVIDER", "gemini").strip().lower(),
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip(),
        ai_timeout_s=float(os.getenv("AI_TIMEOUT_S", "180")),
    )
