import os
import secrets

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "studybuddy-jwt-secret-key-2026-secure"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///studybuddy.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = False  # Tokens don't expire during development