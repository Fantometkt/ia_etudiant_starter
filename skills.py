from utils import *


# =========================================================
# SKILL MODEL
# =========================================================

SKILL_LEVELS = [
    "non_evalue",
    "fragile",
    "partiel",
    "solide",
    "maitrise"
]


def score_to_level(score):
    score = to_int(score, 0, 0, 100)

    if score < 30:
        return "fragile"
    if score < 55:
        return "partiel"
    if score < 78:
        return "solide"
    return "maitrise"


def default_skill_state():
    return {
        "level": "non_evalue",
        "score": 0,
        "attempts": 0,
        "last_seen": now_iso(),
        "trend": "stable",
        "errors": [],
        "strengths": [],
        "recommended_next_action": "diagnostiquer",
        "history": []
    }


def compute_trend(previous, current):
    previous = float(previous or 0)
    current = float(current or 0)

    if current >= previous + 10:
        return "progression"
    if current <= previous - 10:
        return "regression"
    return "stable"


def recommend_next_action(level, errors=None):
    errors = safe_list(errors)

    if level == "fragile":
        return "reexplication_guidée + question simple"
    if level == "partiel":
        return "exercice ciblé + correction détaillée"
    if level == "solide":
        return "question d'examen + consolidation"
    if level == "maitrise":
        return "révision espacée + exercice difficile"

    return "diagnostic initial"


def update_skill(student, notion, score, errors=None, strengths=None, source="interaction"):
    notion = clean(notion)

    if not notion:
        return

    score = to_int(score, 0, 0, 100)
    errors = [clean(e) for e in safe_list(errors) if clean(e)]
    strengths = [clean(s) for s in safe_list(strengths) if clean(s)]

    student.setdefault("skills", {})
    skill = student["skills"].setdefault(notion, default_skill_state())

    previous_score = float(skill.get("score", 0))
    attempts = int(skill.get("attempts", 0))

    new_score = round(((previous_score * attempts) + score) / (attempts + 1), 2)
    level = score_to_level(new_score)

    skill["score"] = new_score
    skill["attempts"] = attempts + 1
    skill["level"] = level
    skill["trend"] = compute_trend(previous_score, new_score)
    skill["last_seen"] = now_iso()

    for e in errors:
        if e not in skill["errors"]:
            skill["errors"].append(e)

    for s in strengths:
        if s not in skill["strengths"]:
            skill["strengths"].append(s)

    skill["errors"] = skill["errors"][-8:]
    skill["strengths"] = skill["strengths"][-8:]

    skill["recommended_next_action"] = recommend_next_action(level, errors)

    skill["history"].append({
        "timestamp": now_iso(),
        "score": score,
        "average_score": new_score,
        "level": level,
        "source": source,
        "errors": errors[:5],
        "strengths": strengths[:5]
    })

    skill["history"] = skill["history"][-15:]


def build_skills_context(student):
    skills = safe_dict(student.get("skills"))

    if not skills:
        return "Aucune compétence suivie pour l’instant."

    sorted_items = sorted(
        skills.items(),
        key=lambda item: item[1].get("last_seen", ""),
        reverse=True
    )

    lines = []

    for notion, skill in sorted_items[:10]:
        lines.append(
            f"- {notion} | niveau={skill.get('level')} | "
            f"score={skill.get('score')} | tendance={skill.get('trend')} | "
            f"prochaine_action={skill.get('recommended_next_action')}"
        )

        errors = skill.get("errors", [])[-3:]
        if errors:
            lines.append("  erreurs : " + ", ".join(errors))

    return "\n".join(lines)


def get_weakest_skills(student, limit=5):
    skills = safe_dict(student.get("skills"))

    items = [
        (notion, data)
        for notion, data in skills.items()
        if data.get("level") in {"fragile", "partiel"}
    ]

    items.sort(key=lambda item: item[1].get("score", 0))

    return items[:limit]


def get_mastered_skills(student, limit=5):
    skills = safe_dict(student.get("skills"))

    items = [
        (notion, data)
        for notion, data in skills.items()
        if data.get("level") in {"solide", "maitrise"}
    ]

    items.sort(key=lambda item: item[1].get("score", 0), reverse=True)

    return items[:limit]