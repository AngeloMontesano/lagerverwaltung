"""Bestandsverwaltung."""
from ..models import Article, db


def adjust_stock(article_id: int, delta: int) -> Article:
    article = Article.query.get_or_404(article_id)
    article.quantity = (article.quantity or 0) + delta
    db.session.commit()
    return article
