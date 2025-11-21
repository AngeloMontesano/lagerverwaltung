# Admin Dashboard

Das Admin-Dashboard dient als Control Plane für die mehrmandantenfähige Lagersoftware. Es verwaltet Mandantenmetadaten, löst Deployments aus und fragt Gesundheitsinformationen der Instanzen ab.

## Lokaler Start

```bash
cd admin_dashboard
docker compose up -d --build
```

Standardmäßig nutzt die App eine SQLite-Datenbank im Volume `admin_data`. Per Umgebungsvariablen können Portainer/Compose-Pfade angepasst werden (siehe `docker-compose.yml`).

## Hauptfunktionen

- Mandanten anlegen (Code, Name, API-Key, Endpoint-URL)
- Deploy/Start einer Instanz via Docker Compose oder optional Portainer-API
- Stoppen/Herunterfahren laufender Instanzen
- Abruf der Health-Information einer Instanz über deren REST-API

## Architektur

- **Application Factory** in `admin_dashboard/app.py`
- **Modelle** in `admin_dashboard/models.py` (Tenant-Metadaten)
- **Routes** in `admin_dashboard/routes/admin.py`
- **Docker-Orchestrierung** über `docker_client.py`
- **Tenant-API-Client** in `instance_api.py`

Das Dashboard selbst speichert keine Lagerdaten, sondern nur Mandanten- und Lifecycle-Informationen.
