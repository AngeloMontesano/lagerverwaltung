"""Blueprint-Registrierung."""
from flask import Blueprint

from .dashboard import bp as dashboard_bp
from .artikel import bp as artikel_bp
from .inventur import bp as inventur_bp
from .api import bp as api_bp

all_blueprints = [dashboard_bp, artikel_bp, inventur_bp, api_bp]


def register_blueprints(app):
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)
