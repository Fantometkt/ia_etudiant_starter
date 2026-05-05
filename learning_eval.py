from utils import *
from llm import call_ollama


STUDENT_EVAL_PROMPT = """
Tu es un évaluateur pédagogique exigeant.

Tu évalues la compréhension réelle d'un étudiant à partir :
- du cours fourni
- de la question
- de la réponse de l'étudiant
- du niveau scolaire/universitaire

Tu dois répondre UNIQUEMENT en JSON valide.

Format exact :
{
  "score": 0,
  "notions_detectees": [],
  "notions_maitrisees": [],
  "notions_fragiles": [],
  "erreurs": [],
  "oublis": [],
  "forces": [],
  "diagnostic": "",
  "next_step": "",
  "question_suivante_recommandee": ""
}

Règles :
- score entre 0 et 100
- 0-30 = compréhension fragile
- 31-55 = compréhension partielle
- 56-78 = compréhension correcte
- 79-100 = maîtrise solide
- distingue erreur, oubli et approximation
- ne sois pas flatteur
- ne sanctionne pas seulement la forme
- juge la compréhension
- ne rajoute aucun texte hors JSON
"""


def fallback_student_eval(reason):
    return {
        "score": 0,
        "notions_detectees": [],
        "notions_maitrisees": [],
        "notions_fragiles": [],
        "erreurs": [reason],
        "oublis": [],
        "forces": [],
        "diagnostic": "Évaluation automatique impossible ou réponse insuffisante.",
        "next_step": "Reprendre la notion avec une question simple.",
        "question_suivante_recommandee": "Peux-tu reformuler l'idée principale avec tes mots ?"
    }


def normalize_student_eval(parsed):
    if not isinstance(parsed, dict):
        return fallback_student_eval("JSON d'évaluation invalide")

    return {
        "score": to_int(parsed.get("score"), 0, 0, 100),
        "notions_detectees": [clean(x) for x in safe_list(parsed.get("notions_detectees")) if clean(x)][:10],
        "notions_maitrisees": [clean(x) for x in safe_list(parsed.get("notions_maitrisees")) if clean(x)][:10],
        "notions_fragiles": [clean(x) for x in safe_list(parsed.get("notions_fragiles")) if clean(x)][:10],
        "erreurs": [clean(x) for x in safe_list(parsed.get("erreurs")) if clean(x)][:10],
        "oublis": [clean(x) for x in safe_list(parsed.get("oublis")) if clean(x)][:10],
        "forces": [clean(x) for x in safe_list(parsed.get("forces")) if clean(x)][:10],
        "diagnostic": clean(parsed.get("diagnostic")),
        "next_step": clean(parsed.get("next_step")),
        "question_suivante_recommandee": clean(parsed.get("question_suivante_recommandee")),
    }


def evaluate_student_answer(cours, question, student_answer, niveau, matiere):
    cours = clean(cours)
    question = clean(question)
    student_answer = clean(student_answer)

    if not student_answer:
        return fallback_student_eval("réponse étudiante absente")

    prompt = f"""
Niveau : {niveau}
Matière : {matiere}

Cours :
{cours if cours else "Aucun cours fourni."}

Question :
{question}

Réponse de l'étudiant :
{student_answer}
""".strip()

    raw = call_ollama([
        {"role": "system", "content": STUDENT_EVAL_PROMPT},
        {"role": "user", "content": prompt}
    ], temp=0.0, max_tokens=1200)

    parsed = extract_json(raw)

    return normalize_student_eval(parsed)


def build_eval_summary(student_eval):
    student_eval = safe_dict(student_eval)

    if not student_eval:
        return "Aucune évaluation étudiant disponible."

    lines = [
        f"Score étudiant : {student_eval.get('score', 0)}/100",
        f"Diagnostic : {student_eval.get('diagnostic', '')}",
        f"Prochaine étape : {student_eval.get('next_step', '')}",
    ]

    if student_eval.get("erreurs"):
        lines.append("Erreurs : " + ", ".join(student_eval["erreurs"][:5]))

    if student_eval.get("oublis"):
        lines.append("Oublis : " + ", ".join(student_eval["oublis"][:5]))

    if student_eval.get("forces"):
        lines.append("Forces : " + ", ".join(student_eval["forces"][:5]))

    return "\n".join(lines)