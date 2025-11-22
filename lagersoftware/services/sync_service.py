"""Synchronisations-Helfer für zentrale Stammdaten."""
from typing import Iterable
from ..models import SyncLog, db


def log_sync(direction: str, status: str, message: str = "") -> SyncLog:
    log = SyncLog(direction=direction, status=status, message=message)
    db.session.add(log)
    db.session.commit()
    return log


def import_master_articles(records: Iterable[dict]) -> dict:
    """Platzhalter für eine spätere Stammdaten-Synchronisation."""
    count = len(list(records))
    log_sync("import", "success", f"{count} Datensätze verarbeitet")
    return {"processed": count}
