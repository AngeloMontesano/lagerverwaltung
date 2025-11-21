"""REST API endpoints for admin dashboard integration."""
from __future__ import annotations

from functools import wraps

from flask import Blueprint, current_app, jsonify, request

from ..services import bestands_service, sync_service

bp = Blueprint("api", __name__, url_prefix="/api")


def require_api_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        expected = current_app.config.get("API_AUTH_TOKEN")
        token = request.headers.get("X-API-TOKEN")
        if expected and token != expected:
            return jsonify({"error": "unauthorized"}), 401
        return func(*args, **kwargs)

    return wrapper


@bp.route("/health")
@require_api_token
def health():
    status = {
        "status": "ok",
        "version": current_app.config.get("APP_VERSION"),
        "tenant_id": current_app.config.get("TENANT_ID"),
        "environment": current_app.config.get("ENVIRONMENT"),
    }
    return jsonify(status)


@bp.route("/inventory/summary")
@require_api_token
def inventory_summary():
    summary = bestands_service.inventory_summary()
    return jsonify(summary)


@bp.route("/articles/bulk_upsert", methods=["POST"])
@require_api_token
def bulk_upsert_articles():
    data = request.get_json(silent=True) or {}
    articles = data.get("articles", [])
    result = sync_service.bulk_upsert_articles(articles)
    return jsonify(result)


@bp.route("/heartbeat", methods=["POST"])
@require_api_token
def heartbeat():
    payload = request.get_json(silent=True) or {}
    response = {
        "received": True,
        "tenant_id": current_app.config.get("TENANT_ID"),
        "version": current_app.config.get("APP_VERSION"),
        "payload": payload,
    }
    return jsonify(response)
