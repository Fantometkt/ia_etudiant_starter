import json
import statistics
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
        "options": {"temperature": temp}
    }
    r = requests.post(OLLAMA_URL, json=payload)
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "").strip()


# ========================
# 🧠 PROMPT USER
# ========================

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


# ========================
# ⚖️ JUGE ULTRA STRICT
# ========================

def judge_response(case, answer):
    judge_prompt = f"""
Tu es un évaluateur ÉLITE extrêmement sévère.

RÈGLES :
- 5 = moyen
- 7 = bon
- 8 = très bon
- 9+ = exceptionnel (rare)
- pénalise fortement :
  - paraphrase
  - longueur inutile
  - hors sujet
  - invention
  - manque de hiérarchisation

FORMAT JSON STRICT :

{{
  "fidelity": 0,
  "clarity": 0,
  "learning_value": 0,
  "revision_value": 0,
  "anti_hallucination": 0,
  "structure_quality": 0,
  "density": 0,
  "total": 0,
  "risk_flags": []
}}

Cours :
{case.get('cours', '')}

Question :
{case.get('message', '')}

Réponse :
{answer}
"""

    messages = [
        {"role": "system", "content": "Tu es un juge académique strict. JSON uniquement."},
        {"role": "user", "content": judge_prompt},
    ]

    try:
        raw = call_ollama(messages, temp=0.0)

        start = raw.find("{")
        end = raw.rfind("}")
        parsed = json.loads(raw[start:end + 1])

        # 🔥 recalcul du total
        scores = [
            parsed.get("fidelity", 0),
            parsed.get("clarity", 0),
            parsed.get("learning_value", 0),
            parsed.get("revision_value", 0),
            parsed.get("anti_hallucination", 0),
            parsed.get("structure_quality", 0),
            parsed.get("density", 0),
        ]

        parsed["total"] = sum(scores)

        return parsed

    except Exception:
        return {
            "fidelity": 3,
            "clarity": 3,
            "learning_value": 3,
            "revision_value": 3,
            "anti_hallucination": 3,
            "structure_quality": 3,
            "density": 3,
            "total": 21,
            "risk_flags": ["judge_error"]
        }


# ========================
# 🚀 LAB LOOP
# ========================

def run_lab():
    cases = load_cases()

    if not cases:
        path = save_report({"error": "no cases"})
        print(path)
        return

    all_results = []

    for case in cases:
        case_result = {
            "case_name": case.get("name", ""),
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
                answer = str(e)
                score = {"total": 0, "risk_flags": ["runtime_error"]}

            case_result["variants"].append({
                "variant": variant_name,
                "score": score,
                "preview": answer[:200]
            })

        # tri
        case_result["variants"].sort(
            key=lambda x: x["score"]["total"],
            reverse=True
        )

        case_result["winner"] = case_result["variants"][0]["variant"]
        all_results.append(case_result)

    # ========================
    # 📊 GLOBAL ANALYSIS
    # ========================

    global_scores = {}
    all_totals = []

    for case in all_results:
        for v in case["variants"]:
            name = v["variant"]
            total = v["score"]["total"]
            all_totals.append(total)

            if name not in global_scores:
                global_scores[name] = []

            global_scores[name].append(total)

    ranking = []

    for name, scores in global_scores.items():
        ranking.append({
            "variant": name,
            "average": round(sum(scores) / len(scores), 2),
            "min": min(scores),
            "max": max(scores),
            "variance": round(statistics.variance(scores), 2) if len(scores) > 1 else 0
        })

    ranking.sort(key=lambda x: x["average"], reverse=True)

    report = {
        "timestamp": now_iso(),
        "model": MODEL_NAME,
        "cases": len(cases),
        "ranking": ranking,
        "global_variance": round(statistics.variance(all_totals), 2) if len(all_totals) > 1 else 0,
        "results": all_results
    }

    path = save_report(report)
    print(f"Rapport : {path}")


if __name__ == "__main__":
    run_lab()