async function sendMessage() {
    let input = document.getElementById("userInput");
    let text = input.value.trim();

    if (text === "") return;

    addMessage(text, "user");
    input.value = "";

    try {
        let res = await fetch("https://health-chatbot-4xf6.onrender.com/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: text })
        });

        let data = await res.json();

        console.log(data); // debug

        addMessage(data.response, "bot");

    } catch (error) {
        addMessage("⚠️ Error connecting to server", "bot");
        console.error(error);
    }
}

function addMessage(text, type) {
    let div = document.createElement("div");
    div.className = "msg " + type;
    div.innerText = text;

    document.getElementById("chat").appendChild(div);
}
