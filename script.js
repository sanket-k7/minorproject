async function sendMessage() {
    let input = document.getElementById("userInput");
    let text = input.value.trim();

    if (text === "") return;

    addMessage(text, "user");
    input.value = "";

    let loading = addMessage("⏳ Thinking...", "bot");

    try {
        let res = await fetch("https://health-chatbot-4xf6.onrender.com/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: text })
        });

        let data = await res.json();   // ✅ ONLY ONCE

        loading.remove();

        if (data.result) {
            addMessage(
                "🦠 Disease: " + data.result + "\n📊 Confidence: " + data.confidence + "%", 
                "bot"
            );
        } else {
            addMessage("⚠️ No response from server", "bot");
        }

    } catch (error) {
        loading.remove();
        addMessage("❌ Server slow / starting (wait 30 sec)", "bot");
        console.error(error);
    }
}
