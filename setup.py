import os
import subprocess
import time
import webbrowser
import requests
from dotenv import load_dotenv
from modules.interactions import luna_speak
from modules.network_utils import is_online  # ✅ Auto-detect connectivity

# Load environment variables
load_dotenv()
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
EXCEL_FILE = os.path.join("data", "apps.xlsx")

def install_requirements():
    print("\n🔹 Installing required packages...\n")
    luna_speak("Installing required packages...")

    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        luna_speak("requirements file is missing.")
        exit(1)

    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully!\n")
        luna_speak("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Check your internet connection.")
        luna_speak("Failed to install dependencies. Please check your connection.")
        exit(1)

def scan_installed_apps():
    os.makedirs("data", exist_ok=True)
    message = "Updating existing apps.xlsx..." if os.path.exists(EXCEL_FILE) else "Creating a new apps list..."
    print(f"\n🔹 {message}\n")
    luna_speak(message)

    try:
        subprocess.run(["python", "modules/check_installed_apps.py"], check=True)
        print("✅ Installed apps scan completed.\n")
        luna_speak("Installed apps scan completed.")
    except subprocess.CalledProcessError:
        print("❌ Failed to scan installed apps.")
        luna_speak("Failed to scan installed applications.")

def wait_for_server(port, timeout=10):
    url = f"http://127.0.0.1:{port}"
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if requests.get(url).status_code == 200:
                return True
        except requests.ConnectionError:
            time.sleep(0.5)
    return False

def start_luna():
    print("\n🔹 Starting Luna AI Assistant...\n")
    luna_speak("Starting Luna AI Assistant...")

    try:
        subprocess.Popen("python main.py", shell=True, cwd=os.getcwd())
    except Exception as e:
        print(f"❌ Failed to start Luna AI: {e}")
        luna_speak("Failed to start Luna AI.")
        return

    if wait_for_server(FLASK_PORT):
        print(f"\n✅ Luna AI is running! Access it at http://127.0.0.1:{FLASK_PORT}/\n")
        luna_speak("Luna AI is now online.")
        webbrowser.open(f"http://127.0.0.1:{FLASK_PORT}/")
    else:
        print("⚠️ Luna AI failed to start in time.")
        luna_speak("Luna AI failed to start.")

def start_gesture_control():
    print("\n🖐️ Launching gesture control system...\n")
    luna_speak("Launching gesture control system.")
    try:
        subprocess.Popen("python hand_gesture_control-main/gesture_mouse.py", shell=True)
    except Exception as e:
        print(f"❌ Failed to start gesture control: {e}")
        luna_speak("Gesture control failed to launch.")

def show_connection_status():
    if is_online():
        print("🌐 Online mode enabled.")
        luna_speak("Internet connection detected. Online mode activated.")
    else:
        print("🔌 Offline mode detected. Using memory only.")
        luna_speak("Offline mode activated. I will use only memory.")

if __name__ == "__main__":
    print("\n🚀 Setting up LUNA...\n")
    luna_speak("Setting up Luna Assistant.")

    show_connection_status()
    install_requirements()
    scan_installed_apps()
    start_luna()
    start_gesture_control()
