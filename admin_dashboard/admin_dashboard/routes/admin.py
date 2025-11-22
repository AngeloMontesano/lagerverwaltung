"""Admin dashboard UI routes."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..app import db
from ..docker_client import DockerClient
from ..instance_api import InstanceAPI
from ..models import Customer, Instance, MasterArticle, SyncLog

bp = Blueprint("admin", __name__)

docker_client = DockerClient()
instance_api = InstanceAPI()


@bp.route("/")
def dashboard():
    customers = Customer.query.all()
    return render_template("dashboard.html", customers=customers)


@bp.route("/customers/new", methods=["POST"])
def create_customer():
    customer = Customer(
        name=request.form.get("name"),
        customer_number=request.form.get("customer_number"),
        contact_email=request.form.get("contact_email"),
        hosting_mode=request.form.get("hosting_mode", "central"),
        plan=request.form.get("plan", "basic"),
    )
    db.session.add(customer)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@bp.route("/customers/<int:customer_id>")
def customer_detail(customer_id: int):
    customer = Customer.query.get_or_404(customer_id)
    return render_template("customer_detail.html", customer=customer)


@bp.route("/instances/new", methods=["POST"])
def create_instance():
    customer_id = int(request.form.get("customer_id"))
    instance = Instance(
        customer_id=customer_id,
        environment=request.form.get("environment", "prod"),
        version=request.form.get("version", "0.1.0"),
        technical_name=request.form.get("technical_name"),
        base_url=request.form.get("base_url"),
        api_base_url=request.form.get("api_base_url"),
        hosting_mode=request.form.get("hosting_mode", "central"),
        api_auth_token=request.form.get("api_auth_token"),
    )
    db.session.add(instance)
    db.session.commit()
    docker_client.deploy_instance(instance)
    return redirect(url_for("admin.customer_detail", customer_id=customer_id))


@bp.route("/instances/<int:instance_id>")
def instance_detail(instance_id: int):
    instance = Instance.query.get_or_404(instance_id)
    return render_template("instance_detail.html", instance=instance)


@bp.route("/instances/<int:instance_id>/health")
def health_check(instance_id: int):
    instance = Instance.query.get_or_404(instance_id)
    result = instance_api.call_health(instance)
    instance.last_health_status = result.get("status") if result else "unknown"
    instance.last_healthcheck_at = db.func.now()
    db.session.commit()
    flash("Healthcheck aktualisiert", "info")
    return redirect(url_for("admin.instance_detail", instance_id=instance_id))


@bp.route("/instances/<int:instance_id>/inventory")
def refresh_inventory(instance_id: int):
    instance = Instance.query.get_or_404(instance_id)
    summary = instance_api.call_inventory_summary(instance)
    instance.last_inventory_summary = summary
    db.session.commit()
    flash("Inventur-Kennzahlen aktualisiert", "info")
    return redirect(url_for("admin.instance_detail", instance_id=instance_id))


@bp.route("/instances/<int:instance_id>/start")
def start_instance(instance_id: int):
    instance = Instance.query.get_or_404(instance_id)
    docker_client.start_instance(instance)
    return redirect(url_for("admin.instance_detail", instance_id=instance_id))


@bp.route("/instances/<int:instance_id>/stop")
def stop_instance(instance_id: int):
    instance = Instance.query.get_or_404(instance_id)
    docker_client.stop_instance(instance)
    return redirect(url_for("admin.instance_detail", instance_id=instance_id))


@bp.route("/instances/<int:instance_id>/restart")
def restart_instance(instance_id: int):
    instance = Instance.query.get_or_404(instance_id)
    docker_client.restart_instance(instance)
    return redirect(url_for("admin.instance_detail", instance_id=instance_id))


@bp.route("/instances/<int:instance_id>/update", methods=["POST"])
def update_instance(instance_id: int):
    instance = Instance.query.get_or_404(instance_id)
    new_version = request.form.get("version", instance.version)
    docker_client.update_instance(instance, new_version)
    return redirect(url_for("admin.instance_detail", instance_id=instance_id))


@bp.route("/master-articles")
def master_articles():
    articles = MasterArticle.query.order_by(MasterArticle.sku).all()
    return render_template("master_articles.html", articles=articles)


@bp.route("/master-articles", methods=["POST"])
def create_master_article():
    article = MasterArticle(
        sku=request.form.get("sku"),
        name=request.form.get("name"),
        description=request.form.get("description"),
        default_uom=request.form.get("default_uom"),
    )
    db.session.add(article)
    db.session.commit()
    return redirect(url_for("admin.master_articles"))


@bp.route("/instances/<int:instance_id>/sync", methods=["POST"])
def sync_articles(instance_id: int):
    instance = Instance.query.get_or_404(instance_id)
    articles = [
        {"artikelnummer": a.sku, "name": a.name, "description": a.description}
        for a in MasterArticle.query.all()
    ]
    result = instance_api.sync_articles(instance, articles) or {}
    sync_log = SyncLog(
        instance_id=instance.id,
        payload_size=len(articles),
        created_count=result.get("created"),
        updated_count=result.get("updated"),
    )
    db.session.add(sync_log)
    db.session.commit()
    flash("Artikel synchronisiert", "info")
    return redirect(url_for("admin.instance_detail", instance_id=instance_id))
