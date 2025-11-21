#!/bin/bash

echo "🚀 Starte Docker Cleanup..."

# Zeige alle laufenden Container an
echo "📋 Aktuelle laufende Container:"
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}"

# Benutzer nach Container-Nummer fragen
read -p "❓ Welchen Container möchtest du löschen? (Nummer eingeben oder 'ALL' für alle Container): " CONTAINER_PATTERN

if [[ "$CONTAINER_PATTERN" == "ALL" ]]; then
    echo "🗑️ Lösche alle Container..."
    docker stop $(docker ps -q) 2>/dev/null
    docker rm $(docker ps -aq) 2>/dev/null
else
    # Finde alle Container mit dieser Nummer am Anfang
    MATCHING_CONTAINERS=$(docker ps --format "{{.Names}}" | grep "^$CONTAINER_PATTERN" || true)

    if [[ -z "$MATCHING_CONTAINERS" ]]; then
        echo "⚠️ Keine Container gefunden, die mit '$CONTAINER_PATTERN' beginnen!"
    else
        echo "🛑 Stoppe und lösche folgende Container:"
        echo "$MATCHING_CONTAINERS"

        # Container stoppen und löschen
        docker stop $MATCHING_CONTAINERS 2>/dev/null
        docker rm $MATCHING_CONTAINERS 2>/dev/null
    fi
fi

# Nachfragen, ob ungenutzte Images gelöscht werden sollen
read -p "❓ Möchtest du ungenutzte Docker-Images löschen? (y/n): " DELETE_IMAGES
if [[ "$DELETE_IMAGES" == "y" ]]; then
    echo "📦 Lösche ungenutzte Docker-Images..."
    docker image prune -a -f
fi

# Nachfragen, ob ungenutzte Volumes gelöscht werden sollen
read -p "❓ Möchtest du ungenutzte Docker-Volumes löschen? (y/n): " DELETE_VOLUMES
if [[ "$DELETE_VOLUMES" == "y" ]]; then
    echo "💾 Lösche ungenutzte Docker-Volumes..."
    docker volume prune -f
fi

# Nachfragen, ob ungenutzte Netzwerke gelöscht werden sollen
read -p "❓ Möchtest du ungenutzte Docker-Netzwerke löschen? (y/n): " DELETE_NETWORKS
if [[ "$DELETE_NETWORKS" == "y" ]]; then
    echo "🌐 Lösche ungenutzte Docker-Netzwerke..."
    docker network prune -f
fi

# Nachfragen, ob FS gelöscht werden soll
read -p "❓ Möchtest du Filesystem-Ordner löschen (y/n): " DELETE_Filesystem
if [[ "$DELETE_Filesystem" == "y" ]]; then
    echo "🌐 Lösche alte Ordner auf dem Filesystem..."
    rm -r "/volume1/docker/lagerverwaltung/$CONTAINER_PATTERN"
fi


echo "✅ Docker Cleanup abgeschlossen!"

