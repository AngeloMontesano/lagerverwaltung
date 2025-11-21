# =============================================
# 🔹 Konfigurationsdatei für die Flask-App
# =============================================

import os

class Config:
    """
    Konfigurationsklasse für die Flask-Anwendung.
    Enthält Einstellungen für die Datenbank, Sicherheit und maximale Request-Größe.
    """

    # =============================================
    # 🔹 Datenbankverbindung für MariaDB
    # =============================================
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://lageruser:lagerpass@localhost/lagerdb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Deaktiviert unnötige Änderungsnachverfolgung

    # =============================================
    # 🔹 Sicherheitseinstellungen
    # =============================================
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # Schlüssel für sichere Sessions

    # =============================================
    # 🔹 Maximale Größe für Datei-Uploads (10 MB)
    # =============================================
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
