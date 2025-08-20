import os
import json

CACHE_FILE = "page_cache.json"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as file:
        return json.load(file)

def save_to_cache(query, content):
    cache = load_cache()
    cache[query.lower()] = content
    with open(CACHE_FILE, "w") as file:
        json.dump(cache, file, indent=4)

def get_cached_summary(query):
    cache = load_cache()
    return cache.get(query.lower())
