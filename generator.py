from utils import *
from prompts import *
from memory_manager import *
from course_analyzer import analyze_course, format_course_analysis
from judge import judge
from llm import call_ollama

FAST_MODES = {"expliquer", "resumer", "a_retenir", "quiz"}

MODE_TEMPS = {
    "expliquer": [0.15, 0.3],
    "resumer": [0.1, 0.2],
    "a_retenir": [0.1, 0.2],
    "quiz": [0.2, 0.3],
    "corriger": [0.15, 0.25],
    "exam": [0.15, 0.25],
    "notions_centrales": [0.15, 0.25],
    "memoire": [0.2, 0.3],
    "reviser": [0.15, 0.25],
}

def build_evolution_block(mem):
    if not mem.get("selftests"):
        return ""

    last = mem["selftests"][-1].get("diagnostics", {})
    recos = last.get("recommendations", [])
    weak = last.get("weak_points", [])

    bloc = []

    for r in recos[:3]:
        bloc.append(f"- {r}")

    for w in weak[:2]:
        bloc.append(f"- Corriger : {w}")

    if not bloc:
        return ""

    return f"""
AMÉLIORATION CONTINUE :
{chr(10).join(bloc)}

RÈGLES D'ÉVOLUTION :
- Corrige activement ces faiblesses
- Ne reproduis pas les erreurs passées
- Évite la paraphrase descriptive
- Hiérarchise davantage
"""

def build_mode_behavior(mode):
    if mode == "resumer":
        return """
COMPORTEMENT ATTENDU :
- très peu de structure
- pas de sous-parties décoratives
- pas de redondance
- priorité à la densité utile
"""
    if mode == "corriger":
        return """
COMPORTEMENT ATTENDU :
- jugement net
- hiérarchisation des erreurs
- expliquer le mécanisme, pas seulement le constat
- vraie amélioration de copie
"""
    if mode == "exam":
        return """
COMPORTEMENT ATTENDU :
- sujet crédible
- attentes du correcteur utiles
- plan efficace
- pas de développement scolaire inutile
"""
    if mode == "expliquer":
        return """
COMPORTEMENT ATTENDU :
- rendre le cours compréhensible
- aller au mécanisme
- éviter la simple reformulation
"""
    if mode == "notions_centrales":
        return """
COMPORTEMENT ATTENDU :
- extraction forte de l’essentiel
- hiérarchisation claire
- pas d’explication décorative
"""
    if mode == "reviser":
        return """
COMPORTEMENT ATTENDU :
- support de révision mémorisable
- liens importants mis en évidence
- pas de bavardage
"""
    return """
COMPORTEMENT ATTENDU :
- réponse utile
- claire
- hiérarchisée
"""

def build_prompt(
    mem,
    message,
    niveau,
    matiere,
    cours,
    student_id,
    learning_style,
    weaknesses,
    previous_response,
    mode,
    learning_goal="comprendre",
    help_level="equilibre"
):
    student_context = build_student_memory_context(mem, student_id)
    course_analysis = analyze_course(cours, niveau, matiere, force=False)
    analysis_text = format_course_analysis(course_analysis)
    evolution_block = build_evolution_block(mem)
    mode_behavior = build_mode_behavior(mode)

    return f"""
CONTEXTE
- Niveau : {niveau}
- Matière : {matiere}
- Mode : {mode}
- Objectif pédagogique : {learning_goal}
- Niveau d’aide : {help_level}

PROFIL ÉTUDIANT
{student_context}

ANALYSE DU COURS
{analysis_text}

{evolution_block}

{mode_behavior}

RÈGLES
- Base principale = le cours
- Réponse dense et utile
- Évite la paraphrase mécanique
- Hiérarchise clairement
- Supprime les répétitions
- Si le cours est insuffisant, dis-le clairement
- Si aucun cours n’est fourni, utilise seulement des connaissances générales fiables et sobres
- N’alourdis pas la structure si elle n’apporte rien

COURS
{cours if cours else "Aucun cours fourni."}

RÉPONSE ÉTUDIANTE
{previous_response if previous_response else "Aucune"}

DEMANDE
{message}
"""

def answer_is_bad(ans: str) -> bool:
    a = clean(ans).lower()
    if not a:
        return True
    bad_markers = [
        "erreur ia",
        "erreur de génération",
        "traceback",
        "importerror",
        "syntaxerror",
    ]
    return any(marker in a for marker in bad_markers)

def score_variant(ans, message, niveau, matiere, cours):
    if answer_is_bad(ans):
        return -999, {"total": -999}
    raw = judge(ans, message, niveau, matiere, cours)
    return raw.get("total", 0), raw

def choose_best_variant(variants, message, niveau, matiere, cours):
    best_answer = variants[0]
    best_score = -10**9
    best_meta = None

    for ans in variants:
        total, raw = score_variant(ans, message, niveau, matiere, cours)
        if total > best_score:
            best_score = total
            best_answer = ans
            best_meta = raw
        elif total == best_score and len(ans) < len(best_answer):
            best_answer = ans
            best_meta = raw

    return best_answer, best_score, best_meta

def generate_answer(
    mem,
    message,
    niveau,
    matiere,
    cours,
    mode,
    student_id="",
    learning_style="",
    weaknesses="",
    previous_response="",
    learning_goal="comprendre",
    help_level="equilibre",
    fast_eval=False
):
    mode_instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["expliquer"])

    prompt = build_prompt(
        mem,
        message,
        niveau,
        matiere,
        cours,
        student_id,
        learning_style,
        weaknesses,
        previous_response,
        mode,
        learning_goal,
        help_level
    )

    if fast_eval:
        messages = [
            {"role": "system", "content": BASE_SYSTEM_PROMPT},
            {"role": "system", "content": mode_instruction},
            {"role": "user", "content": prompt}
        ]
        return call_ollama(messages, temp=0.2)

    temps = MODE_TEMPS.get(mode, [0.15, 0.25])
    variants = []

    for t in temps:
        messages = [
            {"role": "system", "content": BASE_SYSTEM_PROMPT},
            {"role": "system", "content": mode_instruction},
            {"role": "user", "content": prompt}
        ]

        ans = call_ollama(messages, temp=t)
        if ans and not answer_is_bad(ans):
            variants.append(ans)

    if not variants:
        return "Erreur de génération."

    best_answer, best_score, _ = choose_best_variant(
        variants, message, niveau, matiere, cours
    )

    mem.setdefault("best_patterns", []).append({
        "mode": mode,
        "score": best_score,
        "length": len(best_answer)
    })
    mem["best_patterns"] = mem["best_patterns"][-50:]

    return best_answer