# Lagersoftware (Mandantenfähige Instanz)

Diese Anwendung ist eine neu strukturierte Warehouse-App pro Kunde. Sie nutzt Flask mit Application-Factory, Blueprints und einer Serviceschicht. Jede Instanz kann separat betrieben werden (z. B. per Docker Compose) und stellt zusätzlich eine gesicherte REST-API für das zentrale Admin-Dashboard bereit.

## Features
- Artikel-, Bestands-, Bestell- und Inventur-Workflows (vereinfachte UI)
- Service-Layer für wiederverwendbare Geschäftslogik
- REST-API mit Token-Authentifizierung (`X-API-TOKEN`)
- Logging mit Mandantenkennung

## Starten (lokal)
```bash
cd lagersoftware
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=lagersoftware.app:create_app
export DATABASE_URL=sqlite:///lagersoftware.db
flask db upgrade  # falls Migrationen genutzt werden sollen
flask run --host 0.0.0.0 --port 5000
```

## REST-API
- `GET /api/health` – Status, Version, Tenant
- `GET /api/inventory/summary` – Artikelanzahl, Gesamtbestand, kritische Artikel
- `POST /api/articles/bulk_upsert` – `{ "articles": [ {"artikelnummer": "A1", ...} ] }`
- `POST /api/heartbeat` – Heartbeat-Endpoint für spätere Telefon-Home-Szenarien

Alle API-Calls müssen den Header `X-API-TOKEN` mit dem Wert aus `API_AUTH_TOKEN` schicken.

## Docker Compose (Einzelinstanz)
Siehe `docker-compose.yml` als Vorlage. Beispielstart:
```bash
cd lagersoftware
docker compose up --build
```

## Konfiguration
Wichtige Umgebungsvariablen:
- `DATABASE_URL` – SQLAlchemy-Connection-String
- `TENANT_ID` – Mandantenkennung
- `API_AUTH_TOKEN` – Token für gesicherte REST-API
- `SECRET_KEY` – Flask Secret
- `APP_VERSION` – Versionskennung
- `ENVIRONMENT` – z. B. dev/test/prod
