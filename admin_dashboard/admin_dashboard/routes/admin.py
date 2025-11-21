"""Routen für das zentrale Admin-Dashboard."""
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from ..docker_client import TenantOrchestrator
from ..instance_api import InstanceApiClient
from ..models import Tenant, db

bp = Blueprint("admin", __name__)


def _orchestrator() -> TenantOrchestrator:
    return TenantOrchestrator(
        template_path=current_app.config["TENANT_TEMPLATE_PATH"],
        portainer_url=current_app.config.get("PORTAINER_URL"),
        token=current_app.config.get("PORTAINER_TOKEN"),
    )


@bp.route("/")
def index():
    tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    stats = {}
    for tenant in tenants:
        if tenant.endpoint_url:
            try:
                client = InstanceApiClient(tenant.endpoint_url, tenant.api_key)
                stats[tenant.code] = client.health()
            except Exception:  # pragma: no cover - Netzwerkabhängigkeit
                stats[tenant.code] = {"status": "unbekannt"}
    return render_template("dashboard/index.html", tenants=tenants, stats=stats)


@bp.route("/tenants/new", methods=["GET", "POST"])
def create_tenant():
    if request.method == "POST":
        code = request.form["code"].lower()
        tenant = Tenant(
            name=request.form["name"],
            code=code,
            api_key=request.form.get("api_key") or current_app.config["DEFAULT_API_KEY"],
            endpoint_url=request.form.get("endpoint_url", "http://localhost:5000"),
        )
        db.session.add(tenant)
        db.session.commit()
        flash("Mandant angelegt", "success")
        return redirect(url_for("admin.index"))
    return render_template("tenants/new.html")


@bp.route("/tenants/<code>/deploy", methods=["POST"])
def deploy(code: str):
    tenant = Tenant.query.filter_by(code=code).first_or_404()
    orchestrator = _orchestrator()
    result = orchestrator.deploy(code=tenant.code, api_key=tenant.api_key)
    tenant.status = "running" if result.success else "error"
    db.session.commit()
    flash(result.message, "success" if result.success else "danger")
    return redirect(url_for("admin.index"))


@bp.route("/tenants/<code>/stop", methods=["POST"])
def stop(code: str):
    tenant = Tenant.query.filter_by(code=code).first_or_404()
    orchestrator = _orchestrator()
    result = orchestrator.stop(code=tenant.code)
    tenant.status = "stopped" if result.success else tenant.status
    db.session.commit()
    flash(result.message, "success" if result.success else "danger")
    return redirect(url_for("admin.index"))
