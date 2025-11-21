"""Configuration for Admin Dashboard."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    DATABASE_URI: str = os.environ.get("DASHBOARD_DATABASE_URI", "sqlite:///data/dashboard.db")
    SECRET_KEY: str = os.environ.get("DASHBOARD_SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI: str = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    INSTANCE_API_TIMEOUT: int = int(os.environ.get("INSTANCE_API_TIMEOUT", "5"))


class TestConfig(Config):
    DATABASE_URI: str = "sqlite:///:memory:"
