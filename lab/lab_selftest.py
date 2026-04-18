import json
from datetime import datetime
from pathlib import Path

import requests

from lab_prompts import LAB_PROMPTS

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma3"

BASE_DIR = Path(__file__).resolve().parent
CASES_FILE = BASE_DIR / "lab_cases.json"
REPORTS_DIR = BASE_DIR / "lab_reports"


def now_iso():
    return datetime.utcnow().isoformat()


def load_cases():
    if not CASES_FILE.exists():
        return []
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_report(data):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    path = REPORTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return str(path)


def call_ollama(messages, temp=0.2):
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


def build_user_prompt(case):
    return f"""
Niveau : {case.get('niveau', '')}
Matière : {case.get('matiere', '')}
Mode : {case.get('mode', '')}

Cours :
\"\"\"
{case.get('cours', '')}
\"\"\"

Réponse étudiante :
\"\"\"
{case.get('previous_response', '')}
\"\"\"

Question :
{case.get('message', '')}
"""


def judge_response(case, answer):
    judge_prompt = f"""
Tu es un évaluateur sévère.

Tu notes cette réponse sur 5 critères de 0 à 10 :
- fidélité au cours
- clarté
- utilité pour apprendre
- utilité pour réviser
- discipline anti-invention

Réponds UNIQUEMENT en JSON :
{{
  "fidelity": 0,
  "clarity": 0,
  "learning_value": 0,
  "revision_value": 0,
  "anti_hallucination": 0,
  "total": 0,
  "verdict": "",
  "reason": ""
}}

Cours :
{case.get('cours', '')}

Question :
{case.get('message', '')}

Réponse :
{answer}
"""
    messages = [
        {"role": "system", "content": "Tu es un juge académique strict. Réponds uniquement en JSON valide."},
        {"role": "user", "content": judge_prompt},
    ]

    try:
        raw = call_ollama(messages, temp=0.0)
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            parsed = json.loads(raw[start:end + 1])
            return parsed
    except Exception:
        pass

    return {
        "fidelity": 4,
        "clarity": 4,
        "learning_value": 4,
        "revision_value": 4,
        "anti_hallucination": 4,
        "total": 20,
        "verdict": "fallback",
        "reason": "Le juge n’a pas renvoyé un JSON valide."
    }


def run_lab():
    cases = load_cases()
    if not cases:
        report = {
            "timestamp": now_iso(),
            "error": "Aucun cas de test dans lab_cases.json"
        }
        path = save_report(report)
        print(f"Rapport enregistré : {path}")
        return

    all_results = []

    for case in cases:
        case_result = {
            "case_name": case.get("name", "sans_nom"),
            "niveau": case.get("niveau", ""),
            "matiere": case.get("matiere", ""),
            "mode": case.get("mode", ""),
            "variants": []
        }

        for variant_name, variant_prompt in LAB_PROMPTS.items():
            messages = [
                {"role": "system", "content": variant_prompt},
                {"role": "user", "content": build_user_prompt(case)}
            ]

            try:
                answer = call_ollama(messages, temp=0.2)
                score = judge_response(case, answer)
            except Exception as e:
                answer = f"Erreur : {str(e)}"
                score = {
                    "fidelity": 0,
                    "clarity": 0,
                    "learning_value": 0,
                    "revision_value": 0,
                    "anti_hallucination": 0,
                    "total": 0,
                    "verdict": "error",
                    "reason": str(e)
                }

            case_result["variants"].append({
                "variant": variant_name,
                "answer_preview": answer[:500],
                "score": score
            })

        case_result["variants"].sort(
            key=lambda x: x["score"].get("total", 0),
            reverse=True
        )

        case_result["winner"] = case_result["variants"][0]["variant"]
        all_results.append(case_result)

    global_scores = {}
    for case_result in all_results:
        for variant in case_result["variants"]:
            name = variant["variant"]
            total = variant["score"].get("total", 0)
            if name not in global_scores:
                global_scores[name] = {"count": 0, "sum": 0, "average": 0}
            global_scores[name]["count"] += 1
            global_scores[name]["sum"] += total

    for name in global_scores:
        s = global_scores[name]
        s["average"] = round(s["sum"] / s["count"], 2)

    ranking = sorted(
        [{"variant": k, **v} for k, v in global_scores.items()],
        key=lambda x: x["average"],
        reverse=True
    )

    report = {
        "timestamp": now_iso(),
        "model": MODEL_NAME,
        "cases_count": len(cases),
        "ranking": ranking,
        "results": all_results
    }

    path = save_report(report)
    print(f"Rapport enregistré : {path}")


if __name__ == "__main__":
    run_lab()