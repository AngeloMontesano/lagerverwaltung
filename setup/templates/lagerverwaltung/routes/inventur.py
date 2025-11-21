from flask import Blueprint, render_template, request, jsonify, send_file
from models import db, Artikel
from openpyxl import Workbook
import csv
import os
from datetime import datetime, date

bp = Blueprint("inventur", __name__, url_prefix="/inventur")

@bp.route("/", methods=["GET"])
def inventurseite():
    """
    Zeigt die Inventur-Tabelle an.
    """
    artikel_liste = Artikel.query.order_by(Artikel.id).all()
    return render_template("inventur.html", artikel_liste=artikel_liste, now=datetime.now)



@bp.route("/export", methods=["GET"])
def export_csv():
    """
    Exportiert die Inventur als Excel-Datei.
    """
    filename = "/tmp/inventur.xlsx"
    
    # Excel-Datei erstellen
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventur"
    
    # Spaltenüberschriften definieren
    ws.append(["Artikel-ID", "Name", "Barcode", "Kategorie", "Soll", "Min", "Bestand"])

    # Artikeldaten hinzufügen
    for artikel in Artikel.query.all():
        ws.append([
            artikel.pf_artikel_id, artikel.name, artikel.ean, artikel.kategorie,
            artikel.bestand, artikel.sollbestand, artikel.mindestbestand
        ])
    
    # Excel-Datei speichern
    wb.save(filename)
    
    # Die Excel-Datei als Download anbieten
    return send_file(filename, as_attachment=True, download_name="inventur.xlsx")
    
@bp.route("/save_all", methods=["POST"])
def save_all():
    try:
        data = request.get_json()
        print("🚀 Empfangene Daten:", data)

        changed_articles = {}
        updated_count = 0

        for update in data.get("updates", []):
            print(f"🔄 Prüfe Update: {update}")

            artikel_id = update["id"]
            artikel = Artikel.query.filter_by(pf_artikel_id=artikel_id).first()

            if not artikel:
                print(f"⚠️ WARNUNG: Artikel mit ID {artikel_id} nicht gefunden!")
                continue

            artikel.bestand = update["bestand"]
            db.session.commit()
            updated_count += 1

        return jsonify({"message": f"{updated_count} Artikel gespeichert"}), 200

    except Exception as e:
        print("❌ Fehler beim Speichern:", str(e))
        return jsonify({"error": f"Fehler beim Speichern: {str(e)}"}), 500
