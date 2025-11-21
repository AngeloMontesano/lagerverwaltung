"""Blueprint registration."""
from __future__ import annotations

from flask import Flask

from . import dashboard, artikel, bestellungen, bestandsverwaltung, inventur, berichte, einstellungen, api


BLUEPRINTS = [
    dashboard.bp,
    artikel.bp,
    bestellungen.bp,
    bestandsverwaltung.bp,
    inventur.bp,
    berichte.bp,
    einstellungen.bp,
    api.bp,
]


def register_blueprints(app: Flask) -> None:
    for bp in BLUEPRINTS:
        app.register_blueprint(bp)
