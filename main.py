import threading
import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from modules.app_handler import open_application
from modules.utils import (
    get_time, get_battery_status, get_cpu_usage,
    get_ram_usage, get_disk_usage, run_speed_test
)
from modules.interactions import luna_speak
from modules.web_search import search, find, explore  # Import your modular search functions
from modules.history_manager import get_from_history, save_to_history
from modules.history_manager import get_from_history, save_to_history, get_all_history
from modules.network_utils import is_online


load_dotenv("setup.env")
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "False").lower() == "true"

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/history")
def view_history():
    history = get_all_history()
    return render_template("history.html", history=history)

@app.route("/luna_command", methods=["POST"])
def luna_command():
    data = request.get_json()
    command = data.get("command", "").lower()
    response = process_command(command)
    return jsonify({"reply": response})

def process_command(command):
    """Processes user commands and determines the appropriate action."""
    command = command.lower()

    if command.startswith("open "):
        app_name = command.replace("open", "").strip()
        response = open_application(app_name) or f"Sorry, Senpai~ I couldn't find {app_name}!"

    elif command.startswith("search "):
        query = command.replace("search", "").strip()
        detailed = any(word in query for word in ["detail", "detailed", "explain"])
        cached_result = get_from_history(query)
        if cached_result:
            response = f"(Offline) {cached_result}"
        elif not is_online():
            response = "Gomen, Senpai~ I'm offline and haven't seen this query before."
        else:
            response = search(query, detailed=detailed)
            save_to_history(query, response)

    elif command.startswith("find "):
        query = command.replace("find", "").strip()
        cached_result = get_from_history(query)
        if cached_result:
            response = f"(Offline) {cached_result}"
        elif not is_online():
            response = "Gomen, Senpai~ I'm offline and can't find this right now."
        else:
            response = find(query)
            save_to_history(query, response)

    elif command.startswith("explore "):
        query = command.replace("explore", "").strip()
        cached_result = get_from_history(query)
        if cached_result:
            response = f"(Offline) {cached_result}"
        elif not is_online():
            response = "Gomen, Senpai~ I'm offline and need internet to explore this."
        else:
            response = explore(query)
            save_to_history(query, response)

    elif "time" in command:
        response = get_time()

    elif "battery" in command:
        response = get_battery_status()

    elif "cpu usage" in command:
        response = get_cpu_usage()

    elif "ram" in command:
        response = get_ram_usage()

    elif "disk space" in command or "storage" in command:
        response = get_disk_usage()

    elif "speed test" in command:
        response = run_speed_test()

    else:
        response = "Gomen, Senpai~ I couldn't understand that!"

    threading.Thread(target=luna_speak, args=(response,)).start()
    return response
@app.context_processor
def inject_offline_flag():
    return dict(offline_mode=OFFLINE_MODE)

if __name__ == "__main__":
    app.run(debug=True)
