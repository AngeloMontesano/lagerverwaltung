document.getElementById("darkModeToggle").addEventListener("click", function () {
    document.body.classList.toggle("dark-mode");
    localStorage.setItem("darkMode", document.body.classList.contains("dark-mode") ? "enabled" : "disabled");
});

// Dark Mode beim Laden setzen
if (localStorage.getItem("darkMode") === "enabled") {
    document.body.classList.add("dark-mode");
}
