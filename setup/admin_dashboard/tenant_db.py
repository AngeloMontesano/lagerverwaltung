"""Helper functions to talk to tenant databases (read-only)."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


@contextmanager
def _engine_context(db_url: str):
    engine: Engine | None = None
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        yield engine
    finally:
        if engine:
            engine.dispose()


def check_connection(db_url: str) -> bool:
    """Check whether the tenant database can be reached."""
    try:
        with _engine_context(db_url) as engine:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


def get_basic_inventory_stats(db_url: str) -> Dict[str, Any]:
    """Return KPIs from the tenant database.

    The queries are based on the existing schema (see setup/templates/schema.sql):
    - artikel table stores stock (`bestand`) and reorder threshold (`mindestbestand`).
    - A record is considered critical when `bestand < mindestbestand`.
    """
    stats = {"article_count": 0, "total_stock": 0, "critical_articles": 0}
    try:
        with _engine_context(db_url) as engine:
            with engine.connect() as conn:
                article_count = conn.execute(text("SELECT COUNT(*) FROM artikel")).scalar()
                total_stock = conn.execute(
                    text("SELECT COALESCE(SUM(bestand), 0) FROM artikel")
                ).scalar()
                critical_articles = conn.execute(
                    text("SELECT COUNT(*) FROM artikel WHERE bestand < mindestbestand")
                ).scalar()
        stats.update(
            {
                "article_count": int(article_count or 0),
                "total_stock": int(total_stock or 0),
                "critical_articles": int(critical_articles or 0),
            }
        )
    except SQLAlchemyError:
        # Keep defaults; caller can decide how to display errors.
        pass
    return stats
