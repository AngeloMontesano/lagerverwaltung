"""Admin Dashboard application factory."""
from __future__ import annotations

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import Config


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_object: type[Config] | None = None) -> Flask:
    config_object = config_object or Config
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    # Ensure models are registered before blueprints are loaded
    from . import models  # noqa: F401

    from .routes import admin

    app.register_blueprint(admin.bp)

    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "version": "0.1.0",
        }

    return app
