"""Configuration for the warehouse application."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Base configuration loaded from environment variables."""

    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///lagersoftware.db")
    TENANT_ID: str = os.environ.get("TENANT_ID", "DEV-TENANT")
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "dev")
    API_AUTH_TOKEN: str = os.environ.get("API_AUTH_TOKEN", "changeme-token")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", os.urandom(16).hex())
    APP_VERSION: str = os.environ.get("APP_VERSION", "0.1.0")

    SQLALCHEMY_DATABASE_URI: str = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        """Create a config instance from current environment variables."""
        return cls()


class TestConfig(Config):
    ENVIRONMENT: str = "test"
    DATABASE_URL: str = "sqlite:///:memory:"
