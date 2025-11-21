"""Admin dashboard Flask package.

Expose the application factory so gunicorn and Flask CLI can create
instances via ``admin_dashboard.app:create_app``.
"""
from .app import create_app

__all__ = ["create_app"]
