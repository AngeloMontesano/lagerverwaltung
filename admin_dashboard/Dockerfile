FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY admin_dashboard ./admin_dashboard

ENV FLASK_APP=admin_dashboard.app:create_app

CMD ["gunicorn", "-b", "0.0.0.0:8000", "admin_dashboard.app:create_app()"]
