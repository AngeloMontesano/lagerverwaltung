# Lagersoftware (Mandanten-Instanz)

Dieses Paket stellt eine mandantenfähige Lagerverwaltung bereit, die pro Kunde als eigenständige Instanz (Container + Datenbank) betrieben wird. Eine Admin-Konsole orchestriert die Bereitstellung; diese README beschreibt den Betrieb einer einzelnen Instanz.

## Start mit Docker Compose

```bash
cd lagersoftware
CUSTOMER_CODE=demo API_KEY=geheim docker compose up -d --build
```

Wichtige Umgebungsvariablen:

- `CUSTOMER_CODE`: eindeutiger Mandanten-Code, erscheint im Logging und in API-Responses.
- `DATABASE_URL`: vollständige SQLAlchemy-URL (Standard zeigt auf den MariaDB-Service aus `docker-compose.yml`).
- `API_KEY`: Schlüssel zur Absicherung der REST-API.
- `APP_VERSION`: Version der Instanz, erscheint im Health-Endpunkt.
- `LOG_LEVEL`: z. B. `INFO` oder `DEBUG`.

Die Anwendung läuft per Standard auf Port `5000`; mit `APP_PORT` kann eine externe Portzuordnung gesetzt werden.

## REST-API

| Methode | Pfad | Beschreibung | Auth |
| --- | --- | --- | --- |
| GET | `/api/health` | Status, Mandant und Version der Instanz | `X-API-Key`
| GET | `/api/inventory/summary` | Anzahl Artikel und Gesamtmenge | `X-API-Key`
| POST | `/api/articles/bulk_upsert` | Artikel-Liste (JSON) anlegen/aktualisieren | `X-API-Key`
| POST | `/api/sync/master` | Platzhalter für Stammdaten-Sync | `X-API-Key`

Beispielaufruf:

```bash
curl -H "X-API-Key: geheim" http://localhost:5000/api/health
```

## Architektur

- **Application Factory** in `lagersoftware/app.py` (für Gunicorn nutzbar)
- **Config** in `lagersoftware/config.py` liest Umgebungsvariablen
- **Modelle** in `lagersoftware/models.py` (SQLAlchemy)
- **Services** kapseln Geschäftslogik (`services/*.py`)
- **Routes** trennen Web-UI und API (`routes/*.py`)
- **Logging** ergänzt tenant-Kontext über einen Filter

Die Datenbanktabellen werden beim Start automatisch angelegt; für produktive Umgebungen kann `flask db`/Migrations genutzt werden.
