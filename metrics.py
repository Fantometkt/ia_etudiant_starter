from utils import *


METRICS_FILE = "data/metrics.jsonl"


def log_event(event_type, payload=None):
    item = {
        "timestamp": now_iso(),
        "event_type": clean(event_type),
        "payload": safe_dict(payload)
    }

    append_jsonl(METRICS_FILE, item)


def summarize_scores(scores):
    scores = [to_int(s, 0, 0, 100) for s in scores]

    if not scores:
        return {
            "count": 0,
            "average": 0,
            "min": 0,
            "max": 0
        }

    return {
        "count": len(scores),
        "average": average(scores),
        "min": min(scores),
        "max": max(scores)
    }


def build_project_metrics(mem):
    students = safe_dict(mem.get("students"))
    all_scores = []
    total_interactions = 0
    skills_count = 0
    fragile_count = 0
    mastered_count = 0

    for student in students.values():
        progress = safe_dict(student.get("progress"))
        total_interactions += int(progress.get("total_interactions", 0))

        for s in progress.get("last_scores", []):
            all_scores.append(s)

        for skill in safe_dict(student.get("skills")).values():
            skills_count += 1
            if skill.get("level") in {"fragile", "partiel"}:
                fragile_count += 1
            if skill.get("level") in {"solide", "maitrise"}:
                mastered_count += 1

    return {
        "students_count": len(students),
        "total_interactions": total_interactions,
        "student_scores": summarize_scores(all_scores),
        "skills_count": skills_count,
        "fragile_or_partial_skills": fragile_count,
        "solid_or_mastered_skills": mastered_count,
        "generated_at": now_iso()
    }


def build_student_dashboard(student):
    progress = safe_dict(student.get("progress"))
    skills = safe_dict(student.get("skills"))

    fragile = []
    solid = []

    for notion, skill in skills.items():
        item = {
            "notion": notion,
            "level": skill.get("level"),
            "score": skill.get("score"),
            "trend": skill.get("trend"),
            "next_action": skill.get("recommended_next_action")
        }

        if skill.get("level") in {"fragile", "partiel"}:
            fragile.append(item)
        else:
            solid.append(item)

    fragile.sort(key=lambda x: x.get("score") or 0)
    solid.sort(key=lambda x: x.get("score") or 0, reverse=True)

    return {
        "profile": student.get("profile", {}),
        "progress": progress,
        "fragile_skills": fragile[:8],
        "solid_skills": solid[:8],
        "recent_events": student.get("learning_events", [])[-8:],
        "recent_sessions": student.get("sessions", [])[-8:]
    }