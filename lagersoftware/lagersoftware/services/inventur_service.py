"""Inventory counting services."""
from __future__ import annotations

from ..database import db
from ..models import Article, InventoryCount


def record_count(artikelnummer: str, counted_quantity: int) -> InventoryCount | None:
    article = Article.query.filter_by(artikelnummer=artikelnummer).first()
    if not article:
        return None
    count = InventoryCount(article=article, counted_quantity=counted_quantity)
    article.stock = counted_quantity
    db.session.add(count)
    db.session.commit()
    return count


def list_counts() -> list[InventoryCount]:
    return InventoryCount.query.order_by(InventoryCount.counted_at.desc()).all()
