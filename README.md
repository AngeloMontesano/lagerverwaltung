# Lagerverwaltung – Multi-Tenant Plattform

Dieses Repository enthält zwei zusammengehörige Anwendungen:

1. **`lagersoftware/`** – die eigentliche Lager- und Inventur-App, die pro Mandant als eigene Instanz betrieben wird (eigene DB, eigener API-Key).
2. **`admin_dashboard/`** – ein Admin-Dashboard als Control Plane, das Mandanten verwaltet und Deployments/Health-Abfragen koordiniert.

Jede Mandanteninstanz wird über Docker Compose (oder optional Portainer) ausgerollt und besitzt eine eigene MariaDB-Datenbank. Alle konfigurierbaren Werte werden über Umgebungsvariablen gesteuert.

## Schnellstart

- Mandanten-App lokal: `cd lagersoftware && CUSTOMER_CODE=demo API_KEY=geheim docker compose up -d --build`
- Admin-Dashboard: `cd admin_dashboard && docker compose up -d --build`

## Struktur

- `lagersoftware/` – Flask-App mit Services, Routen und REST-API
- `admin_dashboard/` – Flask-App zur Verwaltung von Mandanten und Deployments
- `ARCHITECTURE.md` – detailierte Beschreibung der Module, APIs und Deployment-Strategie

Alle Dokumentationstexte sind bewusst kurz gehalten und auf Deutsch, um den operativen Betrieb zu erleichtern.
