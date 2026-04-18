from utils import *
from prompts import COURSE_ANALYSIS_PROMPT
from memory_manager import extract_focus_topics
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma3"
COURSE_CACHE_FILE = "course_cache.json"

def load_course_cache():
    return load_json_file(COURSE_CACHE_FILE, {})

def save_course_cache(cache):
    save_json_file(COURSE_CACHE_FILE, cache)

def build_request_payload(messages, temp=0.0):
    return {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temp
        }
    }

def call_ollama_course(messages, temp=0.0):
    payload = build_request_payload(messages, temp=temp)
    r = requests.post(OLLAMA_URL, json=payload)
    r.raise_for_status()
    data = r.json()
    return data.get("message", {}).get("content", "").strip()

def fallback_course_analysis(cours):
    text = clean(cours)
    if not text:
        return {
            "notions_centrales": [],
            "mots_cles": [],
            "liens_importants": [],
            "points_a_retenir": [],
            "angles_probables_examen": [],
            "erreurs_classiques": [],
            "zones_floues_ou_manquantes": []
        }

    keywords = extract_focus_topics(text, "", "")
    return {
        "notions_centrales": keywords[:4],
        "mots_cles": keywords[:6],
        "liens_importants": [],
        "points_a_retenir": keywords[:4],
        "angles_probables_examen": [],
        "erreurs_classiques": [],
        "zones_floues_ou_manquantes": []
    }

def analyze_course(cours, niveau, matiere, force=False):
    cours_clean = clean(cours)
    if not cours_clean:
        return fallback_course_analysis(cours_clean)

    key = sha_text(f"{niveau}|{matiere}|{cours_clean}")
    cache = load_course_cache()

    if not force and key in cache:
        return cache[key]

    messages = [
        {"role": "system", "content": COURSE_ANALYSIS_PROMPT},
        {"role": "user", "content": f"Niveau : {niveau}\nMatière : {matiere}\n\nCours :\n{cours_clean}"}
    ]

    try:
        raw = call_ollama_course(messages, temp=0.0)
        parsed = extract_json(raw)
        if isinstance(parsed, dict):
            cache[key] = parsed
            save_course_cache(cache)
            return parsed
    except Exception:
        pass

    fallback = fallback_course_analysis(cours_clean)
    cache[key] = fallback
    save_course_cache(cache)
    return fallback

def format_course_analysis(analysis):
    if not isinstance(analysis, dict):
        return ""

    lines = []
    for key, title in [
        ("notions_centrales", "Notions centrales"),
        ("points_a_retenir", "Points à retenir"),
        ("angles_probables_examen", "Examens")
    ]:
        values = analysis.get(key, [])
        if values:
            lines.append(title + " :")
            for v in values[:5]:
                lines.append(f"- {v}")

    return "\n".join(lines)