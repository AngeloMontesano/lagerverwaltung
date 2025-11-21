"""Application Factory für tenant-spezifische Lagerinstanzen."""
import logging
from logging import Formatter, StreamHandler
from flask import Flask, request
from flask_migrate import Migrate

from .config import Config
from .models import db
from .routes import register_blueprints

APP_VERSION = "0.1.0"


def _configure_logging(app: Flask):
    handler = StreamHandler()
    handler.setLevel(app.config.get("LOG_LEVEL", "INFO"))
    formatter = Formatter(
        "%(asctime)s [%(levelname)s] [tenant=%(tenant)s] %(name)s - %(message)s"
    )

    class TenantFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            record.tenant = app.config.get("CUSTOMER_CODE", "unknown")
            return True

    handler.addFilter(TenantFilter())
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))


def create_app(config_object: Config | None = None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    cfg = config_object or Config.from_env()
    cfg.APP_VERSION = getattr(cfg, "APP_VERSION", APP_VERSION)
    app.config.from_object(cfg)

    _configure_logging(app)

    db.init_app(app)
    Migrate(app, db)

    register_blueprints(app)

    @app.before_request
    def log_request():
        app.logger.debug("%s %s", request.method, request.path)

    @app.context_processor
    def inject_version():
        return {"app_version": app.config.get("APP_VERSION", APP_VERSION)}

    with app.app_context():
        db.create_all()

    return app
