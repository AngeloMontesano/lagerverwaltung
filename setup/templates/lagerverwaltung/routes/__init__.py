# =============================================
# 🔹 Initialisierung der Flask-Blueprints
# =============================================

from flask import Blueprint

# 🔹 Importiere alle Routen-Blueprints
from .artikel import bp as artikel_bp
from .bestellungen import bp as bestellungen_bp
from .inventur import bp as inventur_bp
from .bestandsverwaltung import bp as bestandsverwaltung_bp
from .dashboard import bp as dashboard_bp
from .berichte import bp as berichte_bp
from .einstellungen import bp as einstellungen_bp
from .flash import bp as flash_bp


# 🔹 Haupt-Blueprint für die API
bp = Blueprint("api", __name__)

# =============================================
# 🔹 Registrierung aller Routen-Blueprints
# =============================================
bp.register_blueprint(artikel_bp)
bp.register_blueprint(bestellungen_bp)
bp.register_blueprint(inventur_bp)
bp.register_blueprint(bestandsverwaltung_bp)
bp.register_blueprint(dashboard_bp)
bp.register_blueprint(berichte_bp)
bp.register_blueprint(einstellungen_bp)
bp.register_blueprint(flash_bp)

