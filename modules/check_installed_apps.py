import os
import pandas as pd
from datetime import datetime

EXCEL_FILE = "data/apps.xlsx"

def find_installed_apps():
    """Scan system directories for installed applications and clean names."""
    apps = []
    program_dirs = ["C:\\Program Files", os.path.expanduser("~\\AppData\\Local")]
    ignore_patterns = ["uninstall", "setup", "helper", "update", "test", "tool", "cmd", "debug", "driver"]
    
    for directory in program_dirs:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".exe"):
                        app_name = os.path.splitext(file)[0].replace("_", " ").replace("-", " ").strip()
                        if any(p in app_name.lower() for p in ignore_patterns):
                            continue
                        exe_path = os.path.join(root, file)
                        apps.append([app_name.capitalize(), exe_path, 0])  # Add a usage counter

    unique_apps = {app[0]: app for app in apps}.values()
    return list(unique_apps)

def update_excel():
    """Update `apps.xlsx` with cleaned app names and paths, keeping usage data."""
    os.makedirs("data", exist_ok=True)
    if os.path.exists(EXCEL_FILE):
        old_data = pd.read_excel(EXCEL_FILE, index_col="App Name")
    else:
        old_data = pd.DataFrame(columns=["EXE Path", "Usage Count"])

    installed_apps = find_installed_apps()
    new_data = pd.DataFrame(installed_apps, columns=["App Name", "EXE Path", "Usage Count"])
    new_data.set_index("App Name", inplace=True)

    for app in new_data.index:
        if app in old_data.index:
            new_data.at[app, "Usage Count"] = old_data.at[app, "Usage Count"]

    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data["Last Updated"] = timestamp

    new_data.to_excel(EXCEL_FILE)
    print(f"✅ {len(new_data)} apps saved to {EXCEL_FILE} at {timestamp}")

if __name__ == "__main__":
    print("\n🔹 Scanning installed applications...\n")
    update_excel()