"""Reporting helpers."""
from __future__ import annotations

from . import bestands_service


def generate_inventory_report() -> dict:
    """Return a simple inventory report payload."""
    return bestands_service.inventory_summary()
