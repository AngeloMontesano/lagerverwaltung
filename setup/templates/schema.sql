-- MariaDB Schema Datei für Lagerverwaltung
-- Automatische Erstellung der Datenbank und Tabellen

-- 1️⃣ Datenbank erstellen
CREATE DATABASE IF NOT EXISTS lagerdb;
USE lagerdb;

-- 2️⃣ Kunde (Filialen)
CREATE TABLE IF NOT EXISTS kunde (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pf_kundennummer VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    adresse_str VARCHAR(255) DEFAULT NULL,   -- Straßenadresse
    adresse_plz VARCHAR(10) DEFAULT NULL,    -- Postleitzahl
    adresse_ort VARCHAR(100) DEFAULT NULL,   -- Stadt/Ort
    email VARCHAR(255) UNIQUE DEFAULT NULL,  -- E-Mail-Adresse
    tel VARCHAR(50) DEFAULT NULL,            -- Telefonnummer
    kontakt VARCHAR(255) DEFAULT NULL,       -- Ansprechpartner
    filialnummer VARCHAR(50) NOT NULL
);

-- 3️⃣ Artikel-Tabelle
CREATE TABLE IF NOT EXISTS artikel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pf_artikel_id VARCHAR(50) UNIQUE NOT NULL,
    ean VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    kategorie VARCHAR(100) NOT NULL DEFAULT 'Sonstiges',
    masseinheit VARCHAR(50) NOT NULL,
    bestand INT NOT NULL DEFAULT 999999999,
    mindestbestand INT NOT NULL DEFAULT 0,
    sollbestand INT NOT NULL DEFAULT 10,
    mhd_datum DATE DEFAULT NULL,
    charge VARCHAR(50) DEFAULT NULL,
    kunde_id INT NOT NULL,
    lagerort VARCHAR(255) DEFAULT 'Unbekannt',
    preis DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    beschreibung TEXT DEFAULT '',
	bestellt BOOLEAN DEFAULT FALSE;
    letzte_aenderung TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    letzte_bestellung TIMESTAMP DEFAULT NULL,
    FOREIGN KEY (kunde_id) REFERENCES kunde(id) ON DELETE CASCADE
);

-- 4️⃣ Lagerbewegungen
CREATE TABLE IF NOT EXISTS lagerbewegungen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artikel_id INT NOT NULL,
    pf_artikel_id VARCHAR(50) NOT NULL,
    typ ENUM('Zugang', 'Entnahme') NOT NULL,
    menge INT NOT NULL,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grund TEXT DEFAULT NULL,
    FOREIGN KEY (artikel_id) REFERENCES artikel(id) ON DELETE CASCADE
);

-- 5️⃣ Bestellungen
CREATE TABLE IF NOT EXISTS bestellungen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kunde_id INT NOT NULL,
    pf_kundennummer VARCHAR(50) NOT NULL,
    bestelldatum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Offen', 'Bestellt', 'Geliefert', 'Storniert') DEFAULT 'Offen',
    FOREIGN KEY (kunde_id) REFERENCES kunde(id) ON DELETE CASCADE
);

-- 6️⃣ Bestellpositionen
CREATE TABLE IF NOT EXISTS bestellpositionen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bestellung_id INT NOT NULL,
    artikel_id INT NOT NULL,
    pf_artikel_id VARCHAR(50) NOT NULL,
	menge INT NOT NULL DEFAULT 0;
    preis DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (bestellung_id) REFERENCES bestellungen(id) ON DELETE CASCADE,
    FOREIGN KEY (artikel_id) REFERENCES artikel(id) ON DELETE CASCADE
);

-- 7️⃣ Administrative Einstellungen
CREATE TABLE IF NOT EXISTS administratives (
    id INT AUTO_INCREMENT PRIMARY KEY,
    einstellung VARCHAR(255) UNIQUE NOT NULL,
    wert VARCHAR(255) NOT NULL,
    letzte_aenderung TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 8️⃣ Automatische Kunden-ID setzen
INSERT INTO kunde (pf_kundennummer, name, filialnummer)
VALUES ('$CONTAINER_NAME', 'Standard Filiale', '$CONTAINER_NAME')
ON DUPLICATE KEY UPDATE name = 'Standard Filiale';

-- Fertig ✅

