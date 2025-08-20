import os
import webbrowser
import requests
import pywhatkit as kit
import wikipedia
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from modules.interactions import luna_speak
from modules.cache_manager import get_cached_summary, save_to_cache
from modules.network_utils import is_online

# Load Gemini API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini
use_gemini = False
gemini_model = None
try:
    if GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash-latest")
        use_gemini = True
except ImportError:
    print("⚠️ Gemini module not installed. Gemini features disabled.")

def chat_with_gemini(prompt):
    if not use_gemini or gemini_model is None:
        return "❌ Gemini API not configured."
    try:
        response = gemini_model.generate_content(prompt)
        if response:
            return getattr(response, "text", None) or getattr(response.candidates[0], "text", "❌ No response from Gemini.")
        return "❌ No response from Gemini."
    except Exception as e:
        return f"❌ Gemini API Error: {e}"

def search_wikipedia(query):
    try:
        wikipedia.set_lang("en")
        return wikipedia.summary(query, sentences=2)
    except Exception:
        return ""  # Wikipedia is optional fallback

def fetch_website_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = " ".join(p.get_text() for p in paragraphs[:5])
        if len(content) < 100:
            return ""
        return content
    except Exception:
        return ""

def find_youtube(query):
    if not query.strip():
        return "❌ No valid search term provided."
    luna_speak(f"Senpai~, searching YouTube for '{query}'!")
    try:
        kit.playonyt(query)
        return f"🎬 Playing '{query}' on YouTube..."
    except Exception as e:
        return f"❌ YouTube Search Error: {e}"

def explore_website(query):
    """Ask Gemini for relevant URLs for the query and open the best one."""
    prompt = (
        f"Provide one relevant website URL about: {query}. "
        f"Just give the URL without any explanation."
    )
    response = chat_with_gemini(prompt)
    if "http" in response:
        # Extract URL from response
        lines = response.splitlines()
        url = None
        for line in lines:
            if line.startswith("http"):
                url = line.strip()
                break
        if url:
            luna_speak(f"Senpai~, opening {url} for you.")
            webbrowser.open(url)
            return f"🌐 Opening: {url}"
    return "❌ Could not find a suitable URL to open."

def find(query):
    """Search YouTube and open first video."""
    luna_speak(f"Senpai~, searching for '{query}' on YouTube! 🎬")
    try:
        kit.playonyt(query)
        return f"🎬 Opening YouTube video for '{query}'!"
    except Exception as e:
        return f"❌ Failed to search YouTube: {e}"

def search(query, detailed=False):
    """Unified and optimized search using cache, Wikipedia, and Gemini."""
    query = query.strip().lower()
    
    # Check cache
    cached = get_cached_summary(query)
    if cached:
        response = f"(Cached Summary)\n{cached}"
        luna_speak(response)
        return response

    # Offline fallback
    if not is_online():
        return "I'm offline and I don't have this information saved, Senpai~"

    # Try Wikipedia first if detailed is not requested
    wiki_summary = search_wikipedia(query)
    if wiki_summary and not detailed:
        save_to_cache(query, wiki_summary)
        luna_speak(wiki_summary)
        return wiki_summary

    # Use Gemini for detailed or fallback info
    prompt_parts = []
    if wiki_summary:
        prompt_parts.append(f"Wikipedia summary:\n{wiki_summary}\n")
    prompt_parts.append(f"Provide {'a detailed' if detailed else 'a brief'} explanation about: {query}")

    prompt = "\n".join(prompt_parts)
    response = chat_with_gemini(prompt)

    if "❌" not in response:
        save_to_cache(query, response)
        luna_speak(f"Senpai~, here’s what I found: {response}")
        return response

    return "Gomen~, I couldn't find what you're looking for, Senpai~ 😔"

def explore(query):
    """Get URL from Gemini and open it in browser."""
    prompt = f"Provide one relevant website URL about: {query}. Just give the URL."
    response = chat_with_gemini(prompt)
    if response and "http" in response:
        for line in response.splitlines():
            if line.startswith("http"):
                url = line.strip()
                webbrowser.open(url)
                luna_speak(f"Senpai~, opening {url} for you.")
                return f"🌐 Opening website: {url}"
    return "Gomen~, Senpai~ I couldn't find a suitable website to open."

if __name__ == "__main__":
    command = input("Enter command (find/search/explore): ").strip().lower()
    query = input("Enter your query: ").strip()

    if command == "find":
        print(find_youtube(query))
    elif command == "search":
        detail_choice = input("Do you want a detailed answer? (yes/no): ").strip().lower()
        detailed = detail_choice in ("yes", "y")
        print(search(query, detailed=detailed))
    elif command == "explore":
        print(explore_website(query))
    else:
        print("❌ Invalid command. Use 'find', 'search', or 'explore'.")
