"""Load local API configuration without overriding deployment environment variables."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_config() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
