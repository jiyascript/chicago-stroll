from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

DEFAULT_MODEL = "gemini-3.7-flash"

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

# Load GOOGLE_API_KEY and LangSmith settings.
load_dotenv(ENV_PATH)


def create_model() -> ChatGoogleGenerativeAI:
    """Create the language model used by the planner."""

    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        timeout=30,
        max_retries = 3
    )