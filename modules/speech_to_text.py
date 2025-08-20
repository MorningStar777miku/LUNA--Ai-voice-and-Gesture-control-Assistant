import speech_recognition as sr
import pyttsx3
import time

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')

female_voice = None
for voice in voices:
    if "zira" in voice.name.lower() or "female" in voice.name.lower():
        female_voice = voice.id
        break

if female_voice:
    engine.setProperty('voice', female_voice)
else:
    print("Warning: No female voice found. Using default voice.")

def speak(text):
    """Speaks the given text using the initialized TTS engine."""
    engine.say(text)
    engine.runAndWait()
    time.sleep(1)  # Add a short pause to prevent Luna from picking up its own voice

def listen_to_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        time.sleep(1)  # Short pause before listening
        try:
            audio = recognizer.listen(source, timeout=5)
        except sr.WaitTimeoutError:
            speak("I didn't hear anything.")
            return None

    try:
        command = recognizer.recognize_google(audio).lower()
        return command
    except sr.UnknownValueError:
        try:
            command = recognizer.recognize_sphinx(audio).lower()  # Offline alternative
            return command
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return None
    except sr.RequestError:
        speak("Sorry, there was an error with the speech recognition service.")
        return None

def main():
    while True:
        command = listen_to_command()
        if command:
            speak(f"You said: {command}")
            time.sleep(2)
            speak("Please say your next command when ready.")
        else:
            speak("Please try again.")

if __name__ == "__main__":
    speak("Hello, how can I assist you today?")
    main()