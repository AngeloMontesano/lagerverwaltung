"""Application factory for the admin dashboard."""
from flask import Flask
from flask_migrate import Migrate

from .config import Config
from .models import db
from .routes.admin import admin_bp


def create_app(config_object: type[Config] | None = None) -> Flask:
    """Create and configure the Flask application.

    The factory keeps the dashboard modular and makes testing easier.
    """
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(admin_bp)

    @app.route("/health")
    def health() -> str:
        return "ok"

    return app
