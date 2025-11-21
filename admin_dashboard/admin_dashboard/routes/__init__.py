"""Blueprint-Registrierung für Admin-Dashboard."""
from .admin import bp as admin_bp

all_blueprints = [admin_bp]


def register_blueprints(app):
    for bp in all_blueprints:
        app.register_blueprint(bp)
