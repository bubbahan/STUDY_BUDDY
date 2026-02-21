import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file, overriding any existing terminal vars
load_dotenv(override=True)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "studybuddy-jwt-secret-key-2026-secure"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///studybuddy.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = False  # Tokens don't expire during development

    # OpenRouter AI API
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "stepfun/step-3.5-flash:free")
    OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")