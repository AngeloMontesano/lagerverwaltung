"""Order handling services."""
from __future__ import annotations

from ..database import db
from ..models import Article, Order, OrderItem


def create_order(order_number: str, items: list[dict]) -> Order:
    order = Order(order_number=order_number)
    db.session.add(order)
    db.session.flush()
    for item in items:
        article = Article.query.filter_by(artikelnummer=item["artikelnummer"]).first()
        if not article:
            continue
        order_item = OrderItem(order_id=order.id, article_id=article.id, quantity=item.get("quantity", 0))
        db.session.add(order_item)
    db.session.commit()
    return order


def list_orders() -> list[Order]:
    return Order.query.order_by(Order.created_at.desc()).all()
