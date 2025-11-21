# =============================================
# 🔹 Artikelverwaltung für die Lagerverwaltungs-App
# =============================================

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models import db, Artikel, Kategorie, Lagerort

# 🔹 Blueprint für die Artikelverwaltung
bp = Blueprint("artikel", __name__, url_prefix="/artikel")


# =============================================
# 🔹 HTML-Seite mit Artikeln laden
# =============================================
@bp.route("/", methods=["GET"])
def artikelverwaltung():
    """
    Zeigt die Artikelübersicht an.
    """
    artikel_liste = Artikel.query.order_by(Artikel.id.desc()).all()
    return render_template("artikel.html", artikel_liste=artikel_liste)


# =============================================
# 🔹 API: Alle Artikel als JSON abrufen (für `artikel.js`)
# =============================================
@bp.route("/api/artikel/", methods=["GET"])
def api_get_artikel():
    """
    Gibt alle Artikel als JSON zurück.
    """
    artikel_liste = Artikel.query.order_by(Artikel.id.desc()).all()
    return jsonify([{
        "id": a.id,
        "name": a.name,
        "ean": a.ean,
        "bestand": a.bestand,
        "mindestbestand": a.mindestbestand
    } for a in artikel_liste])


# =============================================
# 🔹 API: Einen Artikel per `PUT` aktualisieren
# =============================================
@bp.route("/api/artikel/<int:id>", methods=["PUT"])
def api_update_artikel(id):
    """
    Aktualisiert einen Artikel basierend auf der ID.
    """
    artikel = Artikel.query.get_or_404(id)
    data = request.get_json()

    artikel.name = data.get("name", artikel.name)
    artikel.ean = data.get("ean", artikel.ean)
    artikel.bestand = data.get("bestand", artikel.bestand)
    artikel.mindestbestand = data.get("mindestbestand", artikel.mindestbestand)

    db.session.commit()
    return jsonify({"message": "Artikel erfolgreich aktualisiert"}), 200


# =============================================
# 🔹 API: Einen neuen Artikel per `POST` hinzufügen
# =============================================
@bp.route("/api/artikel/", methods=["POST"])
def api_add_artikel():
    """
    Erstellt einen neuen Artikel.
    """
    data = request.get_json()

    neuer_artikel = Artikel(
        pf_artikel_id=f"ART-{Artikel.query.count() + 1}",
        name=data["name"],
        ean=data["ean"],
        kategorie=data.get("kategorie", "Unbekannt"),
        bestand=data.get("bestand", 0),
        mindestbestand=data.get("mindestbestand", 5),
        lagerort=data.get("lagerort", "Unbekannt"),
        preis=data.get("preis", 0.0)
    )

    db.session.add(neuer_artikel)
    db.session.commit()

    return jsonify({"message": "Artikel erfolgreich hinzugefügt", "id": neuer_artikel.id}), 201


# =============================================
# 🔹 API: Einen Artikel per `DELETE` entfernen
# =============================================
@bp.route("/api/artikel/<int:id>", methods=["DELETE"])
def api_delete_artikel(id):
    """
    Löscht einen Artikel anhand der ID.
    """
    artikel = Artikel.query.get_or_404(id)
    db.session.delete(artikel)
    db.session.commit()
    return jsonify({"message": "Artikel erfolgreich gelöscht"}), 200


# =============================================
# 🔹 API: Geänderte Artikel speichern
# =============================================
@bp.route("/save_all", methods=["POST"])
def save_all():
    """
    Speichert nur die geänderten Artikel und stellt sicher, dass alle Werte korrekt gespeichert werden.
    """
    try:
        print("🚀 save_all wurde aufgerufen!")  # Debugging für Terminal
        print("\n🔹 Empfangene Formulardaten:", request.form)  # Debugging

        changed_articles = {}
        updated_count = 0

        for key, value in request.form.items():
            # Prüfen, ob der Key ein Feld aus der Datenbank ist
            if "_" in key:  
                field_name = key.split("_")[0]  # Entfernt die Artikel-ID vom Feldnamen
                pf_artikel_id = request.form.get("pf_artikel_id")

                if not pf_artikel_id:
                    continue  

                if pf_artikel_id not in changed_articles:
                    changed_articles[pf_artikel_id] = {}

                changed_articles[pf_artikel_id][field_name] = value.strip()

        print(f"🛠️ Geänderte Artikel: {changed_articles}")

        if not changed_articles:
            return jsonify({"message": "Keine Änderungen vorhanden."}), 200

        for pf_artikel_id, changes in changed_articles.items():
            artikel = Artikel.query.filter_by(pf_artikel_id=pf_artikel_id).first()
            if not artikel:
                print(f"⚠️ WARNUNG: Artikel {pf_artikel_id} nicht gefunden!")
                continue  

            # Änderungen auf das richtige Datenbank-Objekt anwenden
            for key, value in changes.items():
                if hasattr(artikel, key):  
                    setattr(artikel, key, value)
                    print(f"✅ Artikel {pf_artikel_id}: {key} → {value}")
                else:
                    print(f"⚠️ WARNUNG: Artikel {pf_artikel_id} hat kein Feld {key}!")

            updated_count += 1

        db.session.commit()
        print(f"✅ {updated_count} Artikel wurden aktualisiert.")

        return jsonify({"message": f"{updated_count} Artikel gespeichert"}), 200

    except Exception as e:
        print("❌ Fehler beim Speichern:", str(e))
        return jsonify({"error": f"Fehler beim Speichern: {str(e)}"}), 500
