"""Database setup for the warehouse application."""
from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def init_extensions(app):
    """Initialize extensions for the given app."""
    db.init_app(app)
    migrate.init_app(app, db)
