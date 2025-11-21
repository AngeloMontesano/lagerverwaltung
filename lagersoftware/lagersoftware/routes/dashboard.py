"""Dashboard views."""
from __future__ import annotations

from flask import Blueprint, render_template

from ..services import bestands_service, bestellungen_service

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    stats = bestands_service.inventory_summary()
    orders = bestellungen_service.list_orders()[:5]
    return render_template("dashboard.html", stats=stats, orders=orders)
