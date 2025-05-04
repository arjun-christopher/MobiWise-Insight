function toggleDinoGame() {
    const modal = document.getElementById("dino-modal");
    const iframe = modal.querySelector("iframe");

    if (modal.style.display === "block") {
        modal.style.display = "none";
        iframe.style.visibility = "hidden"; // Reset on close
    } else {
        modal.style.display = "block";

        // Ensure iframe reloads cleanly every time if needed
        iframe.src = iframe.src;

        // Add a listener to show once loaded
        iframe.onload = function () {
            iframe.style.visibility = "visible";
        };
    }
}

// Close on outside click
window.addEventListener("click", function (e) {
    const modal = document.getElementById("dino-modal");
    const content = document.querySelector(".dino-modal-content");
    const dinoButton = document.getElementById("dino-button");

    if (modal.style.display === "block" && !content.contains(e.target) && !dinoButton.contains(e.target)) {
        modal.style.display = "none";
        const iframe = modal.querySelector("iframe");
        iframe.style.visibility = "hidden";
    }
});