from utils import *
from skills import update_skill, build_skills_context
from progress_engine import build_progress_context


MEMORY_FILE = "data/memory.json"


# =========================================================
# BASE
# =========================================================

def load_memory():
    return load_json_file(MEMORY_FILE, {
        "history": [],
        "stats": {},
        "selftests": [],
        "selftests_ultra": [],
        "best_patterns": [],
        "students": {}
    })


def save_memory(mem):
    save_json_file(MEMORY_FILE, mem)


# =========================================================
# STUDENT
# =========================================================

def ensure_student(mem, student_id):
    student_id = clean(student_id)

    if not student_id:
        return None

    mem.setdefault("students", {})

    if student_id not in mem["students"]:
        mem["students"][student_id] = {
            "profile": {
                "display_name": "",
                "niveau": "",
                "matiere": "",
                "learning_style": "",
                "weaknesses": "",
                "created_at": now_iso(),
                "last_seen": now_iso()
            },
            "sessions": [],
            "skills": {},
            "learning_events": [],
            "focus_topics": [],
            "memory_notes": [],
            "progress": {
                "total_interactions": 0,
                "avg_student_score": 0,
                "last_scores": [],
                "dominant_modes": {},
                "pre_post_deltas": []
            }
        }

    return mem["students"][student_id]


def update_student_profile(mem, student_id, display_name, niveau, matiere, learning_style, weaknesses):
    student = ensure_student(mem, student_id)

    if not student:
        return

    profile = student.setdefault("profile", {})
    profile["display_name"] = clean(display_name)
    profile["niveau"] = clean(niveau)
    profile["matiere"] = clean(matiere)
    profile["learning_style"] = clean(learning_style)
    profile["weaknesses"] = clean(weaknesses)
    profile["last_seen"] = now_iso()


# =========================================================
# TOPICS
# =========================================================

def extract_focus_topics(cours, matiere="", message=""):
    text = " ".join([clean(cours), clean(matiere), clean(message)]).lower()

    candidates = [
        "socialisation primaire",
        "socialisation secondaire",
        "socialisation",
        "contrôle social",
        "controle social",
        "normes",
        "valeurs",
        "déviance",
        "deviance",
        "rôle social",
        "role social",
        "marché",
        "marche",
        "offre",
        "demande",
        "prix",
        "équilibre",
        "equilibre",
        "chômage",
        "chomage",
        "conscience",
        "vérité",
        "verite",
        "liberté",
        "liberte",
        "justice",
        "industrialisation",
        "urbanisation",
        "prolétariat",
        "proletariat",
        "usine",
        "argumentation",
        "thèse",
        "these",
        "problématique",
        "problematique",
        "fonction",
        "dérivée",
        "derivee",
        "adn",
        "gène",
        "gene",
        "mémoire de travail",
        "memoire de travail",
        "légitimité politique",
        "legitimite politique",
        "règle de droit",
        "regle de droit"
    ]

    found = []

    for c in candidates:
        if c in text and c not in found:
            found.append(c)

    return found[:12]


# =========================================================
# SESSION / PROGRESS
# =========================================================

def summarize_interaction(mode, message, cours, answer, student_eval=None):
    return {
        "timestamp": now_iso(),
        "mode": clean(mode),
        "question": short(message, 220),
        "cours_hint": short(cours, 200),
        "answer_hint": short(answer, 300),
        "student_score": safe_dict(student_eval).get("score") if student_eval else None
    }


def update_progress(student, mode, student_score=None, pre_post_delta=None):
    progress = student.setdefault("progress", {
        "total_interactions": 0,
        "avg_student_score": 0,
        "last_scores": [],
        "dominant_modes": {},
        "pre_post_deltas": []
    })

    progress["total_interactions"] = int(progress.get("total_interactions", 0)) + 1

    mode = clean(mode)
    if mode:
        progress.setdefault("dominant_modes", {})
        progress["dominant_modes"][mode] = progress["dominant_modes"].get(mode, 0) + 1

    if student_score is not None:
        score = to_int(student_score, 0, 0, 100)
        progress.setdefault("last_scores", [])
        progress["last_scores"].append(score)
        progress["last_scores"] = progress["last_scores"][-30:]
        progress["avg_student_score"] = average(progress["last_scores"])

    if pre_post_delta:
        progress.setdefault("pre_post_deltas", [])
        progress["pre_post_deltas"].append(pre_post_delta)
        progress["pre_post_deltas"] = progress["pre_post_deltas"][-30:]


