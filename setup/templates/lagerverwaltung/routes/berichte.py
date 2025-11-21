# =============================================
# 🔹 Berichtsmodul für die Lagerverwaltungs-App
# =============================================

from flask import Blueprint, render_template, jsonify, send_file, request
from models import db, Artikel, Verbrauch
import csv
import pandas as pd
import os
import matplotlib.pyplot as plt
from sqlalchemy import text
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas

# 🔹 Blueprint für Berichte
bp = Blueprint("berichte", __name__, url_prefix="/berichte")


# =============================================
# 🔹 Dashboard-Seite für Verbrauchsstatistik
# =============================================
@bp.route("/", methods=["GET"])
def berichte_dashboard():
    """
    Zeigt das Dashboard mit Verbrauchsstatistik an.
    """
    verbrauchsdaten = Verbrauch.query.order_by(Verbrauch.monat.desc()).all()
    artikel_liste = Artikel.query.all()
    return render_template("berichte.html", verbrauchsdaten=verbrauchsdaten, artikel_liste=artikel_liste)


# =============================================
# 🔹 Verbrauchsdaten abrufen
# =============================================
@bp.route("/daten", methods=["GET"])
def get_verbrauchsdaten():
    """
    Berechnet den Verbrauch pro Artikel und Monat aus der Tabelle `lagerbewegung`.
    """
    query = text("""
        SELECT a.name AS artikel, DATE_FORMAT(l.zeit, '%Y-%m') AS monat, 
               SUM(CASE WHEN l.typ = 'Entnahme' THEN l.menge ELSE 0 END) AS verbrauch
        FROM lagerbewegung l
        JOIN artikel a ON l.artikel_id = a.id
        GROUP BY monat, artikel
        ORDER BY monat DESC;
    """)

    result = db.session.execute(query).fetchall()

    daten = [
        {"artikel": row[0], "monat": row[1], "verbrauch": row[2] or 0}  # Falls NULL, dann 0 setzen
        for row in result
    ]
    return jsonify(daten)


# =============================================
# 🔹 CSV-Export
# =============================================
@bp.route("/export/csv", methods=["GET"])
def export_csv():
    """
    Exportiert die Verbrauchsdaten als CSV-Datei.
    """
    query = text("""
        SELECT a.name AS artikel, DATE_FORMAT(l.zeit, '%Y-%m') AS monat, 
               SUM(CASE WHEN l.typ = 'Entnahme' THEN l.menge ELSE 0 END) AS verbrauch
        FROM lagerbewegung l
        JOIN artikel a ON l.artikel_id = a.id
        GROUP BY monat, artikel
        ORDER BY monat DESC;
    """)
    result = db.session.execute(query).fetchall()

    filename = "/tmp/verbrauch.csv"
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Artikel", "Monat", "Verbrauch"])
        for row in result:
            writer.writerow([row[0], row[1], row[2]])

    return send_file(filename, as_attachment=True, download_name="verbrauch.csv")


# =============================================
# 🔹 Excel-Export
# =============================================
@bp.route("/export/excel", methods=["GET"])
def export_excel():
    """
    Exportiert die Verbrauchsdaten als Excel-Datei (.xlsx).
    """
    query = text("""
        SELECT a.name AS artikel, DATE_FORMAT(l.zeit, '%Y-%m') AS monat, 
               SUM(CASE WHEN l.typ = 'Entnahme' THEN l.menge ELSE 0 END) AS verbrauch
        FROM lagerbewegung l
        JOIN artikel a ON l.artikel_id = a.id
        GROUP BY monat, artikel
        ORDER BY monat DESC;
    """)
    result = db.session.execute(query).fetchall()

    df = pd.DataFrame(result, columns=["Artikel", "Monat", "Verbrauch"])
    excel_path = "/tmp/verbrauch.xlsx"
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True, download_name="verbrauch.xlsx")


# =============================================
# 🔹 PDF-Export mit Verbrauchsanalyse und Trendanalyse
# =============================================
@bp.route("/export/pdf", methods=["GET"])
def export_pdf():
    """
    Exportiert die Verbrauchsdaten als PDF mit nur den ausgewählten Artikeln.
    """
    # 🔹 Artikel und Zeitraum aus URL-Parametern abrufen
    artikel_param = request.args.get("artikel", "")
    start_date = request.args.get("start", "2000-01")
    end_date = request.args.get("end", "2100-12")

    artikel_list = artikel_param.split(",") if artikel_param else []

    # 🔹 SQL-Abfrage für den ausgewählten Zeitraum und Artikel
    query = text("""
        SELECT a.name AS artikel, DATE_FORMAT(l.zeit, '%Y-%m') AS monat, 
               SUM(CASE WHEN l.typ = 'Entnahme' THEN l.menge ELSE 0 END) AS verbrauch
        FROM lagerbewegung l
        JOIN artikel a ON l.artikel_id = a.id
        WHERE DATE_FORMAT(l.zeit, '%Y-%m') BETWEEN :start_date AND :end_date
        """ + (" AND a.name IN :artikel_list" if artikel_list else "") + """
        GROUP BY monat, artikel
        ORDER BY monat ASC;
    """)

    params = {"start_date": start_date, "end_date": end_date}
    if artikel_list:
        params["artikel_list"] = tuple(artikel_list)

    result = db.session.execute(query, params).fetchall()
    df = pd.DataFrame(result, columns=["Artikel", "Monat", "Verbrauch"])

    # 🔹 Falls keine Daten vorhanden sind → PDF mit "Keine Daten verfügbar"
    pdf_path = "/tmp/verbrauchsbericht.pdf"
    c = canvas.Canvas(pdf_path, pagesize=landscape(letter))

    if df.empty:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(250, 550, "Keine Daten für die ausgewählten Artikel!")
        c.save()
        return send_file(pdf_path, as_attachment=True, download_name="verbrauchsbericht.pdf")

    # 🔹 Diagramme erstellen
    artikel_unique = df["Artikel"].unique()

    # 📊 Verbrauchsanalyse
    plt.figure(figsize=(11, 5))
    for artikel in artikel_unique:
        artikel_df = df[df["Artikel"] == artikel]
        plt.bar(artikel_df["Monat"], artikel_df["Verbrauch"], label=artikel)

    plt.xticks(rotation=90)
    plt.xlabel("Monat")
    plt.ylabel("Verbrauch")
    plt.title("Verbrauchsanalyse")
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=4, fontsize=8)

    pdf_chart_path1 = "/tmp/verbrauch_chart.png"
    plt.savefig(pdf_chart_path1, bbox_inches="tight")
    plt.close()

    c.drawImage(pdf_chart_path1, 50, 200, width=700, height=300)
    c.showPage()

    # 📈 Trendanalyse
    c.setFont("Helvetica-Bold", 16)
    c.drawString(250, 550, "Trendanalyse")

    plt.figure(figsize=(11, 5))
    for artikel in artikel_unique:
        artikel_df = df[df["Artikel"] == artikel]
        plt.plot(artikel_df["Monat"], artikel_df["Verbrauch"], label=artikel)

    plt.xticks(rotation=90)
    plt.xlabel("Monat")
    plt.ylabel("Verbrauch")
    plt.title("Trendanalyse")
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=4, fontsize=8)

    pdf_chart_path2 = "/tmp/trend_chart.png"
    plt.savefig(pdf_chart_path2, bbox_inches="tight")
    plt.close()

    c.drawImage(pdf_chart_path2, 50, 200, width=700, height=300)
    
    c.save()
    return send_file(pdf_path, as_attachment=True, download_name="verbrauchsbericht.pdf")
