"""Application Factory für das Admin-Dashboard."""
from flask import Flask
from flask_migrate import Migrate

from .config import Config
from .models import db
from .routes import register_blueprints


def create_app(config_object: Config | None = None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    cfg = config_object or Config()
    app.config.from_object(cfg)

    db.init_app(app)
    Migrate(app, db)
    register_blueprints(app)

    with app.app_context():
        db.create_all()

    return app
