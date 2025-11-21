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
