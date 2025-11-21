# =============================================
# 🔹 Lagerverwaltungs-App mit Flask
# =============================================

from flask import Flask, render_template
# Relative Imports innerhalb des Pakets "lagerverwaltung"
from .database import db, init_db  # Importiere db und init_db
from .routes import (
    artikel, bestandsverwaltung, bestellungen,
    dashboard, inventur, berichte, einstellungen, flash,
)

# =============================================
# 🔹 Flask-App erstellen und konfigurieren
# =============================================
def create_app():
    """
    Erstellt und konfiguriert die Flask-App.
    """
    app = Flask(__name__)
    init_db(app)  # Verbindung zur Datenbank herstellen

    # =============================================
    # 🔹 Blueprints für die einzelnen Module registrieren
    # =============================================
    app.register_blueprint(artikel.bp, url_prefix="/artikel")
    app.register_blueprint(bestandsverwaltung.bp, url_prefix="/bestandsverwaltung")
    app.register_blueprint(bestellungen.bp, url_prefix="/bestellungen")
    app.register_blueprint(inventur.bp, url_prefix="/inventur")
    app.register_blueprint(dashboard.bp, url_prefix="/dashboard")
    app.register_blueprint(berichte.bp, url_prefix="/berichte")
    app.register_blueprint(einstellungen.bp, url_prefix="/einstellungen")
    app.register_blueprint(flash.bp)

    # =============================================
    # 🔹 Startseite definieren
    # =============================================
    @app.route("/")
    def index():
        """Startseite anzeigen"""
        # Lädt die index.html aus dem templates-Ordner
        return render_template("index.html")

    return app


# =============================================
# 🔹 Hauptprogramm: App starten (nur lokal/dev)
# =============================================
if __name__ == "__main__":
    app = create_app()

    # Debugging: Alle registrierten Routen ausgeben
    with app.app_context():
        print("🚀 Registrierte Routen:")
        for rule in app.url_map.iter_rules():
            print(f"{rule} -> {rule.endpoint}")

    # Starte die Flask-App im Debug-Modus
    app.run(host="0.0.0.0", port=5000, debug=True)
