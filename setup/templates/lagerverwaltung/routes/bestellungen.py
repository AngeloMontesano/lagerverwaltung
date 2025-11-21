from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, send_from_directory, abort
from models import db, Artikel, Bestellung, Kunde, Administratives, Bestellposition
import os
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.message import EmailMessage
import json
from datetime import datetime
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func

smtp_path = os.path.join("scripts", "smtp.json")

try:
    with open(smtp_path, "r") as file:
        config = json.load(file)
    print("✅ SMTP-Config geladen:", config)
except FileNotFoundError:
    print(f"❌ Datei nicht gefunden: {smtp_path}")
except json.JSONDecodeError as e:
    print(f"❌ Fehler beim Parsen der JSON-Datei: {e}")
except Exception as e:
    print(f"❌ Unbekannter Fehler beim Laden von smtp.json: {e}")


bp = Blueprint("bestellungen", __name__, url_prefix="/bestellungen")

def generate_order_number():
    """Erstellt eine eindeutige Bestellnummer."""
    return "ORDER-" + str(uuid.uuid4())[:8]  # Kürzt die UUID auf 8 Zeichen

@bp.route("/", methods=["GET"])
def bestellung_uebersicht():
    """
    Zeigt eine Übersicht der zu bestellenden Artikel und Bestellungen an.
    """

    # Abrufen aller Artikel mit niedrigem Bestand
    artikel_liste = Artikel.query.filter(Artikel.bestand < Artikel.sollbestand).all()
    alle_artikel = Artikel.query.all()  # Alle Artikel für das Dropdown-Menü

    # Abrufen aller offenen Bestellungen
    offene_bestellungen = Bestellung.query.filter_by(status="Offen").all()
    erledigte_bestellungen = Bestellung.query.filter_by(status="Erledigt").all()

    # Bestellungen gruppieren
    gruppierte_bestellungen = {}
    for bestellung in offene_bestellungen:
        if bestellung.bestellnummer not in gruppierte_bestellungen:
            gruppierte_bestellungen[bestellung.bestellnummer] = {
                "bestellung_id": bestellung.id,
                "datum": bestellung.bestelldatum.strftime("%Y-%m-%d") if bestellung.bestelldatum else "Unbekannt",
                "status": bestellung.status,
                "artikel": []
            }

        for position in bestellung.positionen:
            if position.artikel:
                gruppierte_bestellungen[bestellung.bestellnummer]["artikel"].append({
                    "artikel_id": position.artikel.pf_artikel_id,
                    "name": position.artikel.name,
                    "menge": position.menge
                })

    # Erledigte Bestellungen gruppieren
    erledigte_gruppierte_bestellungen = {}
    for bestellung in erledigte_bestellungen:
        if bestellung.bestellnummer not in erledigte_gruppierte_bestellungen:
            erledigte_gruppierte_bestellungen[bestellung.bestellnummer] = {
                "bestellung_id": bestellung.id,
                "datum": bestellung.bestelldatum.strftime("%Y-%m-%d") if bestellung.bestelldatum else "Unbekannt",
                "status": bestellung.status,
                "artikel": []
            }

        for position in bestellung.positionen:
            if position.artikel:
                erledigte_gruppierte_bestellungen[bestellung.bestellnummer]["artikel"].append({
                    "artikel_id": position.artikel.pf_artikel_id,
                    "name": position.artikel.name,
                    "menge": position.menge
                })

    # Nur Artikel abrufen, die unter ihrem Sollbestand liegen
    artikel_liste = Artikel.query.filter(Artikel.bestand < Artikel.sollbestand).all()

   # Ermitteln der bestellten Menge für jeden Artikel aus offenen Bestellungen
    bestell_mengen = (
        db.session.query(
            Bestellposition.artikel_id,
            func.sum(Bestellposition.menge).label("menge"),
            Bestellung.bestellnummer
        )
        .join(Bestellung, Bestellung.id == Bestellposition.bestellung_id)
        .filter(Bestellung.status == "Offen")
        .group_by(Bestellposition.artikel_id, Bestellung.bestellnummer)
        .all()
    )

    # Konvertieren der Daten in ein Dictionary
    bestell_mengen_dict = {}
    for artikel_id, menge, bestellnummer in bestell_mengen:
        bestell_mengen_dict[artikel_id] = {
            "menge": menge,
            "bestellnummer": bestellnummer
        }

    # Artikel-Liste mit bestellten Mengen erweitern
    for artikel in artikel_liste:
        artikel.bestellte_menge = bestell_mengen_dict.get(artikel.pf_artikel_id, {}).get("menge", 0)
        artikel.bestellnummer = bestell_mengen_dict.get(artikel.pf_artikel_id, {}).get("bestellnummer", None)

    return render_template(
        "bestellungen.html",
        artikel_liste=artikel_liste,
        alle_artikel=alle_artikel,
        gruppierte_bestellungen=gruppierte_bestellungen,
        erledigte_bestellungen=erledigte_gruppierte_bestellungen
    )

