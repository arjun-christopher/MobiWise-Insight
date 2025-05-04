function toggleChatbot() {
    const modal = document.getElementById("chatbot-modal");
    modal.style.display = modal.style.display === "none" ? "flex" : "none";
}

function sendMessage() {
    const input = document.getElementById("chatbot-input");
    const msg = input.value.trim();
    if (!msg) return;

    const chatBody = document.getElementById("chatbot-body");
    chatBody.innerHTML += `<div><strong>You:</strong> ${msg}</div>`;

    fetch("/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
    })
    .then(res => res.json())
    .then(data => {
        chatBody.innerHTML += `<div><strong>Bot:</strong> ${data.reply}</div><br>`;
        chatBody.scrollTop = chatBody.scrollHeight;
    })
    .catch(() => {
        chatBody.innerHTML += `<div><strong>Bot:</strong> Sorry, something went wrong.</div><br>`;
    });

    input.value = "";
}

document.addEventListener("click", function(event) {
    const chatbotModal = document.getElementById("chatbot-modal");
    const chatbotButton = document.getElementById("chatbot-button");

    // Check if modal is open
    if (chatbotModal && chatbotModal.style.display === "flex") {
        // If the click is outside both the chatbot modal and button, close it
        if (!chatbotModal.contains(event.target) && !chatbotButton.contains(event.target)) {
            chatbotModal.style.display = "none";
        }
    }
});
