FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=admin_dashboard.app:create_app
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "admin_dashboard.app:create_app()"]
