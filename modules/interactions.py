
from modules.app_handler import launch_app
from modules.luna_voice import luna_speak
import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")
for voice in voices:
    if "zira" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        break

def luna_speak(text):
    print(f"🗣️ Luna says: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠️ Error in TTS: {e}")

def interact_with_luna(command):
    if "launch" in command.lower():
        app_name = command.lower().replace("launch", "").strip()
        response = launch_app(app_name)
    else:
        response = f"Gomen~ I don’t understand what '{command}' means yet, Senpai~ 🥺"

    luna_speak(response)
    return response
