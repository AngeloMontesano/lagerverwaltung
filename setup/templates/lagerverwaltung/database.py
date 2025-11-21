# =============================================
# 🔹 Datenbank-Setup für die Lagerverwaltungs-App
# =============================================

import os
from flask_sqlalchemy import SQLAlchemy

# =============================================
# 🔹 SQLAlchemy Instanz initialisieren
# =============================================
db = SQLAlchemy()

def init_db(app):
    """
    Initialisiert die Datenbank und bindet sie an die Flask-App.
    """
    app.config.from_object(Config)  # Konfiguration aus der Config-Klasse laden
    db.init_app(app)  # SQLAlchemy mit der Flask-App verbinden

    with app.app_context():
        db.create_all()  # Erstellt alle Tabellen, falls sie noch nicht existieren

# =============================================
# 🔹 Konfigurationsklasse für die Flask-App & Datenbank
# =============================================
class Config:
    """
    Enthält die Konfiguration für die Flask-Anwendung,
    einschließlich der Datenbankverbindung und Sicherheitsoptionen.
    """

    # 🔹 Datenbankverbindung für MariaDB
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://lageruser:lagerpass@localhost/lagerdb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Deaktiviert unnötige Änderungsnachverfolgung

    # 🔹 Sicherheitseinstellungen
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # Schlüssel für sichere Sessions
