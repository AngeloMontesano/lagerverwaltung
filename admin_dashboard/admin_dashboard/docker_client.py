"""Stubbed Docker client for instance lifecycle operations."""
from __future__ import annotations

from datetime import datetime

from .app import db
from .models import Instance


class DockerClient:
    """Simplified client; replace with real Docker/Portainer integration later."""

    def deploy_instance(self, instance: Instance) -> None:
        instance.status = "running"
        instance.last_deploy_at = datetime.utcnow()
        db.session.commit()

    def start_instance(self, instance: Instance) -> None:
        instance.status = "running"
        db.session.commit()

    def stop_instance(self, instance: Instance) -> None:
        instance.status = "stopped"
        db.session.commit()

    def restart_instance(self, instance: Instance) -> None:
        instance.status = "running"
        db.session.commit()

    def update_instance(self, instance: Instance, new_version: str) -> None:
        instance.version = new_version
        instance.last_deploy_at = datetime.utcnow()
        db.session.commit()
