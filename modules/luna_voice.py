import pyttsx3

def luna_speak(text):
    print(f"\n🗣️ Luna says: {text}")
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)
    engine.setProperty("volume", 1)
    engine.say(text)
    engine.runAndWait()
