# lagerverwaltung/wsgi.py
"""
WSGI-Einstiegspunkt für die Lagerverwaltungs-App.

Wird im Docker-Container von Gunicorn verwendet:
    gunicorn lagerverwaltung.wsgi:app
"""

from .app import create_app

# Gunicorn erwartet hier eine Variable "app"
app = create_app()