@bp.route("/select_artikel/<int:artikel_id>", methods=["GET"])
def select_artikel(artikel_id):
    """
    Gibt die Details eines Artikels zurück, wenn er ausgewählt wurde.
    """
    artikel = Artikel.query.get(artikel_id)
    if artikel:
        return jsonify({
            'id': artikel.pf_artikel_id,
            'name': artikel.name,
            'kategorie': artikel.kategorie,
            'bestand': artikel.bestand,
            'sollbestand': artikel.sollbestand
        })
    return jsonify({'error': 'Artikel nicht gefunden'}), 404


def load_smtp_config():
    """Lädt die SMTP-Konfiguration aus 'scripts/smtp.json'."""
    smtp_path = os.path.join("scripts", "smtp.json")  # Hier "scripts" verwenden
    
    try:
        with open(smtp_path, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"❌ Datei nicht gefunden: {smtp_path}")
    except json.JSONDecodeError as e:
        print(f"❌ Fehler beim Parsen der JSON-Datei: {e}")
    except Exception as e:
        print(f"❌ Unbekannter Fehler beim Laden von smtp.json: {e}")
    
    return None  # Falls das JSON fehlt oder fehlerhaft ist
    
def send_order_email(kunde, pdf_path, bestellnummer, email_empfaenger, email_cc):
    """
    Versendet die Bestell-PDF per E-Mail mit funktionierendem CC.
    """
    smtp_config = load_smtp_config()
    if not smtp_config:
        print("❌ SMTP-Konfiguration konnte nicht geladen werden. E-Mail wird nicht gesendet.")
        return

    EMAIL_ABSENDER = smtp_config["EMAIL_ABSENDER"]
    EMAIL_PASSWORT = smtp_config["EMAIL_PASSWORT"]
    SMTP_SERVER = smtp_config["SMTP_SERVER"]
    SMTP_PORT = smtp_config["SMTP_PORT"]

    msg = EmailMessage()
    msg["Subject"] = f"Bestellung {bestellnummer} - {kunde.name}"
    msg["From"] = EMAIL_ABSENDER

    # ✅ Hauptempfänger setzen
    recipients = [email_empfaenger]  
    msg["To"] = email_empfaenger  

    # ✅ CC-Empfänger in die Empfängerliste & in die Anzeige setzen
    if email_cc:
        msg["CC"] = email_cc  # **Nur Anzeige**
        recipients.append(email_cc)  # **Sorgt dafür, dass die CC-Adresse auch die E-Mail bekommt!**

    msg.set_content(f"""
    Hallo {kunde.name},

    hier ist die Bestellung {bestellnummer}.

    Adresse:
    {kunde.adresse_str}, {kunde.adresse_plz} {kunde.adresse_ort}
    Kontakt: {kunde.email} | {kunde.tel}

    Die PDF ist als Anhang beigefügt.

    Viele Grüße
    Pfersich Flow
    """)

    # 📎 PDF-Anhang hinzufügen
    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ABSENDER, EMAIL_PASSWORT)

            # ✅ Hier wird sichergestellt, dass die CC-Adresse wirklich als Empfänger übergeben wird!
            server.send_message(msg, to_addrs=recipients)

        print(f"✅ E-Mail erfolgreich gesendet an: {', '.join(recipients)}")
    except Exception as e:
        print(f"❌ Fehler beim Senden der E-Mail: {str(e)}")


