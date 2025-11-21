"""Database models for the warehouse application."""
from __future__ import annotations

from datetime import datetime

from .database import db


def utcnow():
    return datetime.utcnow()


class Article(db.Model):
    __tablename__ = "artikel"
    id = db.Column(db.Integer, primary_key=True)
    artikelnummer = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), default=0)
    stock = db.Column(db.Integer, default=0)
    critical_stock = db.Column(db.Integer, default=0)
    barcode = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    def __repr__(self) -> str:  # pragma: no cover - repr for debugging
        return f"<Article {self.artikelnummer}>"


class StockMovement(db.Model):
    __tablename__ = "stock_movements"
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("artikel.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    article = db.relationship("Article", backref=db.backref("movements", lazy=True))


class Order(db.Model):
    __tablename__ = "bestellungen"
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.String(32), default="open")
    created_at = db.Column(db.DateTime, default=utcnow)


class OrderItem(db.Model):
    __tablename__ = "bestellpositionen"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("bestellungen.id"), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("artikel.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", backref=db.backref("items", lazy=True))
    article = db.relationship("Article")


class InventoryCount(db.Model):
    __tablename__ = "inventur"
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("artikel.id"), nullable=False)
    counted_quantity = db.Column(db.Integer, nullable=False)
    counted_at = db.Column(db.DateTime, default=utcnow)

    article = db.relationship("Article", backref=db.backref("inventory_counts", lazy=True))
