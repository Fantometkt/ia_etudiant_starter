import re
from utils import *
from prompts import JUDGE_SYSTEM_PROMPT
from llm import call_ollama

REQUIRED_JUDGE_KEYS = {
    "fidelity",
    "level_fit",
    "clarity",
    "revision_value",
    "enrichment_quality",
}

def parse_score(value):
    if isinstance(value, (int, float)):
        return max(0, min(10, int(round(float(value)))))

    if value is None:
        return 0

    s = str(value).strip().lower()

    if s.isdigit():
        return max(0, min(10, int(s)))

    s = s.replace(",", ".")
    match = re.search(r"-?\d+(\.\d+)?", s)
    if not match:
        return 0

    try:
        num = float(match.group(0))
    except Exception:
        return 0

    return max(0, min(10, int(round(num))))

def build_verdict(total):
    if total >= 45:
        return "exceptionnel"
    if total >= 40:
        return "très fort"
    if total >= 35:
        return "bon"
    if total >= 28:
        return "moyen"
    if total >= 20:
        return "faible"
    return "très faible"

def is_valid_judgment_dict(parsed):
    if not isinstance(parsed, dict):
        return False
    missing = [k for k in REQUIRED_JUDGE_KEYS if k not in parsed]
    return not missing

def normalize_judgment(parsed):
    fidelity = parse_score(parsed.get("fidelity", 0))
    level_fit = parse_score(parsed.get("level_fit", 0))
    clarity = parse_score(parsed.get("clarity", 0))
    revision_value = parse_score(parsed.get("revision_value", 0))
    enrichment_quality = parse_score(parsed.get("enrichment_quality", 0))

    total = fidelity + level_fit + clarity + revision_value + enrichment_quality

    risk_flags = parsed.get("risk_flags", [])
    if not isinstance(risk_flags, list):
        risk_flags = []

    return {
        "fidelity": fidelity,
        "level_fit": level_fit,
        "clarity": clarity,
        "revision_value": revision_value,
        "enrichment_quality": enrichment_quality,
        "total": total,
        "verdict": build_verdict(total),
        "improvement_hint": clean(parsed.get("improvement_hint")) or "Aucune indication précise.",
        "main_weakness": clean(parsed.get("main_weakness")) or "Aucune faiblesse principale identifiée.",
        "risk_flags": risk_flags[:6]
    }

def fallback_judgment(reason, extra_flag=None):
    flags = ["judge_fallback"]
    if extra_flag:
        flags.append(extra_flag)

    return {
        "fidelity": 4,
        "level_fit": 4,
        "clarity": 4,
        "revision_value": 4,
        "enrichment_quality": 4,
        "total": 20,
        "verdict": "fallback",
        "improvement_hint": reason,
        "main_weakness": "Évaluation automatique incomplète.",
        "risk_flags": flags
    }

def judge(answer, message, niveau, matiere, cours):
    prompt = f"""
Niveau : {niveau}
Matière : {matiere}

Cours :
{cours}

Question :
{message}

Réponse :
{answer}
"""

    messages = [
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    try:
        raw = call_ollama(messages, temp=0.0)
        parsed = extract_json(raw)

        if not is_valid_judgment_dict(parsed):
            return fallback_judgment(
                "Le juge n’a pas renvoyé un JSON complet et valide.",
                "invalid_or_incomplete_json"
            )

        return normalize_judgment(parsed)

    except Exception as e:
        return fallback_judgment(
            f"Erreur du juge : {str(e)}",
            "judge_exception"
        )