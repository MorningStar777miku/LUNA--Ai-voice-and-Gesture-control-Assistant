import os
import pandas as pd
import subprocess
import difflib
# from moimdules.luna_voice import luna_speak


EXCEL_FILE = "data/apps.xlsx"

def get_installed_apps():
    if not os.path.exists(EXCEL_FILE):
        return {}

    df = pd.read_excel(EXCEL_FILE, index_col="App Name")
    return df.to_dict(orient="index")

def fuzzy_match_app(command, installed_apps):
    command = command.lower().strip()
    matches = sorted(
        installed_apps.keys(),
        key=lambda x: difflib.SequenceMatcher(None, command, x.lower()).ratio(),
        reverse=True
    )
    return matches[0] if matches and difflib.SequenceMatcher(None, command, matches[0].lower()).ratio() > 0.5 else None

def update_usage_count(app_name):
    if not os.path.exists(EXCEL_FILE):
        return

    df = pd.read_excel(EXCEL_FILE, index_col="App Name")
    if app_name in df.index:
        df.at[app_name, "Usage Count"] += 1
        df.at[app_name, "Last Used"] = pd.Timestamp.now()
        df.to_excel(EXCEL_FILE)

def auto_close_background_apps():
    if not os.path.exists(EXCEL_FILE):
        return

    df = pd.read_excel(EXCEL_FILE)
    if "Last Used" not in df.columns:
        return

    df["Last Used"] = pd.to_datetime(df["Last Used"], errors="coerce")
    unused_apps = df.sort_values("Last Used", ascending=True).head(3)

    for _, row in unused_apps.iterrows():
        try:
            exe_name = os.path.basename(row["EXE Path"])
            subprocess.run(["taskkill", "/F", "/IM", exe_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def open_application(command):
    installed_apps = get_installed_apps()
    command_lower = command.lower()

    if command_lower in installed_apps:
        return launch_app(command_lower, installed_apps[command_lower]["EXE Path"])

    matched_app = fuzzy_match_app(command_lower, installed_apps)
    if matched_app:
        return launch_app(matched_app, installed_apps[matched_app]["EXE Path"])

    return f"⚠️ Gomen, Senpai~ I couldn't find {command} on your system!"

def launch_app(app_name, exe_path):
    try:
        print(f"🚀 Launching: {app_name}")
        print(f"📂 Executable Path: {exe_path}")
        if " " in exe_path:
            exe_path = f'"{exe_path}"'
        auto_close_background_apps()
        subprocess.Popen(exe_path, shell=True)
        update_usage_count(app_name)
        return f"✨ Opening {app_name}, Senpai~!"
    except Exception as e:
        return f"⚠️ Gomen, Senpai~ I found {app_name}, but I couldn't open it. Error: {e}"