def update_student_memory(
    mem,
    student_id,
    display_name,
    niveau,
    matiere,
    learning_style,
    weaknesses,
    mode,
    message,
    cours,
    answer,
    student_eval=None,
    pre_post_delta=None
):
    student = ensure_student(mem, student_id)

    if not student:
        return

    update_student_profile(
        mem,
        student_id,
        display_name,
        niveau,
        matiere,
        learning_style,
        weaknesses
    )

    student.setdefault("sessions", [])
    student["sessions"].append(
        summarize_interaction(mode, message, cours, answer, student_eval)
    )
    student["sessions"] = student["sessions"][-20:]

    topics = extract_focus_topics(cours, matiere, message)

    student.setdefault("focus_topics", [])
    for topic in topics:
        if topic not in student["focus_topics"]:
            student["focus_topics"].append(topic)
    student["focus_topics"] = student["focus_topics"][-25:]

    student.setdefault("memory_notes", [])

    if clean(weaknesses):
        note = f"Lacunes déclarées : {clean(weaknesses)}"
        if note not in student["memory_notes"]:
            student["memory_notes"].append(note)

    if clean(learning_style):
        note = f"Style déclaré : {clean(learning_style)}"
        if note not in student["memory_notes"]:
            student["memory_notes"].append(note)

    student["memory_notes"] = student["memory_notes"][-25:]

    if student_eval:
        event = {
            "timestamp": now_iso(),
            "mode": mode,
            "score": student_eval.get("score"),
            "diagnostic": student_eval.get("diagnostic"),
            "next_step": student_eval.get("next_step"),
            "question_suivante_recommandee": student_eval.get("question_suivante_recommandee"),
            "errors": student_eval.get("erreurs", []),
            "omissions": student_eval.get("oublis", []),
            "strengths": student_eval.get("forces", [])
        }

        student.setdefault("learning_events", [])
        student["learning_events"].append(event)
        student["learning_events"] = student["learning_events"][-40:]

        notions = (
            student_eval.get("notions_fragiles", [])
            or student_eval.get("notions_detectees", [])
            or topics
        )

        for notion in notions:
            update_skill(
                student,
                notion=notion,
                score=student_eval.get("score", 0),
                errors=student_eval.get("erreurs", []) + student_eval.get("oublis", []),
                strengths=student_eval.get("forces", []),
                source="student_eval"
            )

        update_progress(
            student,
            mode,
            student_score=student_eval.get("score"),
            pre_post_delta=pre_post_delta
        )
    else:
        update_progress(student, mode, pre_post_delta=pre_post_delta)


# =========================================================
# CONTEXT FOR GENERATION
# =========================================================

def build_student_memory_context(mem, student_id):
    student_id = clean(student_id)

    if not student_id:
        return "Aucune mémoire étudiant."

    student = safe_dict(mem.get("students")).get(student_id)

    if not student:
        return "Aucune mémoire étudiant."

    profile = safe_dict(student.get("profile"))
    notes = student.get("memory_notes", [])[-5:]
    topics = student.get("focus_topics", [])[-8:]
    sessions = student.get("sessions", [])[-5:]
    events = student.get("learning_events", [])[-4:]

    lines = [
        "PROFIL",
        f"- Nom : {profile.get('display_name', '')}",
        f"- Niveau : {profile.get('niveau', '')}",
        f"- Matière : {profile.get('matiere', '')}",
        f"- Style : {profile.get('learning_style', '')}",
        f"- Lacunes déclarées : {profile.get('weaknesses', '')}",
        "",
        build_progress_context(student),
        "",
        "COMPÉTENCES",
        build_skills_context(student)
    ]

    if topics:
        lines.append("\nTHÈMES FRÉQUENTS")
        lines.append(", ".join(topics))

    if notes:
        lines.append("\nNOTES MÉMOIRE")
        for note in notes:
            lines.append(f"- {note}")

    if events:
        lines.append("\nDERNIERS DIAGNOSTICS")
        for event in events:
            lines.append(
                f"- Score {event.get('score')}/100 : "
                f"{short(event.get('diagnostic'), 160)}"
            )

    if sessions:
        lines.append("\nDERNIÈRES INTERACTIONS")
        for session in sessions:
            lines.append(f"- {session.get('mode')} : {session.get('question')}")

    return "\n".join(lines)