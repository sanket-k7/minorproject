async function sendMessage() {
    let input = document.getElementById("userInput");
    let text = input.value.trim();

    if (text === "") return;

    addMessage(text, "user");
    input.value = "";

    // Show loading
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

        loading.remove(); // remove loading

        if (data.response) {
            addMessage(data.response, "bot");
        } else {
            addMessage("⚠️ No response from server", "bot");
        }

    } catch (error) {
        loading.remove();
        addMessage("❌ Server error / slow startup (wait 30 sec and try again)", "bot");
        console.error(error);
    }
}

function addMessage(text, type) {
    let div = document.createElement("div");
    div.className = "msg " + type;
    div.innerText = text;

    document.getElementById("chat").appendChild(div);
    return div;
}
