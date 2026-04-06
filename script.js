async function sendMessage() {
    let input = document.getElementById("userInput");
    let text = input.value.trim();

    if (text === "") return;

    addMessage(text, "user");
    input.value = "";

    let loading = addMessage("⏳ Thinking...", "bot");

    try {
        let res = await fetch("https://health-chatbot-4xf6.onrender.com/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: text })
        });

        let data = await res.json();

        loading.remove();

        if (data.response) {
            addMessage(data.response, "bot");
        } else {
            addMessage("⚠️ No response from server", "bot");
        }

    } catch (error) {
        loading.remove();
        addMessage("❌ Server error or slow startup", "bot");
        console.error(error);
    }
}

// Add message to UI
function addMessage(text, type) {
    let div = document.createElement("div");
    div.className = "msg " + type;
    div.innerText = text;

    document.getElementById("chat").appendChild(div);

    // Auto scroll
    document.getElementById("chat").scrollTop =
        document.getElementById("chat").scrollHeight;

    return div;
}

// ENTER KEY SUPPORT 🔥
document.getElementById("userInput").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});
