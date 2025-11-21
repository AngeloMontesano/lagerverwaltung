"""Inventory/stock related services."""
from __future__ import annotations

from sqlalchemy import func

from ..database import db
from ..models import Article, StockMovement


def adjust_stock(article: Article, quantity: int, movement_type: str) -> StockMovement:
    article.stock = (article.stock or 0) + quantity
    movement = StockMovement(article=article, quantity=quantity, movement_type=movement_type)
    db.session.add(movement)
    db.session.commit()
    return movement


def inventory_summary() -> dict:
    total_articles = Article.query.count()
    total_stock = db.session.query(func.coalesce(func.sum(Article.stock), 0)).scalar() or 0
    critical_articles = Article.query.filter(Article.stock <= Article.critical_stock).count()
    return {
        "total_articles": total_articles,
        "total_stock": total_stock,
        "critical_articles": critical_articles,
    }
