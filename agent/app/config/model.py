from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI



ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

# Load GOOGLE_API_KEY and LangSmith settings.
load_dotenv(ENV_PATH)


def create_model() -> ChatGoogleGenerativeAI:
    """Create the language model used by the planner."""

    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
    )