from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from models import db, Artikel, Bestellung, Bestellposition
from sqlalchemy.sql import func

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@bp.route("/", methods=["GET"])
def dashboard_page():
    """
    Zeigt das Dashboard an.
    """
    gesamt_artikel = Artikel.query.count()
    kritische_artikel_liste = Artikel.query.filter(Artikel.bestand < Artikel.mindestbestand).all()
    bestellwuerdige_artikel_liste = Artikel.query.filter(
        Artikel.bestand < Artikel.sollbestand, Artikel.bestand >= Artikel.mindestbestand
    ).all()

    # Abrufen der bestellten Mengen
    bestell_mengen = (
        db.session.query(
            Bestellposition.artikel_id,
            func.sum(Bestellposition.menge).label("menge")
        )
        .join(Bestellung, Bestellung.id == Bestellposition.bestellung_id)
        .filter(Bestellung.status == "Offen")
        .group_by(Bestellposition.artikel_id)
        .all()
    )
    
    bestell_mengen_dict = {str(artikel_id): int(menge) for artikel_id, menge in bestell_mengen}

    for artikel in kritische_artikel_liste:
        artikel.bestellte_menge = bestell_mengen_dict.get(str(artikel.pf_artikel_id), 0)
    
    for artikel in bestellwuerdige_artikel_liste:
        artikel.bestellte_menge = bestell_mengen_dict.get(str(artikel.pf_artikel_id), 0)

    return render_template(
        "dashboard.html",
        gesamt_artikel=gesamt_artikel,
        kritische_artikel=len(kritische_artikel_liste),
        kritische_artikel_liste=kritische_artikel_liste,
        bestellwuerdige_artikel=len(bestellwuerdige_artikel_liste),
        bestellwuerdige_artikel_liste=bestellwuerdige_artikel_liste
    )


