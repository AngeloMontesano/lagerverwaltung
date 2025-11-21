"""Konfiguration für das Admin-Dashboard."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "admin-secret")
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "ADMIN_DATABASE_URL", f"sqlite:///{os.path.abspath('data/admin.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    PORTAINER_URL: str | None = os.getenv("PORTAINER_URL")
    PORTAINER_TOKEN: str | None = os.getenv("PORTAINER_TOKEN")
    TENANT_TEMPLATE_PATH: str = os.getenv("TENANT_TEMPLATE_PATH", "../lagersoftware")
    DEFAULT_API_KEY: str = os.getenv("DEFAULT_API_KEY", "demo-key")
