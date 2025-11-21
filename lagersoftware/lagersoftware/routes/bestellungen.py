"""Order routes."""
from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for

from ..services import bestellungen_service

bp = Blueprint("bestellungen", __name__, url_prefix="/bestellungen")


@bp.route("/")
def list_view():
    orders = bestellungen_service.list_orders()
    return render_template("bestellungen/list.html", orders=orders)


@bp.route("/neu", methods=["GET", "POST"])
def create_view():
    if request.method == "POST":
        order_number = request.form.get("order_number")
        bestellungen_service.create_order(order_number=order_number, items=[])
        return redirect(url_for("bestellungen.list_view"))
    return render_template("bestellungen/new.html")
