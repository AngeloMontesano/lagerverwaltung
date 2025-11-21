// =============================================
// 🔹 Initialisierung von Variablen und Set für Artikel
// =============================================
let selectedArtikel = new Set(); // Set für gewählte Artikel

document.addEventListener("DOMContentLoaded", function () {
    let verbrauchChart = null;
    let trendChart = null;
    let startDate = null;
    let endDate = null;

    // =============================================
    // 🔹 Funktion: Verbrauchsdaten abrufen und filtern
    // =============================================
    function loadData() {
        fetch("/berichte/daten")
            .then(response => response.json())
            .then(daten => {
                // Falls kein Enddatum gewählt, setze auf aktuellen Monat
                if (!endDate) {
                    let now = new Date();
                    endDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
                    document.getElementById("endDate").value = endDate;
                }

                // Falls kein Startdatum gewählt, nehme ältestes verfügbares Datum
                if (!startDate && daten.length > 0) {
                    startDate = daten.reduce((min, d) => d.monat < min ? d.monat : min, daten[0].monat);
                    document.getElementById("startDate").value = startDate;
                }

                // Daten filtern nach gewählten Artikeln und Zeitraum
                let filteredData = daten.filter(d =>
                    selectedArtikel.has(d.artikel) &&
                    (!startDate || d.monat >= startDate) &&
                    (!endDate || d.monat <= endDate)
                );

                updateCharts(filteredData);
            })
            .catch(error => console.error("❌ Fehler beim Laden der Verbrauchsdaten:", error));
    }

    // =============================================
    // 🔹 Funktion: Diagramme aktualisieren (oder neu erstellen)
    // =============================================
    function updateCharts(daten) {
        if (!daten || daten.length === 0) {
            console.error("⚠️ Keine Verbrauchsdaten für ausgewählte Artikel.");
            return;
        }

        let artikelNamen = [...new Set(daten.map(d => d.artikel))];
        let monate = [...new Set(daten.map(d => d.monat))].sort();

        let verbrauchswerte = artikelNamen.map(artikel => {
            return monate.map(monat => {
                let eintrag = daten.find(d => d.artikel === artikel && d.monat === monat);
                return eintrag ? eintrag.verbrauch : 0;
            });
        });

        let colors = ["red", "green", "blue", "orange", "purple", "cyan", "pink", "brown", "lime", "navy"];

        // 🔹 Falls Diagramme bereits existieren, zerstören und neu erstellen
        if (verbrauchChart) verbrauchChart.destroy();
        if (trendChart) trendChart.destroy();

        // 🔹 Verbrauchsanalyse Diagramm (Balkendiagramm)
        verbrauchChart = new Chart(document.getElementById("verbrauchChart"), {
            type: "bar",
            data: {
                labels: monate,
                datasets: artikelNamen.map((artikel, index) => ({
                    label: artikel,
                    data: verbrauchswerte[index],
                    backgroundColor: colors[index % colors.length]
                }))
            }
        });

        // 🔹 Trendanalyse Diagramm (Liniendiagramm)
        trendChart = new Chart(document.getElementById("trendChart"), {
            type: "line",
            data: {
                labels: monate,
                datasets: artikelNamen.map((artikel, index) => ({
                    label: artikel,
                    data: verbrauchswerte[index],
                    borderColor: colors[index % colors.length]
                }))
            }
        });
    }

    // =============================================
    // 🔹 Kategorie-Filter für Artikel
    // =============================================
    document.getElementById("kategorieDropdown").addEventListener("change", function () {
        let selectedKategorie = this.value;
        let artikelDropdown = document.getElementById("artikelDropdown");

        // Filtere Artikel nach gewählter Kategorie
        [...artikelDropdown.options].forEach(option => {
            option.hidden = !(selectedKategorie === "all" || option.dataset.kategorie === selectedKategorie);
        });
    });

    // =============================================
    // 🔹 Artikel zur Analyse hinzufügen
    // =============================================
    document.getElementById("addArtikel").addEventListener("click", function () {
        let artikelDropdown = document.getElementById("artikelDropdown");
        let selectedValue = artikelDropdown.value;

        if (selectedValue && !selectedArtikel.has(selectedValue)) {
            selectedArtikel.add(selectedValue);
            console.log("🔄 Gewählte Artikel:", [...selectedArtikel]); // Debugging
            updateSelectedArtikelDisplay();
            loadData(); // Diagramm aktualisieren
        }
    });

    // =============================================
    // 🔹 Anzeige der gewählten Artikel
    // =============================================
    function updateSelectedArtikelDisplay() {
        let container = document.getElementById("selectedArtikelList");
        container.innerHTML = "";
        selectedArtikel.forEach(artikel => {
            let span = document.createElement("span");
            span.className = "badge bg-primary m-1";
            span.innerText = artikel;
            span.onclick = () => removeArtikel(artikel);
            container.appendChild(span);
        });
    }

    // =============================================
    // 🔹 Artikel aus Analyse entfernen
    // =============================================
    function removeArtikel(artikel) {
        selectedArtikel.delete(artikel);
        updateSelectedArtikelDisplay();
        loadData();
    }

    // =============================================
    // 🔹 Zeitauswahl für Diagramme
    // =============================================
    document.getElementById("applyDateFilter").addEventListener("click", function () {
        startDate = document.getElementById("startDate").value;
        endDate = document.getElementById("endDate").value;

        if (!startDate) {
            alert("❗ Bitte ein Startdatum auswählen.");
            return;
        }

        loadData();
    });

    // Lade zunächst keine Daten → Benutzer muss Artikel wählen
    updateCharts([]);

    // =============================================
    // 🔹 Export-Funktionen für CSV, Excel & PDF
    // =============================================
    function exportCSV() { window.location.href = "/berichte/export/csv"; }
    function exportExcel() { window.location.href = "/berichte/export/excel"; }
    
    function exportPDF() {
        if (selectedArtikel.size === 0) {
            alert("⚠️ Bitte wähle mindestens einen Artikel aus, bevor du das PDF exportierst.");
            return;
        }

        let artikelList = [...selectedArtikel].join(",");
        let startDate = document.getElementById("startDate").value || "";
        let endDate = document.getElementById("endDate").value || "";

        let url = `/berichte/export/pdf?artikel=${encodeURIComponent(artikelList)}&start=${startDate}&end=${endDate}`;

        // 🔹 Lade-Overlay anzeigen
        document.getElementById("loadingOverlay").style.display = "flex";

        // 🔹 PDF generieren & herunterladen
        fetch(url)
            .then(response => {
                document.getElementById("loadingOverlay").style.display = "none"; // 🔹 Overlay ausblenden
                if (response.ok) {
                    window.location.href = url; // 🔹 Datei herunterladen
                } else {
                    alert("❌ Fehler beim PDF-Export!");
                }
            })
            .catch(error => {
                document.getElementById("loadingOverlay").style.display = "none"; // 🔹 Overlay ausblenden
                alert("❌ Fehler beim PDF-Export: " + error);
            });

        console.log("Export-URL:", url);
    }

    // =============================================
    // 🔹 Event-Listener für Exporte
    // =============================================
    document.getElementById("exportCSV").addEventListener("click", exportCSV);
    document.getElementById("exportExcel").addEventListener("click", exportExcel);
    document.getElementById("exportPDF").addEventListener("click", exportPDF);
});
