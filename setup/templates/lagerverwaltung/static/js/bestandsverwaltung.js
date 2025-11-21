// =============================================
// 🔹 Initialisierung des Event Listeners
// =============================================
document.addEventListener("DOMContentLoaded", function () {

    // =============================================
    // 🔹 Funktion: Barcode-Scan an den Server senden
    // =============================================
    function sendRequest(endpoint, barcode, type) {
        fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ barcode: barcode })
        })
        .then(response => response.json())
		.then(data => {
			if (data.error) {
				showNotification(data.error, "error");
			} else {
				let notificationType = data.typ === "Entnahme" ? "error" : "success"; // 🔹 Entnahme wird rot, Zugang bleibt grün
				showNotification(data.message, notificationType);
				updateLagerbewegungen(data);
			}
		})
    }

    // =============================================
    // 🔹 Funktion: Barcode-Scan über Enter-Taste erfassen
    // =============================================
    function handleScan(event, type) {
        if (event.key === "Enter") {
            event.preventDefault(); // 🚀 Verhindert das Standardverhalten
            let barcode = event.target.value.trim();
            if (barcode) {
                sendRequest(type === "Entnahme" ? "/bestandsverwaltung/entnahme" : "/bestandsverwaltung/zugang", barcode, type);
                event.target.value = ""; // Eingabefeld nach Scan leeren
            }
        }
    }

    // =============================================
    // 🔹 Event-Listener für Barcode-Scan-Eingabefelder
    // =============================================
    let barcodeEntnahme = document.getElementById("barcode_entnahme");
    if (barcodeEntnahme) {
        barcodeEntnahme.addEventListener("keypress", function(event) {
            handleScan(event, "Entnahme");
        });
    }

    let barcodeZugang = document.getElementById("barcode_zugang");
    if (barcodeZugang) {
        barcodeZugang.addEventListener("keypress", function(event) {
            handleScan(event, "Zugang");
        });
    }

    // =============================================
    // 🔹 Klickevent für Buttons (falls Nutzer nicht "Enter" drückt)
    // =============================================
    document.getElementById("btn_entnahme").addEventListener("click", function () {
        let barcode = document.getElementById("barcode_entnahme").value.trim();
        if (barcode) {
            sendRequest("/bestandsverwaltung/entnahme", barcode, "Entnahme");
            document.getElementById("barcode_entnahme").value = ""; // Eingabe leeren
        }
    });

    document.getElementById("btn_zugang").addEventListener("click", function () {
        let barcode = document.getElementById("barcode_zugang").value.trim();
        if (barcode) {
            sendRequest("/bestandsverwaltung/zugang", barcode, "Zugang");
            document.getElementById("barcode_zugang").value = ""; // Eingabe leeren
        }
    });

    // =============================================
    // 🔹 Benachrichtigungssystem
    // =============================================
	function showNotification(message, category = "success") {
		let container = document.querySelector(".notification-container");
		if (!container) {
			console.error("❌ Kein Notification-Container gefunden!");
			return;
		}

		let notification = document.createElement("div");
		notification.className = `notification ${category}`;
		notification.innerHTML = `
			${message} 
			<button type="button" class="btn-close" onclick="this.parentElement.style.display='none';"></button>
		`;

		container.appendChild(notification);

		setTimeout(() => {
			notification.style.opacity = "0";
			setTimeout(() => notification.remove(), 500);
		}, 5000);
	}


    // =============================================
    // 🔹 Funktion: Aktualisiert die Lagerbewegungen in der Tabelle
    // =============================================
    function updateLagerbewegungen(data) {
        let tableBody = document.querySelector("tbody");
        let newRow = document.createElement("tr");

        // Unterschiedliche Hervorhebung für Zugang/Entnahme
        newRow.className = data.typ === "Entnahme" ? "table-danger" : "table-success";
        newRow.innerHTML = `
            <td>${data.pf_artikel_id}</td>
            <td>${data.ean}</td>
            <td>${data.artikel}</td>
            <td>${data.typ}</td>
            <td>1</td>
            <td>${new Date().toISOString().slice(0, 19).replace("T", " ")}</td>
        `;

        tableBody.prepend(newRow); // Neue Zeile oben einfügen
    }

    // =============================================
    // 🔹 Fokus auf das erste Barcode-Eingabefeld setzen
    // =============================================
    if (barcodeEntnahme) {
        barcodeEntnahme.focus();
    }

	document.addEventListener("DOMContentLoaded", function () {
		document.querySelectorAll("#lagerbewegungen tr").forEach(row => {
			row.addEventListener("click", function () {
				let cells = row.getElementsByTagName("td");

				document.getElementById("lager-artikelname").textContent = cells[2].textContent;
				document.getElementById("lager-typ").textContent = cells[3].textContent;
				document.getElementById("lager-menge").textContent = cells[4].textContent;
				document.getElementById("lager-datum").textContent = cells[5].textContent;

				let modal = new bootstrap.Modal(document.getElementById("lagerbewegungModal"));
				modal.show();
			});
		});
	});


});
