# Admin Dashboard

Dieses Dashboard steuert und überwacht alle mandantenspezifischen Lagersoftware-Instanzen. Es ist als eigenständige Flask-Anwendung mit Application-Factory aufgebaut und nutzt SQLAlchemy/Flask-Migrate für das persistente Metadaten-Model.

## Hauptfunktionen
- Kunden- und Instanzenverwaltung (CRUD light)
- Stub-Steuerung für Start/Stop/Restart/Update über `docker_client.py`
- Health- und Inventurabfragen gegen Mandanten-APIs via `instance_api.py`
- Zentrale Stammdaten (`MasterArticle`) mit Push an Mandanten

## Lokaler Start
```bash
cd admin_dashboard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=admin_dashboard.app:create_app
export DASHBOARD_DATABASE_URI=sqlite:///data/dashboard.db
export DASHBOARD_SECRET_KEY=dev-secret
flask db upgrade  # ggf. vorher flask db init/migrate
flask run --host 0.0.0.0 --port 8000
```

## Docker
```bash
cd admin_dashboard
docker compose up --build
```
Erreichbar unter `http://localhost:8100`. Die SQLite-DB wird unter `./data` persistiert.

## Wichtige Umgebungsvariablen
- `DASHBOARD_DATABASE_URI`
- `DASHBOARD_SECRET_KEY`
- `INSTANCE_API_TIMEOUT`

## Architektur-Hinweise
Details siehe `ARCHITECTURE.md`. Kernelemente:
- `models.py`: Customer, Instance, MasterArticle, SyncLog
- `docker_client.py`: Platzhalter für echte Docker/Portainer-Integration
- `instance_api.py`: REST-Client für Mandanten-APIs (`/api/health`, `/api/inventory/summary`, `/api/articles/bulk_upsert`)
- Blueprints unter `routes/admin.py` für UI-Views
