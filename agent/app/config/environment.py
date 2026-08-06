"""Environment configuration for Chicago Stroll."""

from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


def load_environment() -> None:
    """Load environment variables from agent/.env."""

    load_dotenv(ENV_PATH)