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

RISK_FLAG_PENALTIES = {
    "hallucination": 4,
    "hors_sujet": 3,
    "out_of_scope": 3,
    "mode_mismatch": 2,
    "paraphrase": 2,
    "padding": 2,
    "repetition": 1,
    "judge_fallback": 999,
}

VERY_SHORT_ANSWER_THRESHOLD = 20
VERY_LONG_ANSWER_THRESHOLD = 3500


# ========================
# 🔢 PARSING SCORES
# ========================

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


# ========================
# 🧠 VERDICT
# ========================

def build_verdict(total):
    if total >= 45:
        return "exceptionnel"
    if total >= 40:
        return "très fort"
    if total >= 35:
        return "bon"
    if total >= 28:
        return "moyen"
    if total >= 15:
        return "faible"
    return "très faible"


# ========================
# ✅ VALIDATION
# ========================

def is_valid_judgment_dict(parsed):
    if not isinstance(parsed, dict):
        return False

    missing = [k for k in REQUIRED_JUDGE_KEYS if k not in parsed]
    if missing:
        return False

    for key in REQUIRED_JUDGE_KEYS:
        if parsed.get(key) is None:
            return False

    return True


# ========================
# 🧹 RISK FLAGS
# ========================

def normalize_risk_flags(risk_flags):
    if not isinstance(risk_flags, list):
        return []

    cleaned = []
    for flag in risk_flags:
        txt = clean(flag).lower()
        if txt:
            cleaned.append(txt)

    # déduplication en gardant l'ordre
    return list(dict.fromkeys(cleaned))[:8]


# ========================
# ⚖️ HEURISTIC PENALTIES
# ========================

def compute_risk_penalty(risk_flags):
    penalty = 0

    for flag in risk_flags:
        for key, malus in RISK_FLAG_PENALTIES.items():
            if key in flag:
                penalty += malus

    return penalty


def heuristic_penalty_from_answer(answer):
    ans = clean(answer)
    ans_lower = ans.lower()

    penalty = 0
    flags = []

    if not ans:
        penalty += 8
        flags.append("empty_answer")

    if len(ans) < VERY_SHORT_ANSWER_THRESHOLD:
        penalty += 3
        flags.append("too_short")

    if len(ans) > VERY_LONG_ANSWER_THRESHOLD:
        penalty += 2
        flags.append("too_long")

    error_markers = [
        "traceback",
        "importerror",
        "syntaxerror",
        "erreur ia",
        "erreur de génération",
    ]
    if any(marker in ans_lower for marker in error_markers):
        penalty += 10
        flags.append("generation_error_output")

    return penalty, flags


# ========================
# 📊 NORMALISATION
# ========================

def normalize_judgment(parsed, answer=""):
    fidelity = parse_score(parsed.get("fidelity", 0))
    level_fit = parse_score(parsed.get("level_fit", 0))
    clarity = parse_score(parsed.get("clarity", 0))
    revision_value = parse_score(parsed.get("revision_value", 0))
    enrichment_quality = parse_score(parsed.get("enrichment_quality", 0))

    risk_flags = normalize_risk_flags(parsed.get("risk_flags", []))

    base_total = (
        fidelity
        + level_fit
        + clarity
        + revision_value
        + enrichment_quality
    )

    risk_penalty = compute_risk_penalty(risk_flags)
    heuristic_penalty, heuristic_flags = heuristic_penalty_from_answer(answer)

    total = max(0, base_total - risk_penalty - heuristic_penalty)

    final_risk_flags = list(dict.fromkeys(risk_flags + heuristic_flags))[:8]

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
        "risk_flags": final_risk_flags,
        "is_fallback": False
    }


# ========================
# 🚨 FALLBACK
# ========================

def fallback_judgment(reason, extra_flag=None):
    flags = ["judge_fallback"]

    if extra_flag:
        flags.append(extra_flag)

    return {
        "fidelity": 1,
        "level_fit": 1,
        "clarity": 1,
        "revision_value": 1,
        "enrichment_quality": 1,
        "total": 5,
        "verdict": "fallback",
        "improvement_hint": reason,
        "main_weakness": "Évaluation automatique incomplète.",
        "risk_flags": flags,
        "is_fallback": True
    }


# ========================
# 🧱 PROMPT JUDGE
# ========================

def build_judge_prompt(answer, message, niveau, matiere, cours):
    return f"""
Niveau : {niveau}

Matière : {matiere}

Cours :
{cours}

Question :
{message}

Réponse :
{answer}
""".strip()


# ========================
# 🎯 JUDGE PRINCIPAL
# ========================

def judge(answer, message, niveau, matiere, cours):
    prompt = build_judge_prompt(
        answer=answer,
        message=message,
        niveau=niveau,
        matiere=matiere,
        cours=cours
    )

    messages = [
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    try:
        raw = call_ollama(messages, temp=0.0)

        if not raw or len(raw.strip()) < 10:
            return fallback_judgment(
                "Réponse vide ou trop courte du juge.",
                "empty_judge_output"
            )

        parsed = extract_json(raw)

        if not is_valid_judgment_dict(parsed):
            return fallback_judgment(
                "Le juge n’a pas renvoyé un JSON valide.",
                "invalid_json"
            )

        return normalize_judgment(parsed, answer=answer)

    except Exception as e:
        return fallback_judgment(
            f"Erreur du juge : {str(e)}",
            "judge_exception"
        )