"""Application factory for the admin dashboard package."""
from flask import Flask
from flask_migrate import Migrate

from .config import Config
from .models import db
from .routes.admin import admin_bp


def create_app(config_object: type[Config] | None = None) -> Flask:
    """Create and configure the Flask application instance.

    The factory keeps the dashboard modular, works well with testing and
    plays nicely with WSGI servers such as Gunicorn. Provide a custom
    ``Config`` subclass to override settings in tests or staging
    deployments.
    """

    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(admin_bp)

    @app.route("/health")
    def health() -> str:
        """Return a simple health probe for container orchestrators."""

        return "ok"

    return app
