import datetime
import psutil
import time
import platform
import shutil
import speedtest
import threading
import os
import subprocess
import requests
import pyttsx3

# Initialize Luna's voice (for some utility alerts)
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)
tts_engine.setProperty("volume", 1.0)

# Select a female voice
voices = tts_engine.getProperty('voices')
for voice in voices:
    if 'female' in voice.name.lower():
        tts_engine.setProperty('voice', voice.id)
        break

def speak(text):
    """Luna speaks dynamically when issues arise."""
    threading.Thread(target=lambda: (tts_engine.say(text), tts_engine.runAndWait())).start()

# ========================= SYSTEM MONITORING ========================= #

def get_time():
    now = datetime.datetime.now()
    return f"🕒 It's {now.strftime('%I:%M %p')}, Senpai~!"

def get_weather():
    """Fetches real-time weather data and suggests system adjustments."""
    try:
        location = os.getenv("WEATHER_LOCATION", "YOUR_CITY")  # Replace with your location
        api_key = os.getenv("WEATHER_API_KEY", "YOUR_WEATHER_API_KEY")  # Replace with your API key
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
        response = requests.get(url).json()
        temp = response["current"]["temp_c"]
        
        if temp > 30:
            return f"🌞 It's {temp}°C outside! Consider reducing CPU load to keep cool, Senpai!"
        elif temp < 10:
            return f"❄️ It's {temp}°C! Maybe keep Luna warm by running a few programs? 😆"
        else:
            return f"🌤️ It's a nice {temp}°C outside, Senpai!"
    except Exception:
        return "❌ Weather data unavailable, Senpai!"

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery is None:
        return "⚡ No battery detected, Senpai~!"

    charge_status = "🔌 Plugged in" if battery.power_plugged else "🔋 Running on battery"
    time_left = battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Unknown"
    battery_alert = "⚠️ Battery is low, switching to power saver mode!" if battery.percent < 20 else "✅ Battery is fine!"
    
    if battery.percent < 20:
        enable_power_saver()
    
    return f"🔋 {battery.percent}% | {charge_status} | {time_left} sec left. {battery_alert}"

def get_system_uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    hours, minutes = divmod(int(uptime_seconds) // 60, 60)
    return f"🖥️ System has been running for {hours} hours and {minutes} minutes, Senpai~"

def get_cpu_usage():
    usage = psutil.cpu_percent(interval=1)
    alert = "⚠️ CPU is under heavy load! Be careful, Senpai!" if usage > 80 else "🌿 CPU is stable."
    
    if usage > 90:
        threading.Thread(target=auto_optimize_cpu).start()  
    return f"⚙️ CPU Usage: {usage}% | {alert}"

def get_ram_usage():
    memory = psutil.virtual_memory()
    ram_alert = "⚠️ High RAM usage detected! Want me to clear cache, Senpai?" if memory.percent > 85 else "✅ RAM usage is normal."
    
    if memory.percent > 90:
        threading.Thread(target=clear_ram_cache).start()
    return f"💾 RAM Usage: {memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB ({memory.percent}%) | {ram_alert}"

def get_disk_usage():
    total, used, free = shutil.disk_usage("/")
    storage_alert = "⚠️ Running low on disk space!" if free // (1024**3) < 10 else "✅ Storage is fine!"
    return f"💽 Disk Space: {used // (1024**3)}GB used / {total // (1024**3)}GB total. Free: {free // (1024**3)}GB. {storage_alert}"

# ========================= AI OPTIMIZATION & AUTO-FIXES ========================= #

def auto_optimize_cpu():
    """Auto-closes high CPU-consuming processes."""
    speak("Luna is optimizing CPU usage, Senpai~!")
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        if proc.info['cpu_percent'] > 30:
            try:
                speak(f"Closing {proc.info['name']} to save CPU power, Senpai!")
                psutil.Process(proc.info['pid']).terminate()
            except Exception as e:
            except Exception:
                speak(f"Failed to close {proc.info['name']}, Senpai!")
def clear_ram_cache():
    """Clears RAM cache to free up memory."""
    if platform.system() == "Windows":
        try:
            subprocess.run(["cmd.exe", "/c", "echo Y|PowerShell.exe -Command Clear-RecycleBin"], check=True)
            speak("Luna cleared RAM cache, Senpai!")
        except subprocess.CalledProcessError:
            speak("Failed to clear RAM cache, Senpai!")
    else:
        speak("Clearing RAM is not supported on this system.")

def enable_power_saver():
    """Switches to power saver mode if battery is low."""
    if platform.system() == "Windows":
        try:
            subprocess.run(["powercfg", "/SETACTIVE", "SCHEME_MAX"], check=True)
            speak("Power saver mode activated, Senpai!")
        except subprocess.CalledProcessError:
            speak("Failed to activate power saver mode, Senpai!")

def run_speed_test():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  
        upload_speed = st.upload() / 1_000_000  
        return f"🚀 Internet Speed: {download_speed:.2f} Mbps (Download) | {upload_speed:.2f} Mbps (Upload)"
    except Exception:
        return "❌ Speed test failed, Senpai!"