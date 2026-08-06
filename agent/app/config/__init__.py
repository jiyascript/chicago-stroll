"""Application configuration."""
from app.config.environment import load_environment
from app.config.model import create_model

__all__ = ["create_model", "load_environment"]