from datetime import datetime
import threading
from flask import Flask

# Assuming luna_speak is a function you need to define or import
def luna_speak(message):
    print(message)  # Replace with actual implementation

# Initialize Flask app
app = Flask(__name__)

def auto_greet():
    hour = datetime.now().hour
    if hour < 12:
        return "Ohayou gozaimasu~ Good morning, Senpai! ☀️"
    elif 12 <= hour < 18:
        return "Konnichiwa~ Ready for a productive afternoon, Senpai? 💼"
    else:
        return "Konbanwa~ Time to relax, Senpai~ 🌙"

@app.before_first_request
def startup_greeting():
    greeting = auto_greet()
    threading.Thread(target=luna_speak, args=(greeting,)).start()
