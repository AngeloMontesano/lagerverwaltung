FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY lagersoftware ./lagersoftware

ENV FLASK_APP=lagersoftware.app:create_app

CMD ["gunicorn", "-b", "0.0.0.0:5000", "lagersoftware.app:create_app()"]
