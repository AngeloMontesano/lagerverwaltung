// =============================================
// 🔹 Initialisierung des Event Listeners
// =============================================
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Bestellungen-Skript geladen...");

    // =============================================
    // 🔹 Wichtige HTML-Elemente abrufen
    // =============================================
    const artikelSelect = document.getElementById("neuer_artikel_select");
    const tabelle = document.getElementById("artikel-tabelle");
    const auswahlZeile = document.getElementById("artikel-auswahl-zeile");
    const bestellungForm = document.querySelector("form");

    if (!artikelSelect || !tabelle || !auswahlZeile || !bestellungForm) {
        console.error("❌ FEHLER: Notwendige Elemente wurden nicht gefunden!");
        return;
    }

    // =============================================
    // 🔹 Event: Artikel zum Bestellformular hinzufügen
    // =============================================
    artikelSelect.addEventListener("change", function () {
        const selectedOption = artikelSelect.options[artikelSelect.selectedIndex];

        if (selectedOption.value) {
            console.log("✅ Artikel ausgewählt:", selectedOption.value);

            const artikelId = selectedOption.value;
            const artikelName = selectedOption.dataset.name;
            const artikelKategorie = selectedOption.dataset.kategorie;
            const artikelBestand = selectedOption.dataset.bestand;
            const artikelSollbestand = selectedOption.dataset.sollbestand;

            console.log("📌 Artikel-Daten:", { artikelId, artikelName, artikelKategorie, artikelBestand, artikelSollbestand });

            // Überprüfen, ob Artikel bereits in der Liste ist
            const vorhandeneArtikel = document.querySelectorAll('input[name="artikel_id[]"]');
            for (let input of vorhandeneArtikel) {
                if (input.value === artikelId) {
                    showCustomAlert("❗ Artikel ist bereits in der Liste!");
                    return;
                }
            }

            // Bestellstatus abrufen und Artikel hinzufügen
            fetch(`/bestellungen/api/check_bestellt?artikel_id=${artikelId}`)
                .then(response => response.json())
                .then(data => {
                    const bestellteMenge = data.bestellte_menge || 0;
                    const bestellnummern = data.bestellnummern || [];
                    const bestellnummernText = bestellnummern.length > 0 ? bestellnummern.join(", ") : "";

                    if (bestellteMenge > 0 && (artikelSollbestand - artikelBestand) <= 0) {
                        showCustomAlert("❌ Dieser Artikel kann nicht erneut bestellt werden, da bereits eine offene Bestellung existiert.");
                        return;
                    }

                    const neueZeile = document.createElement("tr");
                    if (bestellteMenge > 0) {
                        neueZeile.classList.add("bestellte-zeile");
                    }

                    neueZeile.innerHTML = `
                        <td><input type="hidden" name="artikel_id[]" value="${artikelId}">${artikelId}</td>
                        <td>${artikelName}</td>
                        <td>${artikelKategorie}</td>
                        <td>${artikelBestand}</td>
                        <td>${artikelSollbestand}</td>
                        <td><input type="number" class="form-control" name="bestellmenge[]" min="0" value="${bestellteMenge > 0 ? 0 : (artikelSollbestand - artikelBestand > 0 ? artikelSollbestand - artikelBestand : 0)}"></td>
                        <td>${bestellteMenge > 0 ? bestellteMenge + ' <button type="button" class="btn btn-secondary btn-sm bestellnummer-btn" title="Offene Bestellungen: ' + bestellnummernText + '">🔍</button>' : '-'}
                        </td>
                        <td><button type="button" class="btn btn-danger btn-sm artikel-entfernen">🗑️</button></td>
                    `;

                    tabelle.insertBefore(neueZeile, auswahlZeile);
                })
                .catch(error => console.error("❌ Fehler beim Abrufen der Bestellinformationen:", error));

            artikelSelect.selectedIndex = 0;
        }
    });

    // =============================================
    // 🔹 Bestellformular absenden
    // =============================================
    bestellungForm.addEventListener("submit", function (event) {
        let bestellmengen = document.querySelectorAll('input[name="bestellmenge[]"]');
        let hatBestellung = false;

        bestellmengen.forEach(menge => {
            let bestellteMenge = parseInt(menge.value);
            let artikelRow = menge.closest("tr");
            let hatOffeneBestellung = artikelRow.classList.contains("bestellte-zeile");

            console.log("🔍 Überprüfe Bestellmenge:", bestellteMenge, "Offene Bestellung:", hatOffeneBestellung);

            if (bestellteMenge > 0) {
                hatBestellung = true;
            }
        });

        if (!hatBestellung) {
            event.preventDefault();
            showCustomAlert("❌ Keine Artikel für Bestellung ausgewählt!");
            return;
        }

        setTimeout(() => {
            location.reload();
        }, 2000);
    });

    // =============================================
    // 🔹 Artikel aus der Bestellliste entfernen
    // =============================================
    tabelle.addEventListener("click", function (event) {
        if (event.target.classList.contains("artikel-entfernen")) {
            event.target.closest("tr").remove();
        }
    });

    // =============================================
    // 🔹 Event-Listener für Stornieren & Erledigt-Markieren
    // =============================================
    document.body.addEventListener("click", function (event) {
        if (event.target.classList.contains("stornieren-btn")) {
            const bestellungId = event.target.dataset.id;
            console.log(`📌 Bestellung stornieren geklickt, ID: ${bestellungId}`);

            if (confirm("Möchtest du diese Bestellung wirklich stornieren?")) {
                fetch("/bestellungen/stornieren", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: `bestellung_id=${bestellungId}`
                })
                .then(response => response.text())
                .then(() => {
                    showCustomAlert("Bestellung erfolgreich storniert!"); 
                    location.reload();
                })
                .catch(error => showCustomAlert("Fehler beim Stornieren der Bestellung!"));
            }
        }

        if (event.target.classList.contains("erledigt-btn")) {
            const bestellungId = event.target.dataset.id;
            console.log(`📌 Als erledigt markieren geklickt, ID: ${bestellungId}`);

            if (confirm("Möchtest du diese Bestellung als erledigt markieren?")) {
                fetch("/bestellungen/erledigt", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: `bestellung_id=${bestellungId}`
                })
                .then(response => response.text())
                .then(() => {
                    showCustomAlert("Bestellung als erledigt markiert!");
                    location.reload();
                })
                .catch(error => showCustomAlert("Fehler beim Erledigen der Bestellung!"));
            }
        }
    });

    // =============================================
    // 🔹 Event-Listener für Lupe-Symbol (Direkt zur Bestellung scrollen)
    // =============================================
    document.querySelectorAll(".scroll-to").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const targetId = this.getAttribute("href");
            document.querySelector(targetId).scrollIntoView({ behavior: "smooth" });
        });
    });

    console.log("✅ Event-Listener für Lupe hinzugefügt.");
});

