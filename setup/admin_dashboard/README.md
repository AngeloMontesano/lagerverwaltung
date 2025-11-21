# Admin-Dashboard für Lagerverwaltungsinstanzen

Dieses Dashboard ist eine eigenständige Flask-Anwendung, die Ihre kundenbezogenen Lagerverwaltungsinstanzen verwaltet. Es ersetzt **nicht** die Lager-App der Kunden, sondern dient als zentrale Konsole für Betrieb, Monitoring und zukünftige Erweiterungen.

## Features
- Multi-Mandanten-Datenmodell mit `Customer` und `Instance`
- Übersicht aller Kundeninstanzen mit Status, Version und Links
- Detailseite mit Steuerungsaktionen (Start/Stop/Restart/Update – stub)
- Lesender Zugriff auf Mandanten-DBs für KPIs (Artikelanzahl, Gesamtbestand, kritische Artikel)
- Klare Trennung zwischen Dashboard-DB (Metadaten) und Mandanten-DBs (Lagerdaten)

## Projektstruktur
```
setup/admin_dashboard/
├── app.py                # Flask Application Factory
├── config.py             # Konfiguration (DB, Secrets, Docker-Endpoint)
├── docker_client.py      # Stub für spätere Docker/Portainer/K8s-Integration
├── docker-compose.yml    # Compose-Setup für das Dashboard
├── Dockerfile            # Container-Build
├── models.py             # Dashboard-Datenmodell
├── requirements.txt      # Python-Abhängigkeiten
├── routes/               # Flask-Blueprints
├── static/               # CSS/Assets
├── templates/            # Jinja2-Templates
├── tenant_db.py          # Lesender Zugriff auf Mandanten-DBs
└── ARCHITECTURE.md       # Architekturbeschreibung
```

## Installation & Start
### Lokal mit Python
```bash
cd setup/admin_dashboard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app:create_app
export DASHBOARD_DATABASE_URI=sqlite:///data/dashboard.db  # optional anpassen
flask db init  # nur beim ersten Mal
flask db migrate -m "init dashboard"
flask db upgrade
flask run --host 0.0.0.0 --port 8000
```

### Mit Docker
```bash
cd setup/admin_dashboard
docker compose up --build
```
Das Dashboard ist dann unter `http://localhost:8100` erreichbar. Die SQLite-DB wird im `./data`-Verzeichnis persistiert.

## Datenmodell
- `Customer`: Name, Kundennummer, Kontakt, Tarif, Zeitstempel
- `Instance`: technische Kennung, Umgebung, Version, Status, `db_url`, `base_url`, Zeitstempel

## Mandanten-DB-Integration
- Jede Instanz besitzt einen vollständigen SQLAlchemy-Connection-String (`db_url`), z. B. `mysql+pymysql://user:pass@host:3306/lagerdb`.
- `tenant_db.py` prüft die Verbindung (`check_connection`) und liefert KPIs (`get_basic_inventory_stats`) basierend auf dem bestehenden Schema (`artikel`-Tabelle aus `setup/templates/schema.sql`).
- Schreibzugriff findet nicht statt; Mandanten-DBs werden nur gelesen.

## Hinweis zur zukünftigen Erweiterung
`docker_client.py` enthält kommentierte Platzhalter für echte Docker-/Portainer-/Kubernetes-Aufrufe. Die Serviceschicht kann ohne Änderung der UI gegen eine echte Umsetzung getauscht werden. Weitere Features wie Artikelreplikation, Monitoring oder Backups lassen sich über zusätzliche Services/Blueprints ergänzen.
