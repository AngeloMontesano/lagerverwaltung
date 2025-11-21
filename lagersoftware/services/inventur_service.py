"""Inventur-Logik."""
from datetime import datetime
from ..models import Article, InventoryCount, db


def start_count(article_id: int, counted_quantity: int) -> InventoryCount:
    count = InventoryCount(
        article_id=article_id,
        counted_quantity=counted_quantity,
        counted_at=datetime.utcnow(),
    )
    db.session.add(count)
    article = Article.query.get(article_id)
    if article:
        article.quantity = counted_quantity
    db.session.commit()
    return count


def latest_counts(limit: int = 20):
    return (
        InventoryCount.query.order_by(InventoryCount.counted_at.desc())
        .limit(limit)
        .all()
    )
