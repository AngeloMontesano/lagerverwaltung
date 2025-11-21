"""REST-API-Bereich mit API-Key-Authentifizierung."""
from functools import wraps
from typing import Callable
from flask import Blueprint, current_app, jsonify, request

from ..services import artikel_service, sync_service

bp = Blueprint("api", __name__, url_prefix="/api")


def require_api_key(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_app.config.get("API_ENABLED", True):
            return jsonify({"error": "API deaktiviert"}), 403
        provided = request.headers.get("X-API-Key") or request.headers.get("Authorization")
        if provided == current_app.config.get("API_KEY"):
            return func(*args, **kwargs)
        return jsonify({"error": "API-Schlüssel ungültig"}), 401

    return wrapper


@bp.route("/health")
@require_api_key
def health():
    return jsonify(
        {
            "status": "ok",
            "customer": current_app.config.get("CUSTOMER_CODE"),
            "version": current_app.config.get("APP_VERSION"),
        }
    )


@bp.route("/inventory/summary")
@require_api_key
def inventory_summary():
    return jsonify(artikel_service.get_inventory_summary())


@bp.route("/articles/bulk_upsert", methods=["POST"])
@require_api_key
def bulk_upsert_articles():
    data = request.get_json(silent=True) or []
    result = artikel_service.bulk_upsert(data)
    return jsonify(result)


@bp.route("/sync/master", methods=["POST"])
@require_api_key
def sync_master():
    payload = request.get_json(silent=True) or []
    result = sync_service.import_master_articles(payload)
    return jsonify(result)
