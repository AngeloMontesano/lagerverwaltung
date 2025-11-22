# Architekturüberblick

Dieses Dokument beschreibt die modulare Struktur der Multi-Tenant-Lagerlösung.

## Komponenten

- **Lagersoftware (`lagersoftware/`)**: Flask-App pro Mandant, stellt Web-UI und REST-API bereit. Jede Instanz erhält eigene Env-Variablen (DATABASE_URL, CUSTOMER_CODE, API_KEY, APP_VERSION).
- **Admin Dashboard (`admin_dashboard/`)**: Control Plane zur Verwaltung der Mandanten, Ausrollen/Stoppen von Instanzen sowie Health-/Inventur-Abfragen über die REST-API.

## Paketstruktur der Mandanten-App

```
lagersoftware/
  app.py            # Application Factory + Logging
  config.py         # liest Env-Variablen
  models.py         # SQLAlchemy-Modelle (Artikel, Inventur, Sync)
  services/         # Geschäftslogik pro Domäne
  routes/           # Blueprint-basiertes Routing (Web + API)
  templates/, static/
  Dockerfile, docker-compose.yml
```

### REST-API

- `GET /api/health` – Status, Mandanten-Code, Version
- `GET /api/inventory/summary` – Anzahl Artikel und Gesamtmenge
- `POST /api/articles/bulk_upsert` – Artikel anlegen/aktualisieren (JSON-Liste)
- `POST /api/sync/master` – Platzhalter für Stammdatenimport

Authentifizierung erfolgt über Header `X-API-Key` (oder `Authorization`), der mit `API_KEY` aus der Instanz-Konfiguration übereinstimmen muss.

## Admin-Dashboard-Struktur

```
admin_dashboard/
  admin_dashboard/app.py      # Application Factory
  admin_dashboard/models.py   # Tenant-Metadaten
  admin_dashboard/routes/     # UI- und Steuer-Routen
  admin_dashboard/docker_client.py  # Compose/Portainer-Ansteuerung
  admin_dashboard/instance_api.py   # Sichere Kommunikation zur Mandanten-API
  templates/, static/
  Dockerfile, docker-compose.yml
```

## Deployment-Modell

- **Pro Mandant** ein Compose-Stack mit zwei Containern: `app` (Flask+Gunicorn) und `db` (MariaDB).
- Env-Variablen werden je Stack gesetzt (`CUSTOMER_CODE`, `API_KEY`, `APP_VERSION`).
- Logs enthalten den Mandanten-Kontext (Log-Filter in `lagersoftware/app.py`).
- Das Admin-Dashboard kann wahlweise lokal `docker compose up` ausführen oder über die Portainer-API einen Stack aktualisieren.

## Lebenszyklus eines Mandanten

1. Mandant im Admin-Dashboard anlegen (Code, Name, API-Key).
2. Deployment triggern → Compose/Portainer startet DB + App-Container mit tenant-spezifischen Variablen.
3. Health-Check über `/api/health` prüfen; Dashboard zeigt Status.
4. Stammdaten-Sync optional via `/api/sync/master`.
5. Updates: Neues Image/Version deployen, `APP_VERSION` hochsetzen, Rolling-Update durch erneutes Compose/Portainer-Deploy.

## Service/Route/Model-Trennung

- **Routes** kümmern sich um HTTP, Validierung und Antwortformate.
- **Services** kapseln Geschäftsregeln (z. B. Bulk-Upsert, Inventur-Logik).
- **Modelle** definieren nur das Datenmodell; DB-Zugriff erfolgt über Services.
