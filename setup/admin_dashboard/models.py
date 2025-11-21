"""Dashboard database models."""
from __future__ import annotations

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    customer_number = db.Column(db.String(50), unique=True, nullable=False)
    contact = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    plan = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    instances = db.relationship("Instance", back_populates="customer", cascade="all, delete")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Customer {self.customer_number}>"


class Instance(db.Model):
    __tablename__ = "instances"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    environment = db.Column(db.String(50), default="prod", nullable=False)
    version = db.Column(db.String(50), default="latest", nullable=False)
    technical_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default="stopped", nullable=False)
    db_url = db.Column(db.String(1024), nullable=False)
    base_url = db.Column(db.String(1024), nullable=False)
    last_deploy_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    customer = db.relationship("Customer", back_populates="instances")

    def mark_status(self, status: str) -> None:
        """Update the instance status with a timestamp."""
        self.status = status
        self.last_deploy_at = datetime.utcnow()

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Instance {self.technical_name} ({self.environment})>"
