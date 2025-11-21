"""Settings routes."""
from __future__ import annotations

from flask import Blueprint, current_app, render_template

bp = Blueprint("einstellungen", __name__, url_prefix="/einstellungen")


@bp.route("/")
def view():
    config = {
        "TENANT_ID": current_app.config.get("TENANT_ID"),
        "ENVIRONMENT": current_app.config.get("ENVIRONMENT"),
        "APP_VERSION": current_app.config.get("APP_VERSION"),
    }
    return render_template("einstellungen/view.html", config=config)
