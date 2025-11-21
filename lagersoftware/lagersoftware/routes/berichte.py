"""Report routes."""
from __future__ import annotations

from flask import Blueprint, render_template

from ..services import reports_service

bp = Blueprint("berichte", __name__, url_prefix="/berichte")


@bp.route("/inventur")
def inventory_report():
    report = reports_service.generate_inventory_report()
    return render_template("berichte/inventur.html", report=report)
