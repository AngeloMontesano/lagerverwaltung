"""SQLAlchemy-Modelle der Lagersoftware."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Article(db.Model, TimestampMixin):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class InventoryCount(db.Model, TimestampMixin):
    __tablename__ = "inventory_counts"

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)
    counted_quantity = db.Column(db.Integer, nullable=False)
    counted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    article = db.relationship(Article, backref=db.backref("counts", lazy=True))


class SyncLog(db.Model, TimestampMixin):
    __tablename__ = "sync_logs"

    id = db.Column(db.Integer, primary_key=True)
    direction = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(32), nullable=False)
    message = db.Column(db.Text)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "direction": self.direction,
            "status": self.status,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
        }
