"""Article pages."""
from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for

from ..services import artikel_service

bp = Blueprint("artikel", __name__, url_prefix="/artikel")


@bp.route("/")
def list_view():
    articles = artikel_service.list_articles()
    return render_template("artikel/list.html", articles=articles)


@bp.route("/neu", methods=["GET", "POST"])
def create_view():
    if request.method == "POST":
        artikel_service.create_article(
            {
                "artikelnummer": request.form.get("artikelnummer"),
                "name": request.form.get("name"),
                "description": request.form.get("description"),
                "price": request.form.get("price", 0),
                "stock": int(request.form.get("stock", 0)),
                "critical_stock": int(request.form.get("critical_stock", 0)),
            }
        )
        return redirect(url_for("artikel.list_view"))
    return render_template("artikel/new.html")
