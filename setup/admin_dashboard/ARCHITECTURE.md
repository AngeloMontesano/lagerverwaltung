# Architektur des Admin-Dashboards

## Überblick
Das Dashboard ist eine separate Flask-Anwendung, die ausschließlich zur Verwaltung der mandantenfähigen Lagerverwaltungsinstanzen dient. Die eigentliche Lager-App läuft pro Kunde als eigene Instanz und bleibt unberührt.

Das System ist in Schichten gegliedert, sodass spätere Erweiterungen (Artikelreplikation, Monitoring, Backups, Lizenzverwaltung) ohne Bruch integrierbar sind.

## Schichten
- **Web/UI (Blueprint `admin`)**: Routen für Übersicht und Instanzdetails, Rendering der Templates.
- **Service/Business-Logik**: Steuerung der Instanzen über `docker_client.py` (aktuell Stub) und lesender Zugriff auf Mandanten-DBs über `tenant_db.py`.
- **Infrastruktur/Datenspeicher**:
  - Dashboard-DB für Metadaten (`models.py`, `Flask-SQLAlchemy`).
  - Mandanten-DBs (per `db_url`), nur lesend für KPIs.

## Hauptmodule
- `app.py`: Application Factory, Blueprint-Registrierung, Migrations-Setup.
- `config.py`: Zentrale Konfiguration (DB-URI, Secret Key, Docker-Endpoint-Platzhalter).
- `models.py`: Datenmodell mit `Customer` und `Instance` inklusive Zeitstempel und Status.
- `routes/admin.py`: UI-Logik, Tabellenübersicht, Detailseite, Steuerungsaktionen.
- `docker_client.py`: Stub-Client für Lifecycle-Aktionen. Kommentare markieren die Stellen, an denen später Docker/Portainer/Kubernetes angebunden wird.
- `tenant_db.py`: Lesender Zugriff auf Mandanten-DBs. Nutzt das bestehende Schema (`artikel`-Tabelle) für KPIs (Anzahl Artikel, Summe Bestand, kritische Artikel).

## Wichtige Flows
1. **Übersicht laden**
   - Admin ruft `/` auf → `routes/admin.dashboard` lädt alle Kunden inkl. Instanzen → `dashboard.html` rendert Tabellenansicht.
2. **Instanzdetails & Steuerung**
   - Admin öffnet `/instance/<id>` → `routes/admin.instance_detail` lädt Instanz.
   - POST-Formular löst Aktionen `start/stop/restart/update` aus → `DockerClient` aktualisiert Status/Version (Stub) und persistiert in Dashboard-DB.
   - Anschließend Redirect zurück auf die Detailseite.
3. **KPI-Abfrage**
   - `instance_detail` prüft per `check_connection(db_url)` die Mandanten-DB.
   - Bei Erfolg werden mit `get_basic_inventory_stats` echte Werte aus der `artikel`-Tabelle geholt (COUNT, SUM, kritische Artikel via `bestand < mindestbestand`).

## Erweiterbarkeit
- **Artikelreplikation**: Neue Services/Blueprints können auf `tenant_db.py` aufbauen oder eigene Module einführen.
- **Monitoring & Alerts**: Healthchecks und Error-Logs können als zusätzliche Hintergrundjobs oder Blueprints ergänzt werden, ohne die Webschicht zu ändern.
- **Backups/Restore**: Weitere Infrastrukturmodule können an `DockerClient` oder neue Klassen angedockt werden.
- **Tarif-/Lizenzverwaltung**: Zusätzliche Felder/Modelle lassen sich via Migrationen ergänzen, ohne die Trennung der Mandanten-Ebenen aufzuheben.

## Datenbankschema der Mandanten
Basierend auf `setup/templates/schema.sql` wird die Tabelle `artikel` genutzt, um die KPIs zu ermitteln:
- `bestand`: aktueller Lagerbestand
- `mindestbestand`: Schwelle für kritische Bestände (`bestand < mindestbestand`)
- Weitere Tabellen (z. B. `kunde`, `lagerbewegungen`, `bestellungen`) bleiben unverändert und können später für zusätzliche KPIs genutzt werden.
