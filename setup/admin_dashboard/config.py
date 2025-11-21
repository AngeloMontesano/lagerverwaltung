"""Configuration for the admin dashboard."""
import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DASHBOARD_DATABASE_URI", "sqlite:///data/dashboard.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("DASHBOARD_SECRET_KEY", "dev-secret-key")
    # Placeholder for later Docker/Portainer/Kubernetes endpoints
    DOCKER_ENDPOINT = os.getenv("DOCKER_ENDPOINT", "unix:///var/run/docker.sock")
