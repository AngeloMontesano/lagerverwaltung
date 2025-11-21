import smtplib
from email.message import EmailMessage

# SMTP-Server-Konfiguration
SMTP_SERVER = "mail.myitnetwork.de"  # Ersetze dies durch deinen SMTP-Server
SMTP_PORT = 465  # Für SSL (587 für TLS)
EMAIL_ABSENDER = "lagerverwaltung@myitnetwork.de"  # Ersetze mit deiner E-Mail-Adresse
EMAIL_PASSWORT = "m5odZeN)WA38d-?oS["  # Ersetze mit deinem Passwort
EMAIL_EMPFAENGER = "angelo@montesano.email"  # Ersetze mit der Empfänger-E-Mail-Adresse

# Erstelle die E-Mail-Nachricht
msg = EmailMessage()
msg.set_content("Dies ist eine Test-E-Mail, um den SMTP-Server zu testen.")
msg["Subject"] = "Test-E-Mail von Python"
msg["From"] = EMAIL_ABSENDER
msg["To"] = EMAIL_EMPFAENGER

try:
    # Verbindung zum SMTP-Server herstellen und E-Mail senden
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_ABSENDER, EMAIL_PASSWORT)  # Anmeldung am SMTP-Server
        server.send_message(msg)  # E-Mail senden
    print("✅ Test-E-Mail wurde erfolgreich gesendet!")
except Exception as e:
    print(f"❌ Fehler beim Senden der Test-E-Mail: {str(e)}")
