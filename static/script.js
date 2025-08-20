let isListening = false;
let recognition;

// Send text command to Flask backend
function sendCommand() {
    let command = document.getElementById("command").value;
    let output = document.getElementById("output");

    if (command.trim() === "") {
        output.innerHTML = "Please enter a command, Senpai~";
        return;
    }

    output.innerHTML = "Processing...";

    fetch("/luna_command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: command })
    })
    .then(response => {
        if (!response.ok) throw new Error("Server error");
        return response.json();
    })
    .then(data => {
        output.innerHTML = data.reply;
    })
    .catch(error => {
        output.innerHTML = "Luna is not responding, Senpai~ Please check the server!";
    });
}

// Start voice recognition
function startListening() {
    let output = document.getElementById("output");
    let SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        output.innerHTML = "Voice recognition is not supported in this browser. Use Chrome!";
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    isListening = true;

    recognition.onstart = function() {
        output.innerHTML = "Listening...";
        document.getElementById("stopButton").style.display = "inline";
    };

    recognition.onresult = function(event) {
        let command = event.results[event.results.length - 1][0].transcript.toLowerCase();
        document.getElementById("command").value = command;
        sendCommand();

        if (command.includes("luna stop")) {
            stopListening();
        }
    };

    recognition.onerror = function() {
        output.innerHTML = "Gomen, Senpai~ I couldn't hear that!";
    };

    recognition.onend = function() {
        output.innerHTML = "Ask me anything, Senpai~";
        document.getElementById("stopButton").style.display = "none";
    };

    recognition.start();
}

// Stop voice recognition
function stopListening() {
    if (recognition) {
        recognition.stop();
        isListening = false;
        document.getElementById("output").innerHTML = "Luna has stopped listening.";
        document.getElementById("stopButton").style.display = "none";
    }
}