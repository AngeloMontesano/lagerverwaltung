"""Konfigurationsmodule für tenant-spezifische Instanzen."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Basiskonfiguration für eine Mandanteninstanz."""

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    CUSTOMER_CODE: str = os.getenv("CUSTOMER_CODE", "demo")
    API_KEY: str = os.getenv("API_KEY", "demo-key")
    API_ENABLED: bool = os.getenv("API_ENABLED", "true").lower() == "true"
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"mariadb+mariadbconnector://lager:lager@db/{os.getenv('CUSTOMER_CODE', 'demo')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def from_env(cls) -> "Config":
        """Erzeuge eine Konfiguration aus Umgebungsvariablen."""
        return cls()
