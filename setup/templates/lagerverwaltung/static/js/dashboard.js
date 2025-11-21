// =============================================
// 🔹 Dashboard-Initialisierung
// =============================================

document.addEventListener("DOMContentLoaded", function () {

    // Dashboard-Daten abrufen
    fetch("/api/dashboard/")
        .then(response => response.json())
        .then(data => {

            // 🔹 Gesamtanzahl der Artikel aktualisieren
            document.getElementById("gesamt-artikel").textContent = data.gesamt_artikel;

            // 🔹 Anzahl der kritischen Artikel aktualisieren
            document.getElementById("kritische-artikel").textContent = data.kritische_artikel;

            // 🔹 Letzte Bestellungen aktualisieren
            const bestellungenList = document.getElementById("letzte-bestellungen");
            bestellungenList.innerHTML = ""; 
            
            data.letzte_bestellungen.forEach(bestellung => {
                const li = document.createElement("li");
                li.textContent = `Bestellung ${bestellung.id}: ${bestellung.menge} Artikel (Status: ${bestellung.status})`;
                li.classList.add("list-group-item");
                li.addEventListener("click", function() {
                    showBestellungDetails(bestellung);
                });
                bestellungenList.appendChild(li);
            });

            // 🔹 Notifications für kritische Artikel
            data.kritische_artikel_liste.forEach(artikel => {
                showNotification(
                    `⚠️ Artikel unter Mindestbestand: ${artikel.name} (Bestand: ${artikel.bestand}, Mindestbestand: ${artikel.mindestbestand})`, 
                    "warning"
                );
            });

        })
        .catch(error => {
            console.error("❌ Fehler beim Abrufen der Dashboard-Daten:", error);
        });

	function showBestellungDetails(bestellung) {
		document.getElementById("bestell-id").textContent = bestellung.id;
		document.getElementById("bestell-menge").textContent = bestellung.menge;
		document.getElementById("bestell-status").textContent = bestellung.status;

		let modal = new bootstrap.Modal(document.getElementById("bestellungModal"));
		modal.show();
	}

});

