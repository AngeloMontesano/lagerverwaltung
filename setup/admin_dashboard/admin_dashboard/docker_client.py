"""Stub for container lifecycle management.

This module prepares integration with Docker/Portainer/Kubernetes. It currently
only updates dashboard metadata and should be replaced with real API calls.
"""
from __future__ import annotations

from datetime import datetime

from .models import Instance, db


class DockerClient:
    """Lifecycle actions for tenant instances.

    Replace the placeholder comments with real API calls to your container
    orchestrator. Keep the interface stable so the web layer does not change
    when the backend implementation evolves.
    """

    def start_instance(self, instance: Instance) -> None:
        """Mark the instance as running and persist the change."""

        # TODO: call Docker/Portainer/Kubernetes API to start the stack/container.
        instance.status = "running"
        instance.last_deploy_at = datetime.utcnow()
        db.session.commit()

    def stop_instance(self, instance: Instance) -> None:
        """Mark the instance as stopped and persist the change."""

        # TODO: call orchestrator API to stop the stack/container.
        instance.status = "stopped"
        instance.last_deploy_at = datetime.utcnow()
        db.session.commit()

    def restart_instance(self, instance: Instance) -> None:
        """Mark the instance as restarted and persist the change."""

        # TODO: call orchestrator API to restart the stack/container.
        instance.status = "running"
        instance.last_deploy_at = datetime.utcnow()
        db.session.commit()

    def update_instance(self, instance: Instance, new_version: str) -> None:
        """Persist a version update and mark the instance as updating."""

        # TODO: pull new image version and redeploy via orchestrator API.
        instance.version = new_version
        instance.status = "updating"
        instance.last_deploy_at = datetime.utcnow()
        db.session.commit()
