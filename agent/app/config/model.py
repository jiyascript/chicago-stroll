import os
from app.config.environment import load_environment

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_FALLBACK_MODEL = "gemini-2.5-flash-lite"

def create_model(model_name: str | None = None):
    load_environment()
    from langchain_google_genai import ChatGoogleGenerativeAI
    selected = model_name or os.getenv("GOOGLE_MODEL", DEFAULT_MODEL)
    return ChatGoogleGenerativeAI(model=selected, temperature=0)

def get_fallback_model_name() -> str:
    return os.getenv("GOOGLE_FALLBACK_MODEL", DEFAULT_FALLBACK_MODEL)
