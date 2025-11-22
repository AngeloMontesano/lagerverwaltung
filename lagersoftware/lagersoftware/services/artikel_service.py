"""Service layer for article operations."""
from __future__ import annotations

from typing import Iterable

from ..database import db
from ..models import Article


def list_articles() -> list[Article]:
    return Article.query.order_by(Article.name).all()


def get_article(article_id: int) -> Article | None:
    return Article.query.get(article_id)


def create_article(data: dict) -> Article:
    article = Article(**data)
    db.session.add(article)
    db.session.commit()
    return article


def update_article(article: Article, data: dict) -> Article:
    for key, value in data.items():
        setattr(article, key, value)
    db.session.commit()
    return article


def delete_article(article: Article) -> None:
    db.session.delete(article)
    db.session.commit()


def bulk_upsert_articles(articles: Iterable[dict]) -> dict:
    created = 0
    updated = 0
    processed = 0
    for payload in articles:
        processed += 1
        artikelnummer = payload.get("artikelnummer")
        if not artikelnummer:
            continue
        article = Article.query.filter_by(artikelnummer=artikelnummer).first()
        if article:
            update_article(article, payload)
            updated += 1
        else:
            create_article(payload)
            created += 1
    return {"processed": processed, "created": created, "updated": updated}
