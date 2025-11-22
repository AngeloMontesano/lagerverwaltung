# Architektur des Admin Dashboards

## Überblick
Das Dashboard bildet die Kontroll-Ebene einer mandantenfähigen Lagersoftware. Es verwaltet Kunden und deren Instanzen, ermöglicht grundlegende Lifecycle-Operationen (stub) und spricht über eine REST-API mit den einzelnen Mandanten-Instanzen.

## Komponenten
- **Application Factory** (`admin_dashboard/app.py`): Initialisiert Flask, SQLAlchemy und Migrationen.
- **Modelle** (`models.py`):
  - `Customer`: Mandantenstammdaten
  - `Instance`: Technische Informationen je Instanz inkl. API-URL, Status, Version
  - `MasterArticle`: Zentrale Artikelstammdaten zur Replikation
  - `SyncLog`: Historie der Synchronisationsläufe
- **docker_client.py**: Stub für Container-Orchestrierung. Die Methoden können später durch echte Docker/Portainer/Kubernetes-Aufrufe ersetzt werden.
- **instance_api.py**: HTTP-Client, der die Mandanten-APIs (`/api/health`, `/api/inventory/summary`, `/api/articles/bulk_upsert`) aufruft und Timeouts/Fehler propagiert.
- **Blueprints** (`routes/admin.py`): UI-Interaktionen für Dashboard, Kunden-, Instanz- und Stammdaten-Ansichten.

## Datenfluss
1. Betreiber legt Kunde + Instanz im Dashboard an.
2. `docker_client` setzt Status der Instanz (aktuell Stub) und könnte später Deployments triggern.
3. Über Buttons auf der Instanz-Detailseite werden Health-Checks und Inventur-Kennzahlen per `instance_api` geladen und im Instance-Record gespeichert.
4. Stammdaten-Sync baut eine Artikel-Payload aus `MasterArticle` und überträgt sie an den Mandanten. Ergebnisse werden in `SyncLog` abgelegt.

## Erweiterungspunkte
- Austausch des Stub-`docker_client` gegen Docker SDK oder Portainer API.
- Cron/Background-Jobs für regelmäßige Healthchecks und KPIs.
- Unterstützung mehrerer Hosting-Varianten pro Instanz (on-prem/central) durch unterschiedliche Deploy-Strategien.
- Rollen- und Rechtekonzept für Dashboard-Benutzer.
