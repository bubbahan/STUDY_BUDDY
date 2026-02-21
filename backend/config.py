import os
import secrets

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "studybuddy-jwt-secret-key-2026-secure"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///studybuddy.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = False  # Tokens don't expire during development

    # OpenRouter AI API
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") or "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"
    OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL") or "stepfun/step-3.5-flash:free"
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"