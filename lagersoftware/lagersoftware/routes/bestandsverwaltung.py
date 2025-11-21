"""Stock management routes."""
from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for

from ..services import artikel_service, bestands_service

bp = Blueprint("bestandsverwaltung", __name__, url_prefix="/bestand")


@bp.route("/anpassen", methods=["GET", "POST"])
def adjust():
    articles = artikel_service.list_articles()
    if request.method == "POST":
        article_id = int(request.form.get("article_id"))
        quantity = int(request.form.get("quantity", 0))
        movement_type = request.form.get("movement_type", "manual")
        article = artikel_service.get_article(article_id)
        if article:
            bestands_service.adjust_stock(article, quantity, movement_type)
        return redirect(url_for("bestandsverwaltung.adjust"))
    return render_template("bestand/adjust.html", articles=articles)
