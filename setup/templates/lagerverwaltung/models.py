# =============================================
# 🔹 Datenbank-Modelle für die Lagerverwaltungs-App
# =============================================

from database import db
from datetime import datetime
import uuid


# =============================================
# 🔹 Artikel-Tabelle
# =============================================
class Artikel(db.Model):
    """
    Tabelle für Artikel in der Lagerverwaltung.
    """
    __tablename__ = "artikel"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    pf_artikel_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    ean = db.Column(db.String(100), unique=True, nullable=False)
    bestand = db.Column(db.Integer, nullable=False, default=999999999)
    mindestbestand = db.Column(db.Integer, nullable=False, default=0)
    sollbestand = db.Column(db.Integer, nullable=False, default=0)
    kategorie = db.Column(db.String(100), nullable=False)
    bestellt = db.Column(db.Integer, nullable=False, default=0)
    kunde_id = db.Column(db.String(50), nullable=False)
    haltbarkeit = db.Column(db.Integer, nullable=False, default=365)
    letzte_aenderung = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    beschreibung = db.Column(db.Text, nullable=True, default='')

    # 🔹 Neues Feld "letzte_bestellung" hinzufügen
    letzte_bestellung = db.Column(db.DateTime, nullable=True)

    # 🔹 Erweiterte Spalten
    lagerort = db.Column(db.String(255), nullable=True, default="Unbekannt")
    preis = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)

    def to_dict(self):
        """
        Wandelt das Artikel-Objekt in ein Dictionary um, das dann in JSON konvertiert werden kann.
        """
        return {
            'id': self.id,
            'name': self.name,
            'kategorie': self.kategorie,
            'bestand': self.bestand,
            'sollbestand': self.sollbestand,
            'pf_artikel_id': self.pf_artikel_id,
            'lagerort': self.lagerort,
            'preis': self.preis,
            'letzte_bestellung': self.letzte_bestellung  # Hinzufügen der letzten Bestellung
        }


# =============================================
# 🔹 Kunden-Tabelle
# =============================================
class Kunde(db.Model):
    """
    Tabelle für Kunden.
    """
    id = db.Column(db.Integer, primary_key=True)
    pf_kundennummer = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    adresse_str = db.Column(db.String(255), nullable=True)
    adresse_plz = db.Column(db.String(10), nullable=True)
    adresse_ort = db.Column(db.String(100), nullable=True)
    tel = db.Column(db.String(50), nullable=True)
    filialnummer = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Kunde {self.name} ({self.pf_kundennummer})>"


# =============================================
# 🔹 Lagerbewegung-Tabelle
# =============================================
class Lagerbewegung(db.Model):
    """
    Tabelle für Lagerbewegungen (Zugang/Entnahme).
    """
    id = db.Column(db.Integer, primary_key=True)
    artikel_id = db.Column(db.Integer, db.ForeignKey("artikel.id"), nullable=False)
    typ = db.Column(db.String(50), nullable=False)  # Zugang oder Entnahme
    menge = db.Column(db.Integer, nullable=False)
    zeit = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    artikel = db.relationship("Artikel", backref="lagerbewegungen")


# =============================================
# 🔹 Verbrauchsstatistik-Tabelle
# =============================================
class Verbrauch(db.Model):
    """
    Tabelle für die Verbrauchsstatistik.
    """
    id = db.Column(db.Integer, primary_key=True)
    artikel_id = db.Column(db.Integer, db.ForeignKey("artikel.id"), nullable=False)
    artikel_name = db.Column(db.String(255), nullable=False)
    monat = db.Column(db.String(7), nullable=False)  # z. B. "2025-01"
    verbrauch = db.Column(db.Integer, nullable=False, default=0)
    letzte_aenderung = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    artikel = db.relationship("Artikel", backref="verbrauchsdaten")


# =============================================
# 🔹 Einstellungen-Tabelle
# =============================================
class Einstellungen(db.Model):
    """
    Tabelle für allgemeine Einstellungen der Lagerverwaltung.
    """
    id = db.Column(db.Integer, primary_key=True)
    einstellung = db.Column(db.String(100), unique=True, nullable=False)
    wert = db.Column(db.String(255), nullable=False)
    letzte_aenderung = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Einstellungen {self.einstellung}: {self.wert}>"


# =============================================
# 🔹 Administratives-Tabelle
# =============================================
class Administratives(db.Model):
    """
    Tabelle für allgemeine Einstellungen des Kunden (z. B. Auto-Bestellung).
    """
    __tablename__ = "administratives"

    id = db.Column(db.Integer, primary_key=True)
    einstellung = db.Column(db.String(255), unique=True, nullable=False)
    wert = db.Column(db.String(255), nullable=False)
    letzte_aenderung = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Einstellung {self.einstellung}: {self.wert}>"

    @staticmethod
    def get_einstellung(name, default=""):
        """
        Gibt den Wert einer bestimmten Einstellung zurück.
        Falls sie nicht existiert, wird der Default-Wert gespeichert und zurückgegeben.
        """
        einstellung = Administratives.query.filter_by(einstellung=name).first()
        if not einstellung:
            einstellung = Administratives(einstellung=name, wert=default)
            db.session.add(einstellung)
            db.session.commit()
        return einstellung.wert

    @staticmethod
    def set_einstellung(name, wert):
        """
        Setzt den Wert einer bestimmten Einstellung.
        """
        einstellung = Administratives.query.filter_by(einstellung=name).first()
        if einstellung:
            einstellung.wert = wert
        else:
            einstellung = Administratives(einstellung=name, wert=wert)
            db.session.add(einstellung)
        db.session.commit()


# =============================================
# 🔹 Bestellungen-Tabelle
# =============================================
class Bestellung(db.Model):
    """
    Repräsentiert eine Bestellung mit einer eindeutigen Bestellnummer.
    """
    __tablename__ = "bestellung"

    id = db.Column(db.Integer, primary_key=True)
    bestellnummer = db.Column(db.String(50), unique=True, nullable=False, default=lambda: f"ORDER-{uuid.uuid4().hex[:8]}")
    bestelldatum = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="Offen")  # Status kann "Offen" oder "Erledigt" sein

    # Beziehung zu Bestellpositionen (1:n)
    positionen = db.relationship("Bestellposition", back_populates="bestellung", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bestellung {self.bestellnummer} ({self.status})>"


# =============================================
# 🔹 Bestellposition-Tabelle
# =============================================
class Bestellposition(db.Model):
    """
    Repräsentiert eine Position innerhalb einer Bestellung.
    """
    __tablename__ = "bestellposition"

    id = db.Column(db.Integer, primary_key=True)
    bestellung_id = db.Column(db.Integer, db.ForeignKey("bestellung.id"), nullable=False)
    artikel_id = db.Column(db.String(50), db.ForeignKey("artikel.pf_artikel_id"), nullable=False)
    menge = db.Column(db.Integer, nullable=False, default=1)

    bestellung = db.relationship("Bestellung", back_populates="positionen")
    artikel = db.relationship("Artikel")

    def __repr__(self):
        return f"<Bestellposition Bestellung {self.bestellung_id}, Artikel {self.artikel_id}, Menge {self.menge}>"


# =============================================
# 🔹 Zusatz-Tabellen: Kategorien & Lagerorte
# =============================================
class Kategorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)


class Lagerort(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
