"""CRUD für Artikel."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from ..models import Article, db

bp = Blueprint("artikel", __name__, url_prefix="/artikel")


@bp.route("/")
def liste():
    articles = Article.query.order_by(Article.sku).all()
    return render_template("artikel/list.html", articles=articles)


@bp.route("/neu", methods=["GET", "POST"])
def erstellen():
    if request.method == "POST":
        article = Article(
            sku=request.form["sku"],
            name=request.form.get("name", ""),
            description=request.form.get("description"),
            quantity=int(request.form.get("quantity") or 0),
        )
        db.session.add(article)
        db.session.commit()
        flash("Artikel angelegt", "success")
        return redirect(url_for("artikel.liste"))
    return render_template("artikel/new.html")
