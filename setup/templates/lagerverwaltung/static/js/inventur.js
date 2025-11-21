document.addEventListener("DOMContentLoaded", function () {
    console.log("📌 Inventur-Skript geladen.");

    let artikelUpdates = [];

    // Funktion zum Laden der Inventurdaten
    function ladeInventur() {
        fetch("/inventur/")
            .then(response => response.json())
            .then(data => {
                console.log("📥 Empfangene Inventurdaten:", data);
                const inventurTabelle = document.getElementById("inventurTabelle").querySelector("tbody");
                inventurTabelle.innerHTML = "";  // Tabelle leeren, bevor neue Daten geladen werden

                data.forEach(artikel => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td>${artikel.id}</td>
                        <td>${artikel.name}</td>
                        <td>${artikel.ean}</td>
                        <td>${artikel.kategorie}</td>
                        <td>${artikel.bestand}</td>
                        <td>${artikel.sollbestand}</td>
                        <td>${artikel.mindestbestand}</td>
                        <td>${artikel.mhd || '-'}</td>
                        <td><input type="number" class="bestand-input form-control" 
                            data-id="${artikel.id}" value="${artikel.bestand}" 
                            data-original="${artikel.bestand}">
                        </td>
                    `;
                    inventurTabelle.appendChild(tr);

                    const inputFeld = tr.querySelector(".bestand-input");
                    inputFeld.addEventListener("input", function () {
                        const artikelId = inputFeld.getAttribute("data-id");
                        const neuerBestand = inputFeld.value.trim();
                        const originalBestand = inputFeld.getAttribute("data-original").trim();

                        if (neuerBestand !== originalBestand) {
                            let artikelUpdate = artikelUpdates.find(item => item.id === artikelId);
                            if (artikelUpdate) {
                                artikelUpdate.bestand = neuerBestand;
                            } else {
                                artikelUpdates.push({ id: artikelId, bestand: neuerBestand });
                            }
                        }
                    });
                });
            })
            .catch(error => console.error("❌ Fehler beim Laden der Inventurdaten:", error));
    }

    // Funktion zum Speichern der Änderungen
    //function speichereAlleInventur() {
        //if (artikelUpdates.length === 0) {
        //    alert("✅ Keine Änderungen zum Speichern!");
        //    return;
      //  }

        console.log("📡 Sende Request an `/inventur/save_all` mit diesen Daten:", artikelUpdates);

        fetch("/inventur/save_all", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ updates: artikelUpdates })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);

            // Nach dem Speichern die Tabelle mit den neuen Beständen neu laden
            artikelUpdates.forEach(update => {
                let artikelId = String(update.id);
                let inputFeld = document.querySelector(`input[data-id='${artikelId}']`);

                if (!inputFeld) {
                    console.warn(`⚠️ Kein Input-Feld für Artikel-ID ${artikelId} gefunden.`);
                    return;
                }

                inputFeld.setAttribute("data-original", update.bestand);
                inputFeld.value = update.bestand;

                let tr = inputFeld.closest("tr");
                tr.querySelector("td:nth-child(5)").innerText = update.bestand;
            });
        })
        .catch(error => {
            console.error("❌ Fehler beim Speichern:", error);
            alert("Fehler beim Speichern! Überprüfe die Konsole für mehr Infos.");
        });
    }

    //document.getElementById("speichern-alle").addEventListener("click", speichereAlleInventur);
	document.getElementById("speichern-alle").addEventListener("click", function () {
		speichereAlleInventur();

		// 🔄 Nach 3 Sekunden ein vollständiges F5-Refresh
		setTimeout(() => {
			console.log("🔄 F5-Refresh wird ausgeführt...");
			window.location.href = window.location.href; // Oder: window.location.reload(true);
		}, 3000);
	});

    // Daten laden
    ladeInventur();
});
