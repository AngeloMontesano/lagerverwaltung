"""Geschäftslogik für Artikel."""
from typing import Iterable, List
from sqlalchemy.exc import IntegrityError
from ..models import Article, db


def list_articles() -> List[Article]:
    return Article.query.order_by(Article.sku).all()


def get_inventory_summary() -> dict:
    count = Article.query.count()
    total_qty = db.session.query(db.func.sum(Article.quantity)).scalar() or 0
    return {"artikel": count, "gesamtmenge": int(total_qty)}


def bulk_upsert(payload: Iterable[dict]) -> dict:
    created = 0
    updated = 0
    for item in payload:
        sku = item.get("sku")
        if not sku:
            continue
        article = Article.query.filter_by(sku=sku).first()
        if article:
            article.name = item.get("name", article.name)
            article.description = item.get("description", article.description)
            article.quantity = item.get("quantity", article.quantity)
            updated += 1
        else:
            article = Article(
                sku=sku,
                name=item.get("name", sku),
                description=item.get("description"),
                quantity=item.get("quantity", 0),
            )
            db.session.add(article)
            created += 1
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise
    return {"created": created, "updated": updated}
