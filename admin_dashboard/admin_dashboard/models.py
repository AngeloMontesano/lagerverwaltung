"""Zentrales Metadatenmodell für Mandanten."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Tenant(db.Model):
    # Für Abwärtskompatibilität heißt die Tabelle weiterhin "customers",
    # damit bestehende SQLite-Dateien aus früheren Experimenten automatisch
    # gefunden und mit db.create_all() angelegt werden.
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    api_key = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(32), default="created", nullable=False)
    app_version = db.Column(db.String(32), default="0.1.0")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    endpoint_url = db.Column(db.String(255))

    def __repr__(self) -> str:  # pragma: no cover - Debughilfe
        return f"<Tenant {self.code}>"
