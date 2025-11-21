#!/bin/bash

# Fehlerhandling aktivieren
set -e
trap 'echo "❌ Fehler in Zeile $LINENO aufgetreten. Bitte prüfen!"' ERR

# 🛠️ Basisverzeichnisse setzen
BASE="/volume1/docker/lagerverwaltung"
SETUP_DIR="$BASE/setup"
TEMPLATE_DIR="$SETUP_DIR/templates"
PROJECT_TEMPLATE="$TEMPLATE_DIR/lagerverwaltung"

# 🏗️ Containernamen abfragen oder als Argument übergeben
if [ -z "$1" ]; then
  read -p "Gib den gewünschten Containernamen ein (z. B. KundenNummer): " CONTAINER_NAME
else
  CONTAINER_NAME="$1"  # Kunden-ID als Argument verwenden
fi

# 📂 Verzeichnisse für den Container erstellen
CONTAINER_DIR="$BASE/kunden/$CONTAINER_NAME"
DB_DIR="$CONTAINER_DIR/mariadb"

echo "📂 Erstelle Verzeichnisse unter $CONTAINER_DIR..."
mkdir -p "$CONTAINER_DIR" "$DB_DIR"

# 📂 Überprüfung, ob die Projektvorlage existiert
if [ ! -d "$PROJECT_TEMPLATE" ]; then
  echo "❌ Fehler: Das Template-Projekt '$PROJECT_TEMPLATE' existiert nicht!"
  exit 1
fi

# 📂 Kopiere Projektvorlage (Flask-App)
echo "📂 Kopiere Projektvorlage nach $CONTAINER_DIR..."
cp -r "$PROJECT_TEMPLATE/" "$CONTAINER_DIR/"

# 📄 Kopiere Dockerfile-Template
echo "📄 Kopiere Dockerfile..."
cp "$TEMPLATE_DIR/Dockerfile" "$CONTAINER_DIR/Dockerfile"

# 📄 Kopiere requirements.txt
echo "📄 Kopiere requirements.txt..."
cp "$TEMPLATE_DIR/requirements.txt" "$CONTAINER_DIR/requirements.txt"

# 📄 Kopiere Schema.sql für MariaDB
echo "📄 Kopiere schema.sql..."
cp "$TEMPLATE_DIR/schema.sql" "$CONTAINER_DIR/schema.sql"

# 🔑 Setze Dateiberechtigungen
echo "🔑 Setze Dateiberechtigungen..."
chown -R $(id -u):$(id -g) "$CONTAINER_DIR/"
chmod -R 755 "$CONTAINER_DIR/"

# 🛠️ Funktion zur Suche nach freien Ports
find_free_ports() {
  local PORT=6000
  while true; do
    local NEXT_PORT=$((PORT + 1))
    if ! netstat -tuln | grep -q ":$PORT " && ! netstat -tuln | grep -q ":$NEXT_PORT "; then
      echo "$PORT $NEXT_PORT"
      return
    fi
    ((PORT+=2))
  done
}

read MARIA_PORT FLASK_PORT < <(find_free_ports)
echo "🔍 Freie Ports gefunden: MariaDB=$MARIA_PORT, Flask=$FLASK_PORT"

# 📄 Docker-Compose Datei erstellen
COMPOSE_FILE="$CONTAINER_DIR/docker-compose.yml"

echo "📄 Erstelle docker-compose.yml in $CONTAINER_DIR..."

cat <<EOF > "$COMPOSE_FILE"
version: "3.8"

services:
  ${CONTAINER_NAME}_mariadb:
    image: mariadb:latest
    container_name: ${CONTAINER_NAME}_mariadb
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: lagerdb
      MYSQL_USER: lageruser
      MYSQL_PASSWORD: lagerpass
    volumes:
      - "$DB_DIR:/var/lib/mysql"
    ports:
      - "$MARIA_PORT:3306"
    labels:
      com.portainer.accesscontrol: "public"
      com.portainer.container: "true"
      com.kunde.id: "${CONTAINER_NAME}"
      com.kunde.service: "mariadb"
    healthcheck:
      test: ["CMD", "mariadb", "-u", "root", "-prootpass", "-e", "SELECT 1;"]
      interval: 10s
      retries: 5
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

  ${CONTAINER_NAME}_flask:
    build: "$CONTAINER_DIR"
    container_name: ${CONTAINER_NAME}_flask
    restart: always
    ports:
      - "$FLASK_PORT:5000"
    depends_on:
      ${CONTAINER_NAME}_mariadb:
        condition: service_healthy  # Warten, bis MariaDB "healthy" ist
    environment:
      FLASK_ENV: production
      DATABASE_URL: mysql+pymysql://lageruser:lagerpass@${CONTAINER_NAME}_mariadb/lagerdb
    labels:
      com.portainer.accesscontrol: "public"
      com.portainer.container: "true"
      com.kunde.id: "${CONTAINER_NAME}"
      com.kunde.service: "flask"
    volumes:
      - "$CONTAINER_DIR/lagerverwaltung:/app"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000"]
      interval: 15s
      retries: 5
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

EOF

echo "✅ docker-compose.yml wurde erfolgreich erstellt in: $COMPOSE_FILE"

# 🚀 Starte den Docker-Compose-Stack
echo "🚀 Starte den Docker-Compose-Stack mit Containernamen: $CONTAINER_NAME..."
cd "$CONTAINER_DIR" || exit
docker-compose up -d ${CONTAINER_NAME}_mariadb  # Starte nur MariaDB zuerst

# 🕐 Warte auf MariaDB, bis ein Login funktioniert
echo "⏳ Warte auf MariaDB..."
until docker exec ${CONTAINER_NAME}_mariadb mariadb -u root -prootpass -e "SELECT 1;" &>/dev/null; do
    echo "⏳ MariaDB startet noch..."
    sleep 10
done

echo "✅ MariaDB ist bereit!"

# 🚀 Starte Flask-App, jetzt wo MariaDB verfügbar ist
docker-compose up -d ${CONTAINER_NAME}_flask
echo "✅ Flask-App wurde gestartet!"


# 🗣️ Warte, bis die Flask-App den Schema-Import durchgeführt hat
echo "⏳ Flask-App führt Schema-Import durch (falls erforderlich)..."
sleep 10  # Warte 10 Sekunden, um sicherzustellen, dass das Schema initialisiert wurde

echo "✅ Setup abgeschlossen! Lagerverwaltung läuft unter:"
echo "📌 MariaDB: http://<Synology-IP>:$MARIA_PORT"
echo "📌 Flask-App: http://<Synology-IP>:$FLASK_PORT"
