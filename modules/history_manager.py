import json
import os
import difflib

HISTORY_FILE = "search_history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r") as file:
        return json.load(file)

def save_to_history(query, result):
    history = load_history()
    history[query.lower()] = result
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

def get_from_history(query):
    history = load_history()
    query = query.lower()
    if query in history:
        return history[query]
    
    # Try fuzzy matching
    close_matches = difflib.get_close_matches(query, history.keys(), n=1, cutoff=0.7)
    if close_matches:
        return f"(Fuzzy match from: '{close_matches[0]}')\n{history[close_matches[0]]}"
    
    return None

def get_all_history():
    return load_history()
