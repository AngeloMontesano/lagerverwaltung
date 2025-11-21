"""Web routes for the admin dashboard."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..docker_client import DockerClient
from ..models import Customer, Instance, db
from ..tenant_db import check_connection, get_basic_inventory_stats

admin_bp = Blueprint("admin", __name__)

docker_client = DockerClient()


@admin_bp.route("/")
def dashboard():
    customers = Customer.query.order_by(Customer.name).all()
    return render_template("dashboard.html", customers=customers)


@admin_bp.route("/instance/<int:instance_id>", methods=["GET", "POST"])
def instance_detail(instance_id: int):
    instance = Instance.query.get_or_404(instance_id)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "start":
            docker_client.start_instance(instance)
            flash("Instanz gestartet", "success")
        elif action == "stop":
            docker_client.stop_instance(instance)
            flash("Instanz gestoppt", "info")
        elif action == "restart":
            docker_client.restart_instance(instance)
            flash("Instanz neu gestartet", "success")
        elif action == "update":
            new_version = request.form.get("version") or instance.version
            docker_client.update_instance(instance, new_version)
            flash(f"Update auf Version {new_version} angestoßen", "info")
        return redirect(url_for("admin.instance_detail", instance_id=instance.id))

    db_ok = check_connection(instance.db_url)
    stats = get_basic_inventory_stats(instance.db_url) if db_ok else None
    return render_template(
        "instance_detail.html",
        instance=instance,
        db_ok=db_ok,
        stats=stats,
    )
