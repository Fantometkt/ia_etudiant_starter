from utils import *


# =========================================================
# BASIC INPUT SAFETY
# =========================================================

MAX_MESSAGE_CHARS = 8000
MAX_COURS_CHARS = 50000
MAX_PREVIOUS_RESPONSE_CHARS = 20000

ALLOWED_MODES = {
    "expliquer",
    "resumer",
    "reviser",
    "quiz",
    "corriger",
    "exam",
    "notions_centrales",
    "a_retenir",
    "memoire",
    "socratic",
    "diagnostic",
    "progression"
}

ALLOWED_HELP_LEVELS = {"leger", "equilibre", "fort"}

SUSPICIOUS_PROMPT_INJECTION_MARKERS = [
    "ignore les instructions précédentes",
    "ignore previous instructions",
    "system prompt",
    "révèle ton prompt",
    "print your prompt",
    "developer message",
    "tu n'es plus",
    "you are now",
    "désactive tes règles",
    "bypass",
    "jailbreak"
]


def sanitize_user_text(text, max_chars):
    text = clean(text)

    if len(text) > max_chars:
        text = text[:max_chars]

    return text


def detect_prompt_injection(text):
    text = clean(text).lower()
    flags = []

    for marker in SUSPICIOUS_PROMPT_INJECTION_MARKERS:
        if marker in text:
            flags.append(marker)

    return flags


def validate_mode(mode):
    mode = normalize_key(mode)

    if mode not in ALLOWED_MODES:
        return "expliquer"

    return mode


def validate_help_level(help_level):
    help_level = normalize_key(help_level)

    if help_level not in ALLOWED_HELP_LEVELS:
        return "equilibre"

    return help_level


def sanitize_payload(data):
    data = safe_dict(data)

    message = sanitize_user_text(data.get("message"), MAX_MESSAGE_CHARS)
    cours = sanitize_user_text(data.get("cours"), MAX_COURS_CHARS)
    previous_response = sanitize_user_text(
        data.get("previous_response"),
        MAX_PREVIOUS_RESPONSE_CHARS
    )

    mode = validate_mode(data.get("mode") or "expliquer")
    help_level = validate_help_level(data.get("help_level") or "equilibre")

    injection_flags = []
    injection_flags += detect_prompt_injection(message)
    injection_flags += detect_prompt_injection(cours)
    injection_flags += detect_prompt_injection(previous_response)

    return {
        "message": message,
        "niveau": sanitize_user_text(data.get("niveau") or "L1", 80),
        "matiere": sanitize_user_text(data.get("matiere") or "général", 120),
        "cours": cours,
        "mode": mode,
        "student_id": sanitize_user_text(data.get("student_id") or "local_student", 120),
        "student_name": sanitize_user_text(data.get("student_name") or "", 120),
        "learning_style": sanitize_user_text(data.get("learning_style") or "", 500),
        "weaknesses": sanitize_user_text(data.get("weaknesses") or "", 1000),
        "previous_response": previous_response,
        "learning_goal": sanitize_user_text(data.get("learning_goal") or "comprendre", 300),
        "help_level": help_level,
        "injection_flags": list(dict.fromkeys(injection_flags))
    }


# =========================================================
# OUTPUT SAFETY / QUALITY
# =========================================================

def looks_like_error_output(answer):
    answer = clean(answer).lower()

    markers = [
        "traceback",
        "syntaxerror",
        "importerror",
        "keyerror",
        "typeerror",
        "erreur ia",
        "erreur de génération",
        "backend inconnu",
        "connection refused",
        "read timed out"
    ]

    return any(m in answer for m in markers)


def output_quality_flags(answer):
    answer = clean(answer)
    lower = answer.lower()
    flags = []

    if not answer:
        flags.append("empty_output")

    if word_count(answer) < 8:
        flags.append("too_short")

    if word_count(answer) > 900:
        flags.append("too_long")

    if looks_like_error_output(answer):
        flags.append("technical_error_output")

    if lower.count("il faut retenir") >= 4:
        flags.append("repetition_possible")

    return flags