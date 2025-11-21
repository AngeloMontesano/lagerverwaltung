// =============================================
// 🔹 Event Listener für DOMContentLoaded
// =============================================
document.addEventListener("DOMContentLoaded", function () {

    // =============================================
    // 🔹 Globale Button-Elemente definieren
    // =============================================
    const globalEditBtn = document.getElementById("global-edit-btn");
    const globalSaveBtn = document.getElementById("global-save-btn");
    const globalCancelBtn = document.getElementById("global-cancel-btn");

    // =============================================
    // 🔹 Eingabefelder & Löschen-Buttons aktivieren/deaktivieren
    // =============================================
    function setEditableState(editable) {
        document.querySelectorAll("tbody input, tbody select").forEach(input => {
            input.disabled = !editable;
        });
        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.classList.toggle("d-none", !editable);
        });
    }

    // =============================================
    // 🔹 "Bearbeiten"-Button → Eingaben aktivieren
    // =============================================
    globalEditBtn.addEventListener("click", function () {
        setEditableState(true);
        globalEditBtn.classList.add("d-none");
        globalSaveBtn.classList.remove("d-none");
        globalCancelBtn.classList.remove("d-none");
    });

    // =============================================
    // 🔹 "Abbrechen"-Button → Seite neu laden (Änderungen verwerfen)
    // =============================================
    globalCancelBtn.addEventListener("click", function () {
        location.reload();
    });

    // =============================================
    // 🔹 "Speichern"-Button → Geänderte Daten speichern
    // =============================================
    document.getElementById("save-all-form").addEventListener("submit", function (event) {
        event.preventDefault(); // Standard-Formular-Submit verhindern

        let changedData = new FormData();
        let changed = false;
        let rowChangedCount = 0;

        document.querySelectorAll("tbody tr").forEach(row => {
            let pfArtikelId = row.cells[0].innerText.trim();
            let inputs = row.querySelectorAll("input, select");

            let rowChanged = false;
            let rowData = new FormData();
            rowData.append("pf_artikel_id", pfArtikelId);

            inputs.forEach(input => {
                let originalValue = input.getAttribute("data-original")?.trim() || "";
                let newValue = input?.value?.trim() || "";

                if (originalValue !== newValue) {
                    rowData.append(input.name, newValue);
                    rowChanged = true;
                }
            });

            if (rowChanged) {
                rowChangedCount++;
                for (let pair of rowData.entries()) {
                    changedData.append(pair[0], pair[1]);
                }
                changed = true;
            }
        });

        console.log(`🔍 ${rowChangedCount} Zeilen geändert.`);
        console.log("📡 Sende Request an `/save_all` mit diesen Daten:", [...changedData.entries()]);

        if (!changed) {
            showNotification("Keine Änderungen zum Speichern!", "error");
            return;
        }

        fetch(this.action, {
            method: "POST",
            body: changedData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || "Unbekannter Fehler beim Speichern.");
                });
            }
            return response.json();
        })
        .then(() => {
            showNotification("Änderungen gespeichert!", "success");
            setTimeout(() => location.reload(), 1500);
        })
        .catch(error => {
            console.error("❌ Fehler beim Speichern:", error);
            showNotification(error.message, "error");
        });
    });

    // =============================================
    // 🔹 Doppelte Werte in Dropdowns entfernen
    // =============================================
    function removeDuplicateOptions(selectId) {
        let seen = new Set();
        let select = document.getElementById(selectId);

        if (select) {
            Array.from(select.options).forEach(option => {
                if (seen.has(option.value)) {
                    option.remove();
                } else {
                    seen.add(option.value);
                }
            });
        }
    }

    removeDuplicateOptions("filter-kategorie");
    removeDuplicateOptions("filter-lagerort");

    // =============================================
    // 🔹 Artikel löschen
    // =============================================
	window.loeschen = function (id) {
		Swal.fire({
			title: "Bist du sicher?",
			text: "Möchtest du diesen Artikel wirklich löschen?",
			icon: "warning",
			showCancelButton: true,
			confirmButtonText: "Ja, löschen!",
			cancelButtonText: "Abbrechen",
			reverseButtons: true,
			confirmButtonColor: "#dc3545",
			cancelButtonColor: "#6c757d"
		}).then((result) => {
			if (result.isConfirmed) {
				fetch(`/api/artikel/${id}`, { method: "DELETE" })
				.then(response => {
					if (!response.ok) throw new Error("Fehler beim Löschen!");
					return response.json();
				})
				.then(() => {
					Swal.fire("Gelöscht!", "Der Artikel wurde erfolgreich entfernt.", "success");
					setTimeout(() => location.reload(), 1000);
				})
				.catch(error => {
					console.error("❌ Fehler beim Löschen:", error);
					Swal.fire("Fehler!", "Artikel konnte nicht gelöscht werden.", "error");
				});
			}
		});
	};


    // =============================================
    // 🔹 Benachrichtigungsfunktion
    // =============================================
	function showNotification(message, category = "success") {
		let container = document.querySelector(".notification-container");

		if (!container) {
			console.warn("⚠️ Notification-Container nicht gefunden. Warte auf DOM...");
			setTimeout(() => showNotification(message, category), 300);
			return;
		}

		let notification = document.createElement("div");
		notification.className = `notification ${category}`;
		notification.innerHTML = `
			${message} 
			<button type="button" class="btn-close" onclick="this.parentElement.style.display='none';">✖</button>
		`;

		container.appendChild(notification);

		setTimeout(() => {
			notification.style.opacity = "0";
			setTimeout(() => notification.remove(), 500);
		}, 5000);
	}


    // =============================================
    // 🔹 Filterfunktion für die Artikeltabelle
    // =============================================
    document.querySelectorAll("thead input, thead select").forEach(input => {
        input.addEventListener("input", function () {
            const filterValues = {
                id: document.getElementById("filter-id")?.value.toLowerCase() || "",
                name: document.getElementById("filter-name")?.value.toLowerCase() || "",
                kategorie: document.getElementById("filter-kategorie")?.value.toLowerCase() || "",
                bestand: document.getElementById("filter-bestand")?.value || "",
                sollbestand: document.getElementById("filter-sollbestand")?.value || "",
                mindestbestand: document.getElementById("filter-minbestand")?.value || "",
                lagerort: document.getElementById("filter-lagerort")?.value.toLowerCase() || "",
                preis: document.getElementById("filter-preis")?.value || ""
            };

            document.querySelectorAll("tbody tr").forEach(row => {
                const rowValues = {
                    id: row.cells[0].innerText.toLowerCase(),
                    name: row.cells[1].querySelector("input").value.toLowerCase(),
                    kategorie: row.cells[2].querySelector("select").value.toLowerCase(),
                    bestand: row.cells[3].querySelector("input").value,
                    sollbestand: row.cells[4].querySelector("input").value,
                    mindestbestand: row.cells[5].querySelector("input").value,
                    lagerort: row.cells[6].querySelector("select").value.toLowerCase(),
                    preis: row.cells[7].querySelector("input").value
                };

                row.style.display = Object.keys(filterValues).every(key => 
                    !filterValues[key] || rowValues[key].includes(filterValues[key])
                ) ? "" : "none";
            });
        });
    });

    // =============================================
    // 🔹 Initialisierung: Setze Eingaben auf nicht-editierbar
    // =============================================
    setEditableState(false);

});
