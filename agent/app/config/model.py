from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

DEFAULT_MODEL = "gemini-3.7-flash"
DEFAULT_FALLBACK_MODEL ="gemini-3.5-flash-lite"
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

# Load GOOGLE_API_KEY and LangSmith settings.
load_dotenv(ENV_PATH)


def create_model(model_name:str | None = None) -> ChatGoogleGenerativeAI:
    """Create the language model used by the planner."""
    selected_model = (model_name or os.getenv("GOOGLE_MODEL", DEFAULT_MODEL))
    return ChatGoogleGenerativeAI(
        model=selected_model,
        timeout=30,
        max_retries = 3
    )
def get_fallback_model_name() -> str:
    """Return configured fallback model name."""

    return os.getenv("GOOGLE_FALLBACK_MODEL",DEFAULT_FALLBACK_MODEL,)