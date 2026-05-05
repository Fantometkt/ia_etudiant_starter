import re
from utils import *
from prompts import JUDGE_SYSTEM_PROMPT
from llm import call_ollama
from safety import output_quality_flags


REQUIRED_JUDGE_KEYS = {
    "fidelity",
    "level_fit",
    "clarity",
    "revision_value",
    "enrichment_quality",
}

RISK_FLAG_PENALTIES = {
    "hallucination": 8,
    "hors_sujet": 5,
    "mode_mismatch": 4,
    "paraphrase": 3,
    "padding": 3,
    "repetition": 2,
    "too_long": 2,
    "too_short": 2,
    "weak_pedagogy": 4,
    "vague": 3,

    # Important : on ne pénalise pas automatiquement tout dépassement du cours.
    # On pénalise seulement si c’est non signalé, inutile ou dangereux.
    "bad_out_of_scope": 6,
    "unsupported_claim": 6,
    "uncontrolled_enrichment": 5,

    "technical_error_output": 10,
    "empty_output": 15,
    "judge_fallback": 999,
}


def parse_score(value):
    if isinstance(value, (int, float)):
        return to_int(value, 0, 0, 10)

    s = clean(value).replace(",", ".")
    match = re.search(r"-?\d+(\.\d+)?", s)

    if not match:
        return 0

    return to_int(match.group(0), 0, 0, 10)


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


def normalize_risk_flags(risk_flags):
    flags = []

    for flag in safe_list(risk_flags):
        flag = normalize_key(flag)
        if flag:
            flags.append(flag)

    return list(dict.fromkeys(flags))[:12]


def compute_risk_penalty(flags):
    penalty = 0

    for flag in flags:
        for key, malus in RISK_FLAG_PENALTIES.items():
            if key in flag:
                penalty += malus

    return penalty


def heuristic_pedagogy_flags(answer, mode):
    answer = clean(answer)
    lower = answer.lower()
    flags = []
    penalty = 0
    wc = word_count(answer)

    for f in output_quality_flags(answer):
        flags.append(f)

    if mode in {"expliquer", "reviser", "socratic"}:
    mechanism_markers = [
    "car",
    "donc",
    "autrement dit",
    "cela signifie",
    "la logique",
    "le mécanisme",
    "l’enjeu",
    "c’est important parce que",
    "pour mieux comprendre",
    "en complément utile",
    "dans la logique du cours",
    "ce que ce cours permet de comprendre"
]
        if not any(m in lower for m in mechanism_markers):
            flags.append("mechanism_weak")
            penalty += 2

    if mode == "corriger":
        correction_markers = ["juste", "faux", "incomplet", "manque", "améliorée"]
        found = sum(1 for m in correction_markers if m in lower)

        if found < 3:
            flags.append("correction_not_precise")
            penalty += 4

    if mode == "resumer" and wc > 230:
        flags.append("summary_too_long")
        penalty += 3

    if mode == "a_retenir" and wc > 120:
        flags.append("a_retenir_too_long")
        penalty += 3

    if mode == "quiz":
        if lower.count("?") < 3:
            flags.append("quiz_not_enough_questions")
            penalty += 3

    return penalty, flags

def enrichment_is_controlled(answer):
    lower = clean(answer).lower()

    markers = [
        "pour mieux comprendre",
        "en complément utile",
        "dans la logique du cours",
        "ce que ce cours permet de comprendre",
        "un exemple classique",
        "à ce niveau, il est utile"
    ]

    return any(m in lower for m in markers)

def is_valid_judgment_dict(parsed):
    if not isinstance(parsed, dict):
        return False

    return all(k in parsed for k in REQUIRED_JUDGE_KEYS)


def normalize_judgment(parsed, answer="", mode=""):
    scores = {
        "fidelity": parse_score(parsed.get("fidelity")),
        "level_fit": parse_score(parsed.get("level_fit")),
        "clarity": parse_score(parsed.get("clarity")),
        "revision_value": parse_score(parsed.get("revision_value")),
        "enrichment_quality": parse_score(parsed.get("enrichment_quality")),
    }

    base_total = sum(scores.values())

    risk_flags = normalize_risk_flags(parsed.get("risk_flags", []))
    heuristic_penalty, heuristic_flags = heuristic_pedagogy_flags(answer, mode)

    final_flags = list(dict.fromkeys(risk_flags + heuristic_flags))[:12]

    total = max(
        0,
        base_total
        - compute_risk_penalty(risk_flags)
        - heuristic_penalty
    )

    return {
        **scores,
        "base_total": base_total,
        "total": total,
        "verdict": build_verdict(total),
        "improvement_hint": clean(parsed.get("improvement_hint")) or "Rendre la réponse plus ciblée, plus fidèle et plus formatrice.",
        "main_weakness": clean(parsed.get("main_weakness")) or "Faiblesse principale non identifiée.",
        "risk_flags": final_flags,
        "is_fallback": False
    }


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
        "base_total": 5,
        "total": 5,
        "verdict": "fallback",
        "improvement_hint": reason,
        "main_weakness": "Évaluation automatique incomplète.",
        "risk_flags": flags,
        "is_fallback": True
    }


def build_judge_prompt(answer, message, niveau, matiere, cours, mode):
    return f"""
Niveau : {niveau}
Matière : {matiere}
Mode demandé : {mode}

Cours :
{cours}

Question :
{message}

Réponse à évaluer :
{answer}
""".strip()


def judge(answer, message, niveau, matiere, cours, mode=""):
    prompt = build_judge_prompt(answer, message, niveau, matiere, cours, mode)

    raw = call_ollama([
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ], temp=0.0, max_tokens=1100)

    if not raw or len(clean(raw)) < 5:
        return fallback_judgment("Réponse vide du juge.", "empty_judge_output")

    parsed = extract_json(raw)

    if not is_valid_judgment_dict(parsed):
        return fallback_judgment("Le juge n’a pas renvoyé un JSON valide.", "invalid_json")

    return normalize_judgment(parsed, answer=answer, mode=mode)