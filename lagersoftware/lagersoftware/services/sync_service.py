"""Synchronization services for master data."""
from __future__ import annotations

from . import artikel_service


def bulk_upsert_articles(payload: list[dict]) -> dict:
    return artikel_service.bulk_upsert_articles(payload)
