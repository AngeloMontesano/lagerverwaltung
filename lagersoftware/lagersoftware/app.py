"""Application factory for the warehouse app."""
from __future__ import annotations

import logging
from logging.config import dictConfig

from flask import Flask

from .config import Config
from .database import init_extensions
from .routes import register_blueprints


def configure_logging(app: Flask) -> None:
    tenant = app.config.get("TENANT_ID", "UNKNOWN")
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": f"%(asctime)s [tenant={tenant}] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console"],
            },
        }
    )



def create_app(config_object: type[Config] | None = None) -> Flask:
    """Create and configure the Flask app."""
    config_object = config_object or Config
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    configure_logging(app)
    init_extensions(app)
    from . import models  # noqa: F401
    register_blueprints(app)

    @app.route("/health")
    def health_check():
        return {
            "status": "ok",
            "version": app.config.get("APP_VERSION"),
            "tenant": app.config.get("TENANT_ID"),
        }

    return app
