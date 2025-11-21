"""Data models for the admin dashboard."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON

from .app import db


def utcnow():
    return datetime.utcnow()


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    customer_number = db.Column(db.String(64), unique=True, nullable=False)
    contact_email = db.Column(db.String(255))
    hosting_mode = db.Column(db.String(32), default="central")
    plan = db.Column(db.String(64), default="basic")
    created_at = db.Column(db.DateTime, default=utcnow)

    instances = db.relationship("Instance", backref="customer", lazy=True)


class Instance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    environment = db.Column(db.String(32), default="prod")
    version = db.Column(db.String(32), default="0.1.0")
    technical_name = db.Column(db.String(128))
    base_url = db.Column(db.String(255))
    api_base_url = db.Column(db.String(255))
    db_host = db.Column(db.String(255))
    db_name = db.Column(db.String(255))
    db_user = db.Column(db.String(255))
    db_port = db.Column(db.Integer, default=3306)
    hosting_mode = db.Column(db.String(32), default="central")
    status = db.Column(db.String(32), default="stopped")
    last_deploy_at = db.Column(db.DateTime)
    last_healthcheck_at = db.Column(db.DateTime)
    last_health_status = db.Column(db.String(32))
    last_inventory_summary = db.Column(JSON)
    api_auth_token = db.Column(db.String(255))


class MasterArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    default_uom = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, default=utcnow)


class SyncLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.Integer, db.ForeignKey("instance.id"), nullable=False)
    synced_at = db.Column(db.DateTime, default=utcnow)
    payload_size = db.Column(db.Integer)
    created_count = db.Column(db.Integer)
    updated_count = db.Column(db.Integer)
    status = db.Column(db.String(32), default="success")

    instance = db.relationship("Instance")
