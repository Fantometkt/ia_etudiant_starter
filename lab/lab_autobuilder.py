import json
from datetime import datetime
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_FILE = BASE_DIR / "lab_prompts.py"
AUTOLOG_FILE = BASE_DIR / "lab_autolog.json"
CANDIDATES_DIR = BASE_DIR / "lab_candidates"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma3"


def now_iso():
    return datetime.utcnow().isoformat()


def load_existing_prompts_text():
    if not PROMPTS_FILE.exists():
        return ""
    return PROMPTS_FILE.read_text(encoding="utf-8")


def load_autolog():
    if not AUTOLOG_FILE.exists():
        return []
    try:
        with open(AUTOLOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_autolog(data):
    with open(AUTOLOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def call_ollama(messages, temp=0.4):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temp
        }
    }
    r = requests.post(OLLAMA_URL, json=payload)
    r.raise_for_status()
    data = r.json()
    return data.get("message", {}).get("content", "").strip()


def build_generation_prompt(existing_prompts_text):
    return f"""
Tu es un concepteur de prompts pour une IA étudiante.

MISSION :
Créer UNE NOUVELLE variante de prompt expérimentale pour améliorer l'IA pédagogique.

OBJECTIF :
- améliorer la compréhension réelle
- éviter de faire le travail à la place de l'étudiant
- limiter les hallucinations
- favoriser l'assimilation
- améliorer la clarté et la hiérarchisation

CONTRAINTES :
- tu ne modifies pas le système principal
- tu proposes seulement UNE nouvelle variante
- elle doit être différente des variantes déjà présentes
- elle doit être utilisable dans un fichier Python

PROMPTS EXISTANTS :
{existing_prompts_text}

FORMAT OBLIGATOIRE :
Réponds UNIQUEMENT en JSON valide :

{{
  "variant_name": "nom_court_sans_espace",
  "goal": "but de la variante",
  "prompt_text": "texte complet du prompt"
}}
"""


def generate_candidate():
    existing = load_existing_prompts_text()

    messages = [
        {
            "role": "system",
            "content": "Tu es un expert en prompts pédagogiques, rigoureux et créatif."
        },
        {
            "role": "user",
            "content": build_generation_prompt(existing)
        }
    ]

    raw = call_ollama(messages, temp=0.5)

    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Réponse JSON introuvable")

    parsed = json.loads(raw[start:end + 1])

    variant_name = parsed["variant_name"].strip()
    goal = parsed["goal"].strip()
    prompt_text = parsed["prompt_text"].strip()

    if not variant_name or not prompt_text:
        raise ValueError("Variant incomplète")

    return {
        "variant_name": variant_name,
        "goal": goal,
        "prompt_text": prompt_text
    }


def save_candidate(candidate):
    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{candidate['variant_name']}.json"
    path = CANDIDATES_DIR / filename

    payload = {
        "created_at": now_iso(),
        "variant_name": candidate["variant_name"],
        "goal": candidate["goal"],
        "prompt_text": candidate["prompt_text"]
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return str(path)


def main():
    candidate = generate_candidate()
    path = save_candidate(candidate)

    autolog = load_autolog()
    autolog.append({
        "timestamp": now_iso(),
        "status": "generated",
        "variant_name": candidate["variant_name"],
        "goal": candidate["goal"],
        "file": path
    })
    autolog = autolog[-100:]
    save_autolog(autolog)

    print(f"Candidat généré : {path}")


if __name__ == "__main__":
    main()