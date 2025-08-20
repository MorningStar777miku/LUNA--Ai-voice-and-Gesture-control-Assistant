import os
import time
import pandas as pd
from modules.interactions import luna_speak  # Import the luna_speak function

EXCEL_FILE = "data/apps.xlsx"

def find_exe_files():
    """Scan system directories for installed .exe files."""
    apps = []
    program_dirs = ["C:\\Program Files", os.path.expanduser("~\\AppData\\Local")]
    ignore_patterns = ["uninstall", "setup", "helper", "update"]

    for directory in program_dirs:
        if os.path.exists(directory):
            print(f"🔍 Scanning: {directory}")
            luna_speak(f"Scanning {directory}")
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".exe") and not any(p in file.lower() for p in ignore_patterns):
                        try:
                            app_name = os.path.splitext(file)[0]
                            exe_path = os.path.join(root, file)
                            apps.append([app_name.capitalize(), exe_path, ""])
                        except PermissionError:
                            print(f"⚠️ Skipping inaccessible file: {file}")
                            luna_speak(f"Skipping inaccessible file: {file}")

    return apps

def update_excel():
    """Updates `apps.xlsx` only if a scan is needed."""
    try:
        if os.path.exists(EXCEL_FILE):
            last_modified = os.path.getmtime(EXCEL_FILE)
            if time.time() - last_modified < 86400:  # 24 hours
                print("✅ Using cached installed apps list.")
                luna_speak("Using cached installed apps list.")
                return

        installed_apps = find_exe_files()
        df = pd.DataFrame(installed_apps, columns=["App Name", "EXE Path", "Web Link"])
        df.to_excel(EXCEL_FILE, index=False)

        print(f"\n✅ {len(installed_apps)} apps saved to {EXCEL_FILE}")
        luna_speak(f"{len(installed_apps)} apps saved to {EXCEL_FILE}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        luna_speak(f"An error occurred: {e}")

if __name__ == "__main__":
    print("\n🔹 Starting app scan...\n")
    luna_speak("Starting app scan")
    update_excel()
    luna_speak("App scan completed")