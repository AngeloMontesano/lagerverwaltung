"""Inventory counting routes."""
from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for

from ..services import inventur_service

bp = Blueprint("inventur", __name__, url_prefix="/inventur")


@bp.route("/", methods=["GET", "POST"])
def manage():
    if request.method == "POST":
        artikelnummer = request.form.get("artikelnummer")
        counted_quantity = int(request.form.get("counted_quantity", 0))
        inventur_service.record_count(artikelnummer, counted_quantity)
        return redirect(url_for("inventur.manage"))
    counts = inventur_service.list_counts()
    return render_template("inventur/manage.html", counts=counts)
