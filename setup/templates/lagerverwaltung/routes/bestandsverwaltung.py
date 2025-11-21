# lagerverwaltung/routes/bestandsverwaltung.py
from flask import Blueprint, render_template, request, jsonify
from models import db, Artikel, Lagerbewegung

bp = Blueprint("bestandsverwaltung", __name__, url_prefix="/bestandsverwaltung")

@bp.route("/", methods=["GET"])
def bestandsseite():
    """
    Zeigt die Bestandsverwaltung mit allen Lagerbewegungen an.
    """
    lagerbewegungen = Lagerbewegung.query.order_by(Lagerbewegung.zeit.desc()).limit(20).all()
    return render_template("bestandsverwaltung.html", lagerbewegungen=lagerbewegungen)

@bp.route("/entnahme", methods=["POST"])
def bestand_entnahme():
    """
    Reduziert den Bestand eines Artikels basierend auf einem Barcode-Scan.
    Erwartet eine JSON-Anfrage mit `barcode`.
    """
    if request.content_type != "application/json":
        return jsonify({"error": "Unsupported Media Type: JSON erforderlich"}), 415

    try:
        data = request.get_json(force=True)  # `force=True` erlaubt JSON auch ohne Content-Type Header
        if not data or "barcode" not in data:
            return jsonify({"error": "Kein Barcode erhalten"}), 400

        barcode = data["barcode"]
        artikel = Artikel.query.filter_by(ean=barcode).first()

        if not artikel:
            return jsonify({"error": "Artikel nicht gefunden"}), 404

        artikel.bestand = max(artikel.bestand - 1, 0)
        db.session.commit()

        neue_bewegung = Lagerbewegung(artikel_id=artikel.id, typ="Entnahme", menge=1)
        db.session.add(neue_bewegung)
        db.session.commit()

        return jsonify({
            "message": "Bestand reduziert",
            "artikel": artikel.name,
            "ean": artikel.ean,
            "pf_artikel_id": artikel.pf_artikel_id,
            "typ": "Entnahme"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server-Fehler: {str(e)}"}), 500

@bp.route("/zugang", methods=["POST"])
def bestand_zugang():
    """
    Erhöht den Bestand eines Artikels beim Wareneingang.
    Erwartet eine JSON-Anfrage mit `barcode`.
    """
    if request.content_type != "application/json":
        return jsonify({"error": "Unsupported Media Type: JSON erforderlich"}), 415

    try:
        data = request.get_json(force=True)
        if not data or "barcode" not in data:
            return jsonify({"error": "Kein Barcode erhalten"}), 400

        barcode = data["barcode"]
        artikel = Artikel.query.filter_by(ean=barcode).first()

        if not artikel:
            return jsonify({"error": "Artikel nicht gefunden"}), 404

        artikel.bestand += 1
        db.session.commit()

        neue_bewegung = Lagerbewegung(artikel_id=artikel.id, typ="Zugang", menge=1)
        db.session.add(neue_bewegung)
        db.session.commit()

        return jsonify({
            "message": "Bestand erhöht",
            "artikel": artikel.name,
            "ean": artikel.ean,
            "pf_artikel_id": artikel.pf_artikel_id,
            "typ": "Zugang"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server-Fehler: {str(e)}"}), 500
