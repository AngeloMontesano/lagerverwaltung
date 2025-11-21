FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=admin_dashboard.app:create_app \
    DASHBOARD_DATABASE_URI=sqlite:////app/data/dashboard.db

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "admin_dashboard.app:create_app()"]
