"""Inventur-Routen."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from ..models import Article
from ..services import inventur_service

bp = Blueprint("inventur", __name__, url_prefix="/inventur")


@bp.route("/")
def liste():
    articles = Article.query.order_by(Article.sku).all()
    counts = inventur_service.latest_counts()
    return render_template("inventur/list.html", articles=articles, counts=counts)


@bp.route("/zaehlung", methods=["POST"])
def zaehlung():
    article_id = int(request.form["article_id"])
    quantity = int(request.form["quantity"])
    inventur_service.start_count(article_id, quantity)
    flash("Zählung gespeichert", "success")
    return redirect(url_for("inventur.liste"))