@bp.route("/stornieren", methods=["POST"])
def bestellung_stornieren():
    """
    Markiert eine Bestellung als 'Storniert'
    """
    bestellung_id = request.form.get("bestellung_id")
    if not bestellung_id:
        return "Fehler: Keine Bestellungs-ID angegeben", 400

    bestellung = Bestellung.query.get(bestellung_id)
    if not bestellung:
        return "Fehler: Bestellung nicht gefunden", 404

    bestellung.status = "Storniert"
    db.session.commit()
    
    return "Bestellung storniert", 200


@bp.route("/erledigt", methods=["POST"])
def bestellung_erledigt():
    """
    Markiert eine Bestellung als 'Erledigt', aktualisiert die Bestandswerte und verschiebt sie in die Erledigten-Liste.
    """
    bestellung_id = request.form.get("bestellung_id")
    if not bestellung_id:
        return jsonify({"error": "Keine Bestellungs-ID angegeben"}), 400

    bestellung = Bestellung.query.get(bestellung_id)
    if not bestellung:
        return jsonify({"error": "Bestellung nicht gefunden"}), 404

    # 🔹 Bestellpositionen abrufen
    bestellpositionen = Bestellposition.query.filter_by(bestellung_id=bestellung.id).all()

    # 🔹 Bestand der Artikel aktualisieren
    for pos in bestellpositionen:
        artikel = Artikel.query.filter_by(pf_artikel_id=pos.artikel_id).first()
        if artikel:
            artikel.bestand += pos.menge
            db.session.add(artikel)

    # 🔹 Bestellung als "Erledigt" markieren
    bestellung.status = "Erledigt"
    db.session.commit()

    flash(f"✅ Bestellung {bestellung.bestellnummer} wurde erfolgreich erledigt!", "success")
    return jsonify({"success": True, "message": "Bestellung als erledigt markiert"}), 200

@bp.route("/artikel_entfernen", methods=["POST"])
def artikel_entfernen():
    """
    Entfernt einen Artikel aus der Bestellübersicht (nicht aus der Datenbank).
    """
    artikel_id = request.form.get("artikel_id")

    if not artikel_id:
        return jsonify({"status": "error", "message": "Artikel-ID fehlt"}), 400

    artikel = Artikel.query.filter_by(pf_artikel_id=artikel_id).first()
    if not artikel:
        return jsonify({"status": "error", "message": "Artikel nicht gefunden"}), 404

    return jsonify({"status": "success", "message": "Artikel wurde entfernt"})


@bp.route("/api/artikel/", methods=["GET"])
def alle_artikel():
    artikel_liste = Artikel.query.all()
    return jsonify([{
        "id": artikel.pf_artikel_id,
        "name": artikel.name,
        "kategorie": artikel.kategorie,
        "bestand": artikel.bestand,
        "sollbestand": artikel.sollbestand
    } for artikel in artikel_liste])
    
    
