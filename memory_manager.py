from utils import *

MEMORY_FILE = "memory.json"

# =========================
# BASE
# =========================

def load_memory():
    return load_json_file(MEMORY_FILE, {
        "history": [],
        "stats": {},
        "selftests": [],
        "students": {}
    })

def save_memory(mem):
    save_json_file(MEMORY_FILE, mem)

# =========================
# STRUCTURE ÉTUDIANT
# =========================

def ensure_student(mem, student_id):
    if not student_id:
        return None

    if "students" not in mem:
        mem["students"] = {}

    if student_id not in mem["students"]:
        mem["students"][student_id] = {
            "profile": {
                "display_name": "",
                "niveau": "",
                "matiere": "",
                "learning_style": "",
                "weaknesses": "",
                "last_seen": now_iso()
            },
            "sessions": [],
            "memory_notes": [],
            "focus_topics": [],
            "progress_clues": {
                "frequent_modes": {},
                "recent_difficulties": [],
                "recent_strengths": []
            }
        }

    return mem["students"][student_id]

# =========================
# PROFIL
# =========================

def update_student_profile(mem, student_id, display_name, niveau, matiere, learning_style, weaknesses):
    student = ensure_student(mem, student_id)
    if not student:
        return

    student["profile"]["display_name"] = display_name
    student["profile"]["niveau"] = niveau
    student["profile"]["matiere"] = matiere
    student["profile"]["learning_style"] = learning_style
    student["profile"]["weaknesses"] = weaknesses
    student["profile"]["last_seen"] = now_iso()

# =========================
# ANALYSE CONTENU
# =========================

def extract_focus_topics(cours, matiere, message):
    text = " ".join([clean(matiere), clean(message), clean(cours)]).lower()

    topics = []
    keywords = [
        "socialisation", "contrôle social", "normes", "valeurs",
        "identité", "rôles sociaux", "déviance", "groupe social",
        "famille", "institution", "stratification", "capital culturel",
        "habitus", "pouvoir", "intégration", "conformité",
        "socialisation primaire", "socialisation secondaire",
        "conscience", "liberté", "justice", "vérité",
        "croissance", "chômage", "marché", "offre", "demande",
        "industrialisation", "urbanisation", "mouvement ouvrier"
    ]

    for k in keywords:
        if k in text:
            topics.append(k)

    return topics[:10]

def summarize_interaction(mode, message, cours, answer):
    return {
        "timestamp": now_iso(),
        "mode": mode,
        "question": clean(message)[:160],
        "cours_hint": clean(cours)[:120],
        "answer_hint": clean(answer).replace("\n", " ")[:180]
    }

# =========================
# PROGRESSION
# =========================

def update_progress(student, mode, weaknesses, answer):
    progress = student.setdefault("progress_clues", {
        "frequent_modes": {},
        "recent_difficulties": [],
        "recent_strengths": []
    })

    if mode:
        progress["frequent_modes"][mode] = progress["frequent_modes"].get(mode, 0) + 1

    if weaknesses:
        if weaknesses not in progress["recent_difficulties"]:
            progress["recent_difficulties"].append(weaknesses)
        progress["recent_difficulties"] = progress["recent_difficulties"][-8:]

    if "complément utile" in clean(answer).lower():
        strength = "Bonne utilisation des compléments utiles"
        if strength not in progress["recent_strengths"]:
            progress["recent_strengths"].append(strength)

    progress["recent_strengths"] = progress["recent_strengths"][-8:]

# =========================
# UPDATE GLOBAL
# =========================

def update_student_memory(mem, student_id, display_name, niveau, matiere, learning_style, weaknesses, mode, message, cours, answer):
    if not student_id:
        return

    student = ensure_student(mem, student_id)
    if not student:
        return

    update_student_profile(mem, student_id, display_name, niveau, matiere, learning_style, weaknesses)

    student["sessions"].append(
        summarize_interaction(mode, message, cours, answer)
    )
    student["sessions"] = student["sessions"][-10:]

    topics = extract_focus_topics(cours, matiere, message)
    for t in topics:
        if t not in student["focus_topics"]:
            student["focus_topics"].append(t)

    student["focus_topics"] = student["focus_topics"][-18:]

    if weaknesses:
        note = f"Lacunes : {weaknesses}"
        if note not in student["memory_notes"]:
            student["memory_notes"].append(note)

    if learning_style:
        note = f"Style : {learning_style}"
        if note not in student["memory_notes"]:
            student["memory_notes"].append(note)

    student["memory_notes"] = student["memory_notes"][-18:]

    update_progress(student, mode, weaknesses, answer)

# =========================
# CONTEXTE POUR IA
# =========================

def build_student_memory_context(mem, student_id):
    if not student_id:
        return "Aucune mémoire."

    student = mem.get("students", {}).get(student_id)
    if not student:
        return "Aucune mémoire."

    profile = student.get("profile", {})
    sessions = student.get("sessions", [])[-3:]
    notes = student.get("memory_notes", [])[-4:]
    topics = student.get("focus_topics", [])[-6:]

    lines = [
        f"Nom : {profile.get('display_name', '')}",
        f"Niveau : {profile.get('niveau', '')}",
        f"Matière : {profile.get('matiere', '')}",
        f"Style : {profile.get('learning_style', '')}",
        f"Lacunes : {profile.get('weaknesses', '')}",
    ]

    if topics:
        lines.append("Thèmes : " + ", ".join(topics))

    if notes:
        lines.append("Notes :")
        for n in notes:
            lines.append(f"- {n}")

    if sessions:
        lines.append("Dernières interactions :")
        for s in sessions:
            lines.append(f"- {s.get('mode')} : {s.get('question')}")

    return "\n".join(lines)