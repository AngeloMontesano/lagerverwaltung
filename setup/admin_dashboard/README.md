# Admin-Dashboard für Lagerverwaltungsinstanzen

Dieses Dashboard ist eine eigenständige Flask-Anwendung im Package `admin_dashboard`, die Ihre kundenbezogenen Lagerverwaltungsinstanzen verwaltet. Es ersetzt **nicht** die Lager-App der Kunden, sondern dient als zentrale Konsole für Betrieb, Monitoring und zukünftige Erweiterungen.

## Features
- Multi-Mandanten-Datenmodell mit `Customer` und `Instance`
- Übersicht aller Kundeninstanzen mit Status, Version und Links
- Detailseite mit Steuerungsaktionen (Start/Stop/Restart/Update – Stub)
- Lesender Zugriff auf Mandanten-DBs für KPIs (Artikelanzahl, Gesamtbestand, kritische Artikel)
- Klare Trennung zwischen Dashboard-DB (Metadaten) und Mandanten-DBs (Lagerdaten)

## Projektstruktur
```
setup/admin_dashboard/
├── admin_dashboard/          # Python-Package für das Dashboard
│   ├── __init__.py
│   ├── app.py                # Flask Application Factory
│   ├── config.py             # Konfiguration (DB, Secrets, Docker-Endpoint)
│   ├── docker_client.py      # Stub für spätere Docker/Portainer/K8s-Integration
│   ├── models.py             # Dashboard-Datenmodell
│   ├── routes/               # Flask-Blueprints
│   ├── static/               # CSS/Assets
│   ├── templates/            # Jinja2-Templates
│   └── tenant_db.py          # Lesender Zugriff auf Mandanten-DBs
├── Dockerfile                # Container-Build
├── docker-compose.yml        # Compose-Setup für das Dashboard
├── requirements.txt          # Python-Abhängigkeiten
├── README.md                 # Diese Datei
└── ARCHITECTURE.md           # Architekturbeschreibung
```

## Lokal starten (ohne Docker)
```bash
cd setup/admin_dashboard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export FLASK_APP=admin_dashboard.app:create_app
export DASHBOARD_DATABASE_URI=sqlite:///data/dashboard.db  # optional anpassen
export DASHBOARD_SECRET_KEY=dev-secret-key                  # bitte ersetzen

flask db upgrade  # setzt die Dashboard-DB auf, nach Bedarf vorher flask db init/migrate
flask run --host 0.0.0.0 --port 8000
```

## Start mit Docker
```bash
cd setup/admin_dashboard
docker compose up --build -d
```
Das Dashboard ist dann unter `http://localhost:8100` erreichbar. Die SQLite-DB wird im `./data`-Verzeichnis persistiert.

## Anwendung über Gunicorn
Im Container (siehe Dockerfile) wird die App mit Gunicorn geladen:
```bash
gunicorn -b 0.0.0.0:8000 "admin_dashboard.app:create_app()"
```
Die Application-Factory wird direkt aus dem Package aufgerufen, sodass alle Importe paketkonform funktionieren.

## Mandanten-DB-Integration
- Jede Instanz besitzt einen vollständigen SQLAlchemy-Connection-String (`db_url`), z. B. `mysql+pymysql://user:pass@host:3306/lagerdb`.
- `tenant_db.py` prüft die Verbindung (`check_connection`) und liefert KPIs (`get_basic_inventory_stats`) basierend auf dem bestehenden Schema (`artikel`-Tabelle aus `setup/templates/schema.sql`).
- Schreibzugriff findet nicht statt; Mandanten-DBs werden nur gelesen.

## Hinweis zur zukünftigen Erweiterung
`docker_client.py` enthält kommentierte Platzhalter für echte Docker-/Portainer-/Kubernetes-Aufrufe. Die Serviceschicht kann ohne Änderung der UI gegen eine echte Umsetzung getauscht werden. Weitere Features wie Artikelreplikation, Monitoring oder Backups lassen sich über zusätzliche Services/Blueprints ergänzen.