def create_order_pdf(bestellnummer, kunde, artikel_daten):
    """
    Erstellt eine Bestell-PDF mit allen relevanten Daten.
    """
    import os
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    pdf_filename = f"bestellung_{bestellnummer}.pdf"
    pdf_path = os.path.join("pdf", pdf_filename)
    os.makedirs("pdf", exist_ok=True)

    pdf = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    pdf.setTitle(f"Bestellung {bestellnummer}")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 50, f"Bestellung {bestellnummer}")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 80, f"Kunde: {kunde.name}")
    pdf.drawString(50, height - 100, f"Kundennummer: {kunde.pf_kundennummer}")
    pdf.drawString(50, height - 120, f"Adresse: {kunde.adresse_str}, {kunde.adresse_plz} {kunde.adresse_ort}")
    pdf.drawString(50, height - 140, f"Kontakt: {kunde.email} | {kunde.tel}")

    y_position = height - 170
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position, "Bestellpositionen:")

    pdf.setFont("Helvetica", 10)
    y_position -= 20
    pdf.drawString(50, y_position, "Artikel")
    pdf.drawString(300, y_position, "Bestand")
    pdf.drawString(400, y_position, "Sollbestand")
    pdf.drawString(500, y_position, "Zu bestellen")

    y_position -= 10
    pdf.line(50, y_position, 550, y_position)

    y_position -= 20

    print("📌 DEBUG: Eingehende Artikel-Daten:", artikel_daten)

    for artikel in artikel_daten:
        try:
            artikel_id = artikel.get("artikel_id", "UNBEKANNT")
            artikel_name = artikel.get("name", "OHNE NAME")
            artikel_bestand = artikel.get("bestand", 0)
            artikel_sollbestand = artikel.get("sollbestand", 0)
            artikel_menge = artikel.get("menge", 0)

            if y_position < 100:  
                pdf.showPage()  
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(50, height - 50, f"Bestellung {bestellnummer}")
                pdf.setFont("Helvetica", 10)
                y_position = height - 80  

            pdf.drawString(50, y_position, str(artikel_id))
            pdf.drawString(110, y_position, artikel_name)
            pdf.drawString(320, y_position, str(artikel_bestand))
            pdf.drawString(400, y_position, str(artikel_sollbestand))
            pdf.drawString(500, y_position, str(artikel_menge))
            y_position -= 20

        except Exception as e:
            print(f"❌ Fehler bei der Verarbeitung eines Artikels: {e}")

    pdf.showPage()
    pdf.save()

    return pdf_path  # 📌 Pfad der erstellten PDF zurückgeben

@bp.route('/pdf/<filename>')
def serve_pdf(filename):
    pdf_dir = os.path.join(os.getcwd(), "pdf")  # Pfad zum PDF-Ordner
    file_path = os.path.join(pdf_dir, filename)  # Datei zusammenfügen

    if not os.path.exists(file_path):
        abort(404)  # Falls die Datei nicht existiert, 404-Fehler zurückgeben

    return send_from_directory(pdf_dir, filename, as_attachment=False)

@bp.route("/api/check_bestellt", methods=["GET"])
def check_bestellt():
    artikel_id = request.args.get("artikel_id")

    if not artikel_id:
        return jsonify({"error": "Kein Artikel angegeben"}), 400

    bestell_info = (
        db.session.query(
            Bestellposition.artikel_id,
            func.sum(Bestellposition.menge).label("menge"),
            Bestellung.bestellnummer
        )
        .join(Bestellung, Bestellung.id == Bestellposition.bestellung_id)
        .filter(Bestellung.status == "Offen", Bestellposition.artikel_id == artikel_id)
        .group_by(Bestellposition.artikel_id, Bestellung.bestellnummer)
        .all()
    )

    if bestell_info:
        # Bestellte Mengen aufsummieren
        total_menge = sum(item.menge for item in bestell_info)
        bestellnummern = [item.bestellnummer for item in bestell_info]

        return jsonify({
            "bestellte_menge": total_menge,
            "bestellnummern": bestellnummern
        })
    else:
        return jsonify({
            "bestellte_menge": 0,
            "bestellnummern": []
        })



