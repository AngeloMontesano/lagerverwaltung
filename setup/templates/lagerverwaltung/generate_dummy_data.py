import random
import os
from datetime import datetime, timedelta
from flask import Flask
from database import db
from models import Artikel, Lagerbewegung, Bestellung
from sqlalchemy.exc import IntegrityError

# 🔹 Initialisiere die Flask-App für den Kontext
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://lageruser:lagerpass@1111_mariadb/lagerdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ✅ App-Kontext wird explizit gesetzt
with app.app_context():

    def generate_unique_pf_artikel_id():
        """
        Erstellt eine einzigartige Artikel-ID.
        """
        while True:
            neue_id = "ART-" + str(random.randint(1000, 9999))
            existiert = Artikel.query.filter_by(pf_artikel_id=neue_id).first()
            if not existiert:
                return neue_id

    def create_dummy_articles():
        """
        Erstellt Dummy-Artikel in der Datenbank.
        """
        artikel_namen = [
            "Mehl", "Zucker", "Salz", "Butter", "Milch", "Eier", "Hefe", "Honig",
            "Backpulver", "Vanillezucker", "Schokolade", "Mandeln", "Haselnüsse",
            "Kakao", "Joghurt", "Öl", "Essig", "Zitronensaft", "Kartoffeln", "Karotten",
            "Zwiebeln", "Knoblauch", "Apfel", "Banane", "Orangensaft", "Käse", "Wurst",
            "Brot", "Brötchen", "Marmelade", "Schinken", "Nudeln", "Reis", "Linsen"
        ]

        for _ in range(50):
            pf_artikel_id = generate_unique_pf_artikel_id()
            artikel = Artikel(
                pf_artikel_id=pf_artikel_id,
                name=random.choice(artikel_namen),
                ean=str(random.randint(1000000000000, 9999999999999)),
                bestand=random.randint(1, 50),
                mindestbestand=random.randint(1, 10),
                sollbestand=random.randint(10, 30),
                kategorie="Zutaten",
                kunde_id="1",
                mhd_datum="2025-12-31"
            )

            try:
                db.session.add(artikel)
                db.session.commit()
                print(f"✅ Artikel {pf_artikel_id} ({artikel.name}) erstellt!")
            except IntegrityError:
                db.session.rollback()
                print(f"⚠️ Artikel {pf_artikel_id} bereits vorhanden, wird übersprungen.")

    create_dummy_articles()
