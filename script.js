async function send() {
    let input = document.getElementById("msg");
    let text = input.value;

    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    let res = await fetch("https://health-chatbot-4xf6.onrender.com/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: text})
});

let data = await res.json();
addMessage(data.response, "bot");
}

function addMessage(text, type) {
    let div = document.createElement("div");
    div.className = "msg " + type;
    div.innerText = text;

    document.getElementById("chat").appendChild(div);
}