@bp.route("/pdf", methods=["POST"])
def bestellung_generieren_pdf():
    """
    Erstellt eine Bestellung, speichert sie in der Datenbank und sendet sie ggf. per E-Mail mit PDF-Anhang.
    """
    artikel_ids = request.form.getlist("artikel_id[]")  # ✅ Alle Artikel-IDs holen
    bestellmengen = request.form.getlist("bestellmenge[]")  # ✅ Alle Bestellmengen holen

    print(f"📌 DEBUG: Erhaltene Artikel-IDs: {artikel_ids}")
    print(f"📌 DEBUG: Erhaltene Bestellmengen: {bestellmengen}")

    send_email = "send_email" in request.form  # 🔹 Prüfen, ob die Bestellung per E-Mail gesendet werden soll

    if not artikel_ids or not bestellmengen or len(artikel_ids) != len(bestellmengen):
        flash("Fehler: Keine Artikel ausgewählt oder fehlerhafte Daten!", "danger")
        return redirect(url_for("bestellungen.bestellung_uebersicht"))

    kunde = Kunde.query.first()
    if not kunde:
        flash("Kein Kunde gefunden!", "danger")
        return redirect(url_for("bestellungen.bestellung_uebersicht"))

    bestellnummer = f"ORDER-{uuid.uuid4().hex[:8]}"

    neue_bestellung = Bestellung(
        bestellnummer=bestellnummer,
        bestelldatum=datetime.utcnow(),
        status="Offen"
    )
    db.session.add(neue_bestellung)
    db.session.flush()

    # 1️⃣ Ermitteln der bereits bestellten Mengen aus offenen Bestellungen
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

    # 2️⃣ Dictionary mit bestellten Mengen
    bestell_mengen_dict = {artikel_id: menge for artikel_id, menge in bestell_mengen}

    # 3️⃣ **Artikel-Liste initialisieren**
    artikel_liste = []

    # 4️⃣ **Artikel mit Bestellmenge 0 UND bestehender offener Bestellung ignorieren**
    for artikel_id, bestellmenge in zip(artikel_ids, bestellmengen):
        try:
            artikel = Artikel.query.filter_by(pf_artikel_id=artikel_id).first()
            if not artikel:
                continue

            menge = int(bestellmenge) if bestellmenge.isdigit() else 0
            bereits_bestellt = bestell_mengen_dict.get(artikel.pf_artikel_id, 0)

            # Falls Artikel bereits bestellt wurde und Bestellmenge 0 ist, überspringen
            if bereits_bestellt > 0 and menge == 0:
                print(f"⚠ Artikel {artikel.pf_artikel_id} wird ignoriert (bereits bestellt)")
                continue

            neue_bestellposition = Bestellposition(
                bestellung_id=neue_bestellung.id,
                artikel_id=artikel.pf_artikel_id,
                menge=menge,
            )
            db.session.add(neue_bestellposition)

            artikel_liste.append({
                "artikel_id": artikel.pf_artikel_id,
                "name": artikel.name,
                "kategorie": artikel.kategorie,
                "bestand": artikel.bestand,
                "sollbestand": artikel.sollbestand,
                "menge": menge,
            })

            artikel.bestellt = True

        except Exception as e:
            print(f"❌ Fehler beim Hinzufügen des Artikels {artikel_id}: {e}")

    db.session.commit()

    print("📌 DEBUG: Artikel-Liste für PDF:", artikel_liste)

    try:
        pdf_path = create_order_pdf(bestellnummer, kunde, artikel_liste)
    except Exception as e:
        print(f"❌ Fehler bei create_order_pdf: {e}")
        flash(f"Fehler bei der PDF-Erstellung: {e}", "danger")
        return redirect(url_for("bestellungen.bestellung_uebersicht"))

    # **Nur E-Mail senden, wenn der Button 'Bestellung senden (PDF und per E-Mail)' geklickt wurde**
    if send_email:
        email_empfaenger = Administratives.get_einstellung("bestell_email_empfaenger", "default_email@domain.com")
        email_cc = request.form.get("email_cc")

        try:
            send_order_email(kunde, pdf_path, bestellnummer, email_empfaenger, email_cc)
            flash(f"Bestellung {bestellnummer} erfolgreich erstellt und per E-Mail versendet!", "success")
        except Exception as e:
            flash(f"Fehler beim Senden der E-Mail: {str(e)}", "danger")

    return send_file(pdf_path, as_attachment=True, download_name=f"bestellung_{bestellnummer}.pdf", mimetype="application/pdf")
