from utils import *
from skills import get_weakest_skills, get_mastered_skills


# =========================================================
# LEARNING STATE
# =========================================================

def infer_learning_state(student):
    progress = safe_dict(student.get("progress"))
    skills = safe_dict(student.get("skills"))

    if not skills:
        return {
            "state": "nouveau_profil",
            "summary": "Aucune donnée d’apprentissage suffisante.",
            "priority": "diagnostic_initial"
        }

    weakest = get_weakest_skills(student, limit=3)
    mastered = get_mastered_skills(student, limit=3)

    last_scores = progress.get("last_scores", [])
    avg_score = average(last_scores)

    if avg_score < 35:
        state = "grande_fragilite"
        priority = "reprendre_les_bases"
    elif avg_score < 60:
        state = "comprehension_partielle"
        priority = "corriger_les_confusions"
    elif avg_score < 80:
        state = "niveau_correct"
        priority = "consolider_et_preparer_examen"
    else:
        state = "niveau_solide"
        priority = "approfondir_et_maintenir"

    return {
        "state": state,
        "summary": f"Score moyen récent : {avg_score}/100.",
        "priority": priority,
        "weakest_skills": [
            {
                "notion": notion,
                "score": data.get("score"),
                "level": data.get("level"),
                "errors": data.get("errors", [])[-3:]
            }
            for notion, data in weakest
        ],
        "mastered_skills": [
            {
                "notion": notion,
                "score": data.get("score"),
                "level": data.get("level")
            }
            for notion, data in mastered
        ]
    }


def recommend_mode(student):
    state = infer_learning_state(student)

    if state["state"] == "nouveau_profil":
        return "diagnostic"

    if state["state"] == "grande_fragilite":
        return "expliquer"

    if state["state"] == "comprehension_partielle":
        return "socratic"

    if state["state"] == "niveau_correct":
        return "quiz"

    return "exam"


def build_progress_context(student):
    state = infer_learning_state(student)

    lines = [
        "ÉTAT D’APPRENTISSAGE",
        f"- État : {state.get('state')}",
        f"- Résumé : {state.get('summary')}",
        f"- Priorité : {state.get('priority')}",
    ]

    weakest = state.get("weakest_skills", [])
    if weakest:
        lines.append("\nCompétences fragiles :")
        for item in weakest:
            errors = item.get("errors", [])
            line = f"- {item.get('notion')} ({item.get('level')}, {item.get('score')}/100)"
            if errors:
                line += " | erreurs : " + ", ".join(errors)
            lines.append(line)

    mastered = state.get("mastered_skills", [])
    if mastered:
        lines.append("\nCompétences solides :")
        for item in mastered:
            lines.append(f"- {item.get('notion')} ({item.get('level')}, {item.get('score')}/100)")

    return "\n".join(lines)


def build_learning_plan(student, horizon="court"):
    state = infer_learning_state(student)
    weakest = state.get("weakest_skills", [])

    if not weakest:
        return {
            "goal": "Établir un diagnostic initial",
            "steps": [
                "Faire répondre l’étudiant à une question courte.",
                "Évaluer la réponse.",
                "Identifier les premières notions fragiles."
            ],
            "recommended_mode": "diagnostic"
        }

    first = weakest[0]
    notion = first.get("notion")

    if horizon == "court":
        return {
            "goal": f"Stabiliser la notion : {notion}",
            "steps": [
                "Reprendre la définition ou l’idée centrale.",
                "Identifier l’erreur principale.",
                "Faire une question guidée.",
                "Corriger immédiatement la réponse.",
                "Finir par une phrase à retenir."
            ],
            "recommended_mode": "socratic"
        }

    return {
        "goal": "Construire une progression sur plusieurs séances",
        "steps": [
            "Séance 1 : diagnostic des notions fragiles.",
            "Séance 2 : explication ciblée des blocages.",
            "Séance 3 : exercices courts avec correction.",
            "Séance 4 : sujet type examen.",
            "Séance 5 : révision espacée des notions faibles."
        ],
        "recommended_mode": "progression"
    }


def compute_progress_delta(pre_score, post_score):
    pre_score = to_int(pre_score, 0, 0, 100)
    post_score = to_int(post_score, 0, 0, 100)

    delta = post_score - pre_score

    if delta >= 25:
        label = "progression_forte"
    elif delta >= 10:
        label = "progression_reelle"
    elif delta >= 1:
        label = "progression_legere"
    elif delta == 0:
        label = "stable"
    else:
        label = "regression"

    return {
        "pre_score": pre_score,
        "post_score": post_score,
        "delta": delta,
        "label": label
    }