# Produktionsfähiges Python-Image
FROM python:3.10

# Arbeitsverzeichnis im Container
WORKDIR /app

# Requirements zuerst kopieren (bessere Layer-Caches)
COPY requirements.txt .

# Python-Abhängigkeiten installieren
RUN pip install --no-cache-dir -r requirements.txt

# Jetzt den restlichen Code ins Image kopieren
COPY . .

# Sinnvolle Environment-Variablen
ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# Port-Deklaration (Dokumentation für Docker/Portainer)
EXPOSE 5000

# Start der App über Gunicorn
# lagerverwaltung.wsgi:app -> Paket "lagerverwaltung", Modul "wsgi", Variable "app"
CMD ["gunicorn", "-b", "0.0.0.0:5000", "lagerverwaltung.wsgi:app", "--workers", "4"]
