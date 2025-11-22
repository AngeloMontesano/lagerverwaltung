# Lagerverwaltung Platform

Dieses Repository enthält zwei voneinander getrennte Anwendungen:

1. **Lagersoftware (pro Kunde)** unter `lagersoftware/`
2. **Admin Dashboard (Control Plane)** unter `admin_dashboard/`

Jede Kundeninstanz der Lagersoftware läuft als eigenes Flask/Python-Paket mit eigener Datenbank. Das Admin Dashboard verwaltet Kunden, Instanzen und Stammdaten und kann über die bereitgestellten REST-APIs Healthchecks und Synchronisationen auslösen.

## Schnelleinstieg
- **Warehouse Instance**: siehe `lagersoftware/README.md` für Start, Konfiguration und REST-API.
- **Admin Dashboard**: siehe `admin_dashboard/README.md` für Betrieb, Docker Compose und Datenmodell.
- **Schema-Template**: Eine Beispiel-SQL-Datei für die grundlegende MariaDB-Struktur liegt unter `setup/templates/schema.sql`.

## Docker
Beide Anwendungen bringen eigene `Dockerfile` und `docker-compose.yml`-Vorlagen mit, um sie unabhängig voneinander deployen zu können. Jede Warehouse-Instanz erhält eine eigene Datenbank (z. B. MariaDB) und wird über `TENANT_ID`/`API_AUTH_TOKEN` eindeutig identifizierbar.