// =============================================
// 🔹 Benachrichtigungssystem
// =============================================
function showCustomAlert(message) {
    const alertBox = document.createElement("div");
    alertBox.className = "custom-alert";
    alertBox.innerHTML = `<span>${message}</span>`;

    document.body.appendChild(alertBox);

    setTimeout(() => {
        alertBox.style.opacity = "0";
        setTimeout(() => alertBox.remove(), 500);
    }, 3000);
}

// =============================================
// 🔹 Sortierung und Gruppierung erledigter Bestellungen
// =============================================
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Bestellungen-Skript geladen...");

    // Referenz zur Accordion-Liste der erledigten Bestellungen
    const erledigteBestellungenAccordion = document.getElementById("erledigteBestellungenAccordion");
    if (!erledigteBestellungenAccordion) return;

    // Bestellungen nach Datum gruppieren (Monatliche Gruppierung)
    const erledigteBestellungen = Array.from(erledigteBestellungenAccordion.children);
    const bestellungenNachMonat = {};

    erledigteBestellungen.forEach((bestellung) => {
        const datumText = bestellung.querySelector(".accordion-button").textContent;
        const datum = new Date(datumText.split("|")[1].trim());
        const monatJahr = datum.toLocaleString("de-DE", { year: "numeric", month: "long" });
        
        if (!bestellungenNachMonat[monatJahr]) {
            bestellungenNachMonat[monatJahr] = [];
        }
        bestellungenNachMonat[monatJahr].push(bestellung);
    });

    // Sortierte Gruppierung in die Accordion-Struktur einfügen
    erledigteBestellungenAccordion.innerHTML = "";
    Object.entries(bestellungenNachMonat).sort((a, b) => new Date(b[0]) - new Date(a[0])).forEach(([monat, bestellungen]) => {
        const accordionItem = document.createElement("div");
        accordionItem.classList.add("accordion-item");
        accordionItem.innerHTML = `
            <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${monat.replace(/\s/g, '')}">
                    📅 ${monat}
                </button>
            </h2>
            <div id="collapse${monat.replace(/\s/g, '')}" class="accordion-collapse collapse">
                <div class="accordion-body"></div>
            </div>
        `;
        const body = accordionItem.querySelector(".accordion-body");
        bestellungen.sort((a, b) => new Date(b.querySelector(".accordion-button").textContent.split("|")[1].trim()) - new Date(a.querySelector(".accordion-button").textContent.split("|")[1].trim()));
        bestellungen.forEach((bestellung) => body.appendChild(bestellung));
        erledigteBestellungenAccordion.appendChild(accordionItem);
    });
});


// =============================================
// 🔹 Styling für Benachrichtigungen
// =============================================
const style = document.createElement("style");
style.innerHTML = `
    .custom-alert {
        position: fixed;
        top: 20px;
        right: 20px;
        background: red;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        z-index: 1000;
        font-size: 14px;
        transition: opacity 0.5s ease-in-out;
    }
`;
document.head.appendChild(style);
