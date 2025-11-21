"""Dashboardsicht für Lagerinstanzen."""
from flask import Blueprint, render_template
from ..services import artikel_service, inventur_service

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    summary = artikel_service.get_inventory_summary()
    counts = inventur_service.latest_counts()
    return render_template("dashboard.html", summary=summary, counts=counts)
